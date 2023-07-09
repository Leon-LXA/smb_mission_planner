#!/usr/bin/env python
import smach
import rospy
import tf
import smach
import actionlib
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal


class TestMission(smach.State):
    def __init__(self, mission_data, reference_frame):
        smach.State.__init__(
            self, outcomes=['Completed', 'Aborted', 'Next Test'])

        # Get parameters
        # Frames
        self.reference_frame = reference_frame

        self.mission_data = mission_data
        self.test_idx = 0
        self.test_name = ""
        self.next_test = False

        self.update_rate = rospy.Rate(10)
        self.test_pub = rospy.Publisher('/control/keyboard_teleop/cmd_vel', Twist, queue_size=1)
        

    def execute(self, userdata):
        if(self.test_idx >= len(self.mission_data.keys())):
            rospy.loginfo("No more tests left in current mission.")
            self.test_idx = 0
            return 'Completed'

        self.test_name = list(self.mission_data.keys())[
            self.test_idx]
        current_test = self.mission_data[self.test_name]

        self.setTest(
            current_test['lin_vel'], current_test['ang_vel'], current_test['time'])
        rospy.loginfo("Test set: '" + self.test_name + "'.")

        if self.next_test:
            rospy.loginfo("Test '" + self.test_name +
                              "' published. Loading next test...")
            self.test_idx += 1
            return 'Next Test'
        else:
            rospy.logwarn(
                "Can't publish test. Aborting mission...")
            self.test_idx = 0.
            return 'Aborted'

    def setTest(self, lin_vel, ang_vel, time):
        twist_msg = Test()
        twist_msg.linear.x = lin_vel
        twist_msg.angular.z = ang_vel
        endtime = rospy.Time.now() + rospy.Duration(time)

        while rospy.Time.now() < endtime:
            self.twist_pub.publish(twist_msg)
            self.update_rate.sleep()

        self.next_test = True


