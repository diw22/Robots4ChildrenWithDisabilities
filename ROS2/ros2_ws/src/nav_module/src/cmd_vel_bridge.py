#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
import zmq
import json
import numpy as np


class CmdVelBridge(Node):
    def __init__(self):
        super().__init__('cmd_vel_bridge')

        # Create subscription with BEST_EFFORT QoS to match typical robot cmd_vel behavior
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            qos
        )
        
        # ZMQ socket (PUSH to motor controller)
        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.PUSH)
        self.socket.connect("tcp://192.168.137.109:5555")  # Port and IP must match motor side

        self.get_logger().info("cmd_vel_bridge node started and connected to ZMQ motor controller.")

    def cmd_vel_callback(self, msg):
        # Extract velocities from Twist message
        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z

        # Convert body velocity to raw wheel velocities
        wheel_cmds = self.body_to_wheel_raw(vx, vy, omega)

        # Wrap in raw_velocity message
        message = {"raw_velocity": wheel_cmds}

        self.get_logger().debug(f"Received cmd_vel: vx={vx:.2f}, vy={vy:.2f}, omega={omega:.2f}")
        self.get_logger().debug(f"Sending wheel commands: {wheel_cmds}")

        try:
            self.socket.send_string(json.dumps(message), flags=zmq.NOBLOCK)
        except zmq.ZMQError as e:
            self.get_logger().warn(f"Failed to send cmd_vel via ZMQ: {e}")

    def degps_to_raw(self, degps: float) -> int:
        steps_per_deg = 4096.0 / 360.0
        speed_in_steps = abs(degps) * steps_per_deg
        speed_int = int(round(speed_in_steps))
        if speed_int > 0x7FFF:
            speed_int = 0x7FFF
        if degps < 0:
            return speed_int | 0x8000
        else:
            return speed_int & 0x7FFF

    def body_to_wheel_raw(
        self,
        x_cmd: float,
        y_cmd: float,
        theta_cmd: float,
        wheel_radius: float = 0.05,
        base_radius: float = 0.125,
        max_raw: int = 3000,
    ) -> dict:
        """
        Convert desired body-frame velocities into wheel raw commands.

        Parameters:
        x_cmd      : Linear velocity in x (m/s).
        y_cmd      : Linear velocity in y (m/s).
        theta_cmd  : Rotational velocity (deg/s).
        wheel_radius: Radius of each wheel (meters).
        base_radius : Distance from the center of rotation to each wheel (meters).
        max_raw    : Maximum allowed raw command (ticks) per wheel.

        Returns:
        A dictionary with wheel raw commands:
            {"left_wheel": value, "back_wheel": value, "right_wheel": value}.

        Notes:
        - Internally, the method converts theta_cmd to rad/s for the kinematics.
        - The raw command is computed from the wheels angular speed in deg/s
            using degps_to_raw(). If any command exceeds max_raw, all commands
            are scaled down proportionally.
        """
        # Convert rotational velocity from deg/s to rad/s.
        theta_rad = theta_cmd * (np.pi / 180.0)
        # Create the body velocity vector [x, y, theta_rad].
        velocity_vector = np.array([x_cmd, y_cmd, theta_rad])

        # Define the wheel mounting angles (defined from y axis cw)
        angles = np.radians(np.array([300, 180, 60]))
        # Build the kinematic matrix: each row maps body velocities to a wheel’s linear speed.
        # The third column (base_radius) accounts for the effect of rotation.
        m = np.array([[np.cos(a), np.sin(a), base_radius] for a in angles])

        # Compute each wheel’s linear speed (m/s) and then its angular speed (rad/s).
        wheel_linear_speeds = m.dot(velocity_vector)
        wheel_angular_speeds = wheel_linear_speeds / wheel_radius

        # Convert wheel angular speeds from rad/s to deg/s.
        wheel_degps = wheel_angular_speeds * (180.0 / np.pi)

        # Scaling
        steps_per_deg = 4096.0 / 360.0
        raw_floats = [abs(degps) * steps_per_deg for degps in wheel_degps]
        max_raw_computed = max(raw_floats)
        if max_raw_computed > max_raw:
            scale = max_raw / max_raw_computed
            wheel_degps = wheel_degps * scale

        # Convert each wheel’s angular speed (deg/s) to a raw integer.
        wheel_raw = [self.degps_to_raw(deg) for deg in wheel_degps]

        return {"left_wheel": wheel_raw[0], "back_wheel": wheel_raw[1], "right_wheel": wheel_raw[2]}

    def destroy_node(self):
        # Clean up ZMQ socket and context explicitly
        if hasattr(self, "socket"):
            self.socket.close()
        if hasattr(self, "zmq_context"):
            self.zmq_context.term()
        self.get_logger().info("cmd_vel_bridge node shutdown. ZMQ resources cleaned up.")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
