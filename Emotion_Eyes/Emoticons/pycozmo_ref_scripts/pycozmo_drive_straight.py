#This script is based off of the 'go_to_pose.py' script 
#along with the 'path.py' script

from threading import Event

import pycozmo
import sys 

try:
    from PIL import Image
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

SPEED_MMPS = 100.0
ACCEL_MMPS2 = 20.0
DECEL_MMPS2 = 20.0

e = Event()

#on_path_following_event is for the robot to stop after it has completed the path
def on_path_following_event(cli, pkt: pycozmo.protocol_encoder.PathFollowingEvent):
    print(pkt.event_type)
    show_image(robot)
    # if the packet is not a path started event, set the event
    if pkt.event_type != pycozmo.protocol_encoder.PathEventType.PATH_STARTED:
        #set the event
        e.set()

def on_robot_pathing_change(cli, state: bool):
    if state:
        print("Started pathing.")
    else:
        print("Stopped pathing.")
        
def show_image(robot: pycozmo.client, image_path: str):
    #image = Image.open()
    target_size = (128, 32)
    image = Image.open(os.path.join(os.path.dirname(__file__), "assets", image_path))
    resized_image = image.resize(target_size, Image.ANTIALIAS)
    image =  resized_image.convert('1')
    cli.display_image(image)


#connect to the robot
with pycozmo.connect() as cli:
    #add the event handlers
    cli.add_handler(pycozmo.protocol_encoder.PathFollowingEvent, on_path_following_event)
    #add the event handler to the robot pathing change event
    cli.add_handler(pycozmo.event.EvtRobotPathingChange, on_robot_pathing_change)
    
    cli.add_handler(pycozmo.event.EvtRobotPathingChange, on_robot_pathing_change)
    #pkt is for the robot to drive straight
    pkt = pycozmo.protocol_encoder.AppendPathSegLine(
        #from_x and from_y are the starting coordinates
        from_x=0.0, from_y=0.0,
        #to_x and to_y are the ending coordinates
        to_x=200.0, to_y=0.0,
        #speed_mmps is the speed of the robot in millimeters per second
        speed_mmps=SPEED_MMPS, accel_mmps2=ACCEL_MMPS2, decel_mmps2=DECEL_MMPS2)
    #send the packet
    cli.conn.send(pkt)
    #pkt is for the robot to execute the path
    pkt = pycozmo.protocol_encoder.ExecutePath(event_id=1)
    cli.conn.send(pkt)

    e.wait(timeout=30.0)