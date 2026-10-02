import math
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class Commander(Node):
    """Reproduce la rutina 'Animated robot' enviando posiciones a buluk_controller."""

    def __init__(self):
        super().__init__('buluk_commander')
        self.pub = self.create_publisher(Float64MultiArray, '/buluk_controller/commands', 10)
        self.t0 = time.monotonic()
        self.periodo = 3.0                      # 1.5 s ida + 1.5 s regreso
        self.giro = 2 * math.pi / 1.5           # una vuelta cada 1.5 s (rad/s)
        self.create_timer(0.02, self.loop)      # 50 Hz
        self.get_logger().info('Commander iniciado: rutina Animated robot')

    def loop(self):
        t = time.monotonic() - self.t0
        s = 0.5 - 0.5 * math.cos(2 * math.pi * t / self.periodo)   # va suave 0 -> 1 -> 0

        intake = -1.920 * s               # 0° a -110°
        angulator = 1.536 + 0.873 * s     # 88° a 138°
        box = -0.23 * s                   # 0 a -0.23 m
        tambor = self.giro * t            # giro continuo
        roller1 = self.giro * t
        roller2 = -self.giro * t

        msg = Float64MultiArray()
        # Mismo orden que en controllers.yaml
        msg.data = [intake, angulator, tambor, box, roller1, roller2]
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = Commander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()