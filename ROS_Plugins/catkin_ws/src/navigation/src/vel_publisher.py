#!/usr/bin/python3

import rospy
from geometry_msgs.msg import Twist, Vector3
from navigation.msg import img_result
import math 

X_SHIFT_EPSILON = rospy.get_param("navigation/x_shift_epsilon") # error tolerance for x_shift
RATE = rospy.get_param("navigation/rate")
FORWARD_VELOCITY = rospy.get_param("navigation/forward_vel")
SPIN_VELOCITY = rospy.get_param("navigation/spin_vel")
VERBOSE = rospy.get_param("navigation/verbose")

class VelocityPublisher:
    # reads the image processing results and publishes the velocity commands

    def __init__(self, rate, verbose):
        rospy.init_node('vel_publisher', anonymous = True)
        rospy.loginfo("VelocityPublisher initialized")
        # we don't need queues since we only care about the most recent data
        self.pub = rospy.Publisher('/husky_model/husky/cmd_vel', Twist, queue_size=1)
        self.sub = rospy.Subscriber("/img_result", img_result, self.callback, queue_size=1)
        self.rate = rospy.Rate(rate)
        self.verbose = verbose 
        rospy.loginfo("Running...")

    def publish(self, message):
        self.pub.publish(message)
        if self.verbose:
            rospy.loginfo(message)
        self.rate.sleep()   

    def callback(self, shift):
        velocity = self.get_velocity(shift)
        self.publish(velocity)

    def get_velocity(self, data):
        red_detected = data.red
        shift = data.shift

        if red_detected == 'no': # no red light found
            return Twist(Vector3(0, 0, 0), Vector3(0, 0, SPIN_VELOCITY)) # turn left
        
        if self.verbose:
            rospy.loginfo(f"shift: {shift}")

        if abs(shift) < X_SHIFT_EPSILON:
            return Twist(Vector3(FORWARD_VELOCITY, 0, 0), Vector3(0, 0, 0)) # move forward
        
        if shift > 0:
            vel = -math.log(shift, 10) # log function to slow down as we get closer to the center
            return Twist(Vector3(0, 0, 0), Vector3(0, 0, vel)) # turn right
        
        if shift < 0:
            vel = math.log(-shift, 10) # log function to slow down as we get closer to the center
            return Twist(Vector3(0, 0, 0), Vector3(0, 0, vel)) # turn left
        

def process(rate, verbose):
    vp = VelocityPublisher(rate, verbose)
    rospy.spin()

if __name__ == '__main__':
    process(rate = RATE, verbose = VERBOSE) # rate chosen to match the camera's frame rate