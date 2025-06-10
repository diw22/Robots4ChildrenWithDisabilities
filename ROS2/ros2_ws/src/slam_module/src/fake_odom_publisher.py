import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion, TransformStamped
from tf2_ros import TransformBroadcaster
import time

class FakeOdomPublisher(Node):
    def __init__(self):
        super().__init__('fake_odom_publisher')
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.x = 0.0
        self.v = 0.05  # 5cm/s
        self.start_time = time.time()

        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        now = self.get_clock().now().to_msg()
        elapsed = time.time() - self.start_time
        self.x = self.v * elapsed

        # Quaternion: no rotation
        q = Quaternion()
        q.w = 1.0

        # Publish odometry
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.orientation = q
        odom.twist.twist.linear.x = self.v
        self.odom_pub.publish(odom)

        # Publish TF transform
        tf = TransformStamped()
        tf.header.stamp = now
        tf.header.frame_id = 'odom'
        tf.child_frame_id = 'base_link'
        tf.transform.translation.x = self.x
        tf.transform.rotation = q
        self.tf_broadcaster.sendTransform(tf)

def main(args=None):
    rclpy.init(args=args)
    node = FakeOdomPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
