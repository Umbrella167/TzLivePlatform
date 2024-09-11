# -*- coding: utf-8 -*-

import src.VISION.visionmodule as visions
import threading
from src.SHARE.ShareData import shareData
import time
LOG = False
ACTION_IP = '127.0.0.1'
ACTION_PORT = 20011
ROBOT_ID = 1

def get_debug_data():
    debug = visions.DEBUG(20001)
    while True:
        debug_info=debug.get_info()
        # for msg in debug_info.msgs:
        #     if msg.type == debugs.Debug_Msg.LINE:
        #         lines.append([[msg.line.start.x, -1*msg.line.start.y],[msg.line.end.x, -1*msg.line.end.y],msg.color])
        #         pass
        #     elif msg.type == debugs.Debug_Msg.ARC:
        #         arcs.append([[[msg.arc.rect.point1.x,-1*msg.arc.rect.point1.y],[msg.arc.rect.point2.x,-1*msg.arc.rect.point2.y]],msg.arc.start,msg.arc.span,msg.color])
        #         pass
        #     elif msg.type == debugs.Debug_Msg.TEXT:
        #         texts.append([[msg.text.pos.x, -1*(msg.text.pos.y + 160)],msg.text.text,msg.text.size,msg.color]   )
        #         pass
        # data.debug_line = lines
        # data.debug_arc = arcs
        # data.debug_text = texts

def get_vision_data():
    VISION_PORT = 41001
    vision = visions.VisionModule(VISION_PORT)
    start_time = time.time()
    elapsed_time_last = start_time
    while True:
        if shareData.input.switch_proto_received:
            packge = vision.get_info()
            
            
            
            
            elapsed_time = float(f"{time.time() - start_time:.5f}")
            if (f"{elapsed_time:.2f}" != f"{elapsed_time_last:.2f}"):
                elapsed_time = float(f"{elapsed_time:.2f}")
            shareData.ui.plot_elapsed_time = elapsed_time
            shareData.ui.plot_timeshapes_x.append(elapsed_time)
            shareData.ui.plot_timeshapes_y.append(1)
            shareData.vision.vision_data[elapsed_time] = packge
            elapsed_time_last = elapsed_time
            
            
        # robots_blue = packge.robots_blue
        # robots_yellow = packge.robots_yellow
        # ball = packge.balls
        # data.ball_data["pos"] = [ball.x, ball.y,data.ball_radius]
        # car_live = {}
        # for robot_yellow in robots_yellow:
        #     id_yellow = robot_yellow.robot_id
        #     pos_yellow = [robot_yellow.x, robot_yellow.y]
        #     dir_yellow = -1*robot_yellow.orientation
        #     tag_yellow = f"YELLOW_{id_yellow}"
        #     car_live[tag_yellow] = {
        #         "pos" : pos_yellow,
        #         "dir" : dir_yellow,
        #         "color":"YELLOW"
        #     }
        # for robot_blue in robots_blue:
        #     id_blue = robot_blue.robot_id
        #     pos_blue = [robot_blue.x, robot_blue.y] 
        #     dir_blue = -1*robot_blue.orientation
        #     tag_blue = f"BLUE_{id_blue}"
        #     car_live[tag_blue] = {
        #         "pos" : pos_blue,
        #         "dir" : dir_blue,
        #         "color":"BLUE"
        #     }
        # data.car_data = car_live

def vision_thread():
    vision_thread = threading.Thread(target=get_vision_data,daemon=True)
    vision_thread.start()