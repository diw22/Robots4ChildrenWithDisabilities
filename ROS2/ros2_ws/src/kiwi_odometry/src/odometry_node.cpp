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
    last_time_ = this->now();

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
  rclcpp::Time last_time_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::TimerBase::SharedPtr timer_;

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

        RCLCPP_INFO(this->get_logger(), "\n[ZMQ] Received message: left=%d, right=%d, back=%d", raw_left_, raw_right_, raw_back_);
      }else {
        RCLCPP_INFO(this->get_logger(), "\n[ZMQ] No message received.");
      }
    } catch (const zmq::error_t& e) {
      RCLCPP_WARN(this->get_logger(), "ZMQ error: %s", e.what());
    } catch (const std::exception& e) {
      RCLCPP_WARN(this->get_logger(), "JSON parse error: %s", e.what());
    }

    rclcpp::Time current_time = this->now();
    double dt = (current_time - last_time_).seconds();
    last_time_ = current_time;

    double w1 = rawToDegPerSec(raw_left_) * (M_PI / 180.0);
    double w2 = rawToDegPerSec(raw_back_) * (M_PI / 180.0);
    double w3 = rawToDegPerSec(raw_right_) * (M_PI / 180.0);

    const double r = 0.05;
    const double l = 0.125;

    double vx = r / 3.0 * (-std::sqrt(3) * w1 + std::sqrt(3) * w3);
    double vy = r / 3.0 * (-w1 + 2 * w2 - w3);
    double omega = r / (3.0 * l) * (w1 + w2 + w3);

    double delta_x = (vx * std::cos(theta_) - vy * std::sin(theta_)) * dt;
    double delta_y = (vx * std::sin(theta_) + vy * std::cos(theta_)) * dt;
    double delta_theta = omega * dt;

    x_ += delta_x;
    y_ += delta_y;
    theta_ += delta_theta;

    auto odom = nav_msgs::msg::Odometry();
    odom.header.stamp = current_time;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_link";

    odom.pose.pose.position.x = x_;
    odom.pose.pose.position.y = y_;
    odom.pose.pose.position.z = 0.0;
    odom.pose.pose.orientation.z = std::sin(theta_ / 2.0);
    odom.pose.pose.orientation.w = std::cos(theta_ / 2.0);

    odom.twist.twist.linear.x = vx;
    odom.twist.twist.linear.y = vy;
    odom.twist.twist.angular.z = omega;

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
