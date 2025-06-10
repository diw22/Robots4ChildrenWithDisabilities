#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

using NavigateToPose = nav2_msgs::action::NavigateToPose;
using GoalHandleNavigateToPose = rclcpp_action::ClientGoalHandle<NavigateToPose>;

class NavigatorNode : public rclcpp::Node {
public:
  NavigatorNode() : Node("navigator_node") {
    // Create action client for the NavigateToPose action server
    client_ptr_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");

    // Subscribe to /goal_pose topic (e.g. from RViz) to receive target goal
    goal_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
      "/goal_pose", 10,
      std::bind(&NavigatorNode::goal_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "NavigatorNode is ready and waiting for /goal_pose...");
  }

private:
  // Action client to interact with nav2 NavigateToPose action
  rclcpp_action::Client<NavigateToPose>::SharedPtr client_ptr_;

  // Subscriber for goal pose topic
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr goal_sub_;

  // Callback function called when a new goal is received
  void goal_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
    // Wait for the action server to be ready
    if (!client_ptr_->wait_for_action_server(std::chrono::seconds(2))) {
      RCLCPP_WARN(this->get_logger(), "Action server not available.");
      return;
    }

    // Create a goal message using the received pose
    auto goal_msg = NavigateToPose::Goal();
    goal_msg.pose = *msg;

    RCLCPP_INFO(this->get_logger(), "Sending navigation goal to (%.2f, %.2f)",
                goal_msg.pose.pose.position.x, goal_msg.pose.pose.position.y);

    // Define goal options including feedback and result callbacks
    auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
    send_goal_options.feedback_callback =
      std::bind(&NavigatorNode::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);

    send_goal_options.result_callback =
      std::bind(&NavigatorNode::result_callback, this, std::placeholders::_1);

    // Send the goal asynchronously
    client_ptr_->async_send_goal(goal_msg, send_goal_options);
  }

  // Feedback callback provides updates on progress toward the goal
  void feedback_callback(
    GoalHandleNavigateToPose::SharedPtr,
    const std::shared_ptr<const NavigateToPose::Feedback> feedback)
  {
    RCLCPP_INFO(this->get_logger(),
      "Feedback: Distance remaining = %.2f",
      feedback->distance_remaining);
  }

  // Result callback called when navigation finishes (success, canceled, or aborted)
  void result_callback(const GoalHandleNavigateToPose::WrappedResult & result) {
    switch (result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        RCLCPP_INFO(this->get_logger(), "Goal reached successfully.");
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_WARN(this->get_logger(), "Goal was aborted.");
        break;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_INFO(this->get_logger(), "Goal was canceled.");
        break;
      default:
        RCLCPP_ERROR(this->get_logger(), "Unknown result code.");
        break;
    }
  }
};

int main(int argc, char **argv) {
  // Initialize ROS 2 and spin the node
  rclcpp::init(argc, argv);
  auto node = std::make_shared<NavigatorNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
