"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: Team7_MiniGrandPrix.py

Title: Final Challenge Code

Team 7

"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(0, "../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Declare any global variables here
MIN_CONTOUR_AREA = 30

BLUE = ((90, 90, 90), (120, 255, 255))
GREEN = ((40, 140, 140), (80, 255, 255)) 
ORANGE = ((10, 140, 140), (25, 255, 255)) 
YELLOW = ((25, 140, 140), (35, 255, 255)) 
PURPLE = ((135, 140, 140), (160, 255, 255))

THRESHOLD = {
    "BLUE": BLUE,
    "GREEN": GREEN,
    "ORANGE": ORANGE,
    "YELLOW": YELLOW,
}

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour
current_color = ""
target_area = 0
counter = 0

########################################################################################
# Functions
########################################################################################

def update_contour():
    global contour_center
    global contour_area
    global current_color

    max_area = 0
    best_contour = None
    best_color = ""

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
        current_color = ""
        return
    
    h = rc.camera.get_height()
    w = rc.camera.get_width()

    crop = int(rc.camera.get_height() // (23 / 10))
    image = rc_utils.crop(image, (crop, 0), (rc.camera.get_height(), rc.camera.get_width()))

    for color_name, (hsv_min, hsv_max) in THRESHOLD.items():
        contours = rc_utils.find_contours(image, hsv_min, hsv_max)
        largest_contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if largest_contour is not None:
            area = rc_utils.get_contour_area(largest_contour)
            if  color_name == "BLUE" or (area > 20000 and color_name == "GREEN") or (area > 15000 and color_name == "YELLOW") or (area > 15000 and color_name == "ORANGE"):
                max_area = area
                best_contour = largest_contour
                best_color = color_name
    
    if best_contour is not None:
        contour_area = max_area
        current_color = best_color
        contour_center = rc_utils.get_contour_center(best_contour)

        rc_utils.draw_contour(image, best_contour)
        rc_utils.draw_circle(image, contour_center)
    else:
        contour_area = 0
        current_color = ""
        contour_center = None

        rc.display.show_color_image(image)

    # Display the image to the screen
    rc.display.show_color_image(image)

# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    global speed
    global angle

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def update():
    global speed
    global angle
    global contour_center
    global target_area 
    global counter

    update_contour()
    rc.drive.set_max_speed(1.0)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)
    
    if contour_center is not None:
        setpoint = rc.camera.get_width() // 2
        error = setpoint - contour_center[1]
    
    if current_color == "BLUE":
            counter = 0
            speed = 0.7
            kp = -0.0046875
            error = setpoint - contour_center[1]
            angle = kp * error
            angle = rc_utils.clamp(angle, -1, 1)
    elif current_color == "ORANGE":
            speed = 0
            angle = 0
            rc.drive.stop()
            counter = 0
    elif current_color == "YELLOW":
            counter += rc.get_delta_time()
            print(counter) 
            target_area = 100000
            speed = rc_utils.clamp((target_area - contour_area) * 0.000098888, -0.35, 0.3)
            setpoint = rc.camera.get_width() // 2
            error = setpoint - contour_center[1]
            angle = rc_utils.clamp((-0.005768 * error) -0.0005, -0.7, 0.6)
            if counter > 14.5:
                    speed = 0.5
                    angle = -0.8
    elif current_color == "GREEN":
        speed = 0.15
        angle = 0.05

    rc.drive.set_speed_angle(speed, angle)


# [FUNCTION] update_slow() is similar to update() but is called once per second by
# default. It is especially useful for printing debug messages, since printing a 
# message every frame in update is computationally expensive and creates clutter
def update_slow():
    # Print a line of ascii text denoting the contour area and x-position
    if rc.camera.get_color_image() is None:
        # If no image is found, print all X's and don't display an image
        print("X" * 10 + " (No image) " + "X" * 10)
    else:
        # If an image is found but no contour is found, print all dashes
        if contour_center is None:
            print("-" * 32 + " : area = " + str(contour_area))

        # Otherwise, print a line of dashes with a | indicating the contour x-position
        else:
            s = ["-"] * 32
            s[int(contour_center[1] / 20)] = "|"
            print("".join(s) + " : area = " + str(contour_area))


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
 