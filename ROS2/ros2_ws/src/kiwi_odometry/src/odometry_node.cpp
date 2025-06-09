// odometry_node.cpp
#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include <chrono>
#include <cmath>
#include <string>

using namespace std::chrono_literals;

class OdometryPublisher : public rclcpp::Node {
public:
  OdometryPublisher() : Node("kiwi_odometry_node") {
    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 10);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
    timer_ = this->create_wall_timer(50ms, std::bind(&OdometryPublisher::update, this));

    x_ = 0.0;
    y_ = 0.0;
    theta_ = 0.0;
    last_time_ = this->now();
  }

private:
  // Converts 16-bit raw motor speed to degrees per second
  double rawToDegPerSec(int raw_speed) {
    const double steps_per_deg = 4096.0 / 360.0;
    int magnitude = raw_speed & 0x7FFF;
    double degps = static_cast<double>(magnitude) / steps_per_deg;
    if (raw_speed & 0x8000) {
      degps = -degps;
    }
    return degps;
  }

  void update() {
    rclcpp::Time current_time = this->now();
    double dt = (current_time - last_time_).seconds();
    last_time_ = current_time;

    // Dummy raw data to simulate encoder input (replace with actual input)
    int raw_left = 1200;
    int raw_back = -800;
    int raw_right = 1000;

    // Convert raw to rad/s
    double w1 = rawToDegPerSec(raw_left) * (M_PI / 180.0);
    double w2 = rawToDegPerSec(raw_back) * (M_PI / 180.0);
    double w3 = rawToDegPerSec(raw_right) * (M_PI / 180.0);

    const double r = 0.05;   // wheel radius (m)
    const double l = 0.125;  // base radius (m)

    // Compute robot velocity from wheel angular velocities
    double vx = r / 3.0 * (-std::sqrt(3) * w1 + std::sqrt(3) * w3);
    double vy = r / 3.0 * (-w1 + 2 * w2 - w3);
    double omega = r / (3.0 * l) * (w1 + w2 + w3);

    // Integrate to get position
    double delta_x = (vx * std::cos(theta_) - vy * std::sin(theta_)) * dt;
    double delta_y = (vx * std::sin(theta_) + vy * std::cos(theta_)) * dt;
    double delta_theta = omega * dt;

    x_ += delta_x;
    y_ += delta_y;
    theta_ += delta_theta;

    // Publish odometry message
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

    // Broadcast TF transform
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

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Time last_time_;
  double x_, y_, theta_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<OdometryPublisher>());
  rclcpp::shutdown();
  return 0;
}
