#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include <chrono>
#include <cmath>
#include <string>
#include <zmq.hpp>
#include <nlohmann/json.hpp>

using namespace std::chrono_literals;

class OdometryPublisher : public rclcpp::Node {
public:
  OdometryPublisher() : Node("kiwi_odometry_node"), context_(1), socket_(context_, zmq::socket_type::pull) {
    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 10);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
    timer_ = this->create_wall_timer(50ms, std::bind(&OdometryPublisher::update, this));

    x_ = y_ = theta_ = 0.0;
    filtered_vx_ = filtered_vy_ = filtered_omega_ = 0.0;
    last_time_ = this->get_clock()->now();

    std::string ip = "192.168.137.109";
    int port = 5556;
    std::string connection_string = "tcp://" + ip + ":" + std::to_string(port);

    socket_.connect(connection_string);
    int conflate = 1;
    socket_.set(zmq::sockopt::conflate, conflate);
  }

private:
  zmq::context_t context_;
  zmq::socket_t socket_;
  int raw_left_ = 0;
  int raw_right_ = 0;
  int raw_back_ = 0;

  double x_, y_, theta_;
  double filtered_vx_, filtered_vy_, filtered_omega_;
  rclcpp::Time last_time_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::TimerBase::SharedPtr timer_;

  // Converts raw motor speed (16-bit encoded) to degrees per second
  double rawToDegPerSec(int raw_speed) {
    const double steps_per_deg = 4096.0 / 360.0;
    int magnitude = raw_speed & 0x7FFF;
    double degps = static_cast<double>(magnitude) / steps_per_deg;
    if (raw_speed & 0x8000) degps = -degps;
    return degps;
  }

  void update() {
    zmq::message_t message;
    try {
      auto result = socket_.recv(message, zmq::recv_flags::dontwait);
      if (result.has_value()) {
        std::string msg_str(static_cast<char*>(message.data()), message.size());
        auto json_msg = nlohmann::json::parse(msg_str);

        raw_left_ = json_msg.at("left_wheel").get<int>();
        raw_back_ = json_msg.at("back_wheel").get<int>();
        raw_right_ = json_msg.at("right_wheel").get<int>();

        RCLCPP_INFO(this->get_logger(), "[ZMQ] Received message: left=%d, right=%d, back=%d", raw_left_, raw_right_, raw_back_);
      } else {
        RCLCPP_INFO(this->get_logger(), "[ZMQ] No message received.");
      }
    } catch (const zmq::error_t& e) {
      RCLCPP_WARN(this->get_logger(), "ZMQ error: %s", e.what());
    } catch (const std::exception& e) {
      RCLCPP_WARN(this->get_logger(), "JSON parse error: %s", e.what());
    }

    rclcpp::Time current_time = this->get_clock()->now();
    double dt = (current_time - last_time_).seconds();

    // Skip update if dt is too large to avoid odometry jump
    if (dt > 1.0) {
      RCLCPP_WARN(this->get_logger(), "Large dt (%.3f s), skipping update to avoid odometry error.", dt);
      last_time_ = current_time;
      return;
    }

    last_time_ = current_time;

    // Convert raw motor data to angular velocity (rad/s)
    double w1 = -rawToDegPerSec(raw_left_) * (M_PI / 180.0);
    double w2 = rawToDegPerSec(raw_back_) * (M_PI / 180.0);
    double w3 = -rawToDegPerSec(raw_right_) * (M_PI / 180.0);

    // Wheel and robot geometry
    const double r = 0.05;
    const double l = 0.125;
    const double omega_gain = 3.0;

    double vx = r / 3.0 * (-std::sqrt(3) * w1 + std::sqrt(3) * w3);
    double vy = r / 3.0 * (-w1 + 2 * w2 - w3);
    vy *= 0.8;
    double omega = omega_gain * r / (3.0 * l) * (w1 + w2 + w3);

    // Optional: invert directions to align with mapping orientation
    vx = -vx;
    vy = -vy;
    omega = -omega;

    // Apply exponential moving average filter
    const double alpha = 0.5;
    filtered_vx_ = alpha * vx + (1 - alpha) * filtered_vx_;
    filtered_vy_ = alpha * vy + (1 - alpha) * filtered_vy_;
    filtered_omega_ = alpha * omega + (1 - alpha) * filtered_omega_;

    double delta_x = (filtered_vx_ * std::cos(theta_) - filtered_vy_ * std::sin(theta_)) * dt;
    double delta_y = (filtered_vx_ * std::sin(theta_) + filtered_vy_ * std::cos(theta_)) * dt;
    double delta_theta = filtered_omega_ * dt;

    x_ += delta_x;
    y_ += delta_y;
    theta_ += delta_theta;

    RCLCPP_INFO(this->get_logger(), "POSE | x: %.3f, y: %.3f, theta: %.3f", x_, y_, theta_);

    auto odom = nav_msgs::msg::Odometry();
    odom.header.stamp = current_time;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_link";

    odom.pose.pose.position.x = x_;
    odom.pose.pose.position.y = y_;
    odom.pose.pose.position.z = 0.0;
    odom.pose.pose.orientation.z = std::sin(theta_ / 2.0);
    odom.pose.pose.orientation.w = std::cos(theta_ / 2.0);

    odom.twist.twist.linear.x = filtered_vx_;
    odom.twist.twist.linear.y = filtered_vy_;
    odom.twist.twist.angular.z = filtered_omega_;

    odom_pub_->publish(odom);

    geometry_msgs::msg::TransformStamped tf_msg;
    tf_msg.header.stamp = current_time;
    tf_msg.header.frame_id = "odom";
    tf_msg.child_frame_id = "base_link";
    tf_msg.transform.translation.x = x_;
    tf_msg.transform.translation.y = y_;
    tf_msg.transform.translation.z = 0.0;
    tf_msg.transform.rotation.z = std::sin(theta_ / 2.0);
    tf_msg.transform.rotation.w = std::cos(theta_ / 2.0);

    tf_broadcaster_->sendTransform(tf_msg);
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<OdometryPublisher>());
  rclcpp::shutdown();
  return 0;
}
