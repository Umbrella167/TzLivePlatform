# -*- coding: utf-8 -*-

import src.VISION.visionmodule as visions
import threading
from src.SHARE.ShareData import shareData
import time
from src.MESGLOGGER.Logger import log
import dearpygui.dearpygui as dpg
LOG = False
ACTION_IP = "127.0.0.1"
ACTION_PORT = 20011
ROBOT_ID = 1


def get_debug_data():
    debug = visions.DEBUG(20001)
    while True:
        debug_info = debug.get_info()
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
    shareData.time.start_time = start_time * 1e9
    y_add = shareData.ui.plot_timeshapes_y[0]
    while True:
        if shareData.input.switch_proto_received:
            packge = vision.get_info()
            time_now = time.time()
            index_time = int(time_now * 1e9)
            log.log(packge, index_time, 10)
            elapsed_time = time_now - start_time
            shareData.time.elapsed_time = elapsed_time
            shareData.ui.plot_timeshapes_x.append(elapsed_time)
            shareData.ui.plot_timeshapes_y.append(y_add)
            shareData.ui.real_msg = packge

def get_event_data():
    event = visions.EVENT()
    area_height = shareData.ui.plot_original_area_height
    while True:
        event_info = event.get_info()
        event_name = event_info.name
        event_type = event_info.type
        event_start_time = (event_info.start_time - shareData.time.start_time) / 1e9
        event_end_time = (event_info.end_time - shareData.time.start_time) / 1e9
        event_color = event_info.color_rgba
        event_color = [1 if x < 1 else x for x in event_color]

        event_tag = event_info.tag
        event_level = abs(event_info.level)
        event_index = event_info.index
        shareData.event.event = {
                "name": event_name,
                "start_time": event_start_time,
                "end_time":event_end_time,
                "type": event_type,
                "tag":event_tag,
                "index":event_index,
                "color_rgba":event_color,
                "level":event_level
            }

        # dpg.add_area_series(
        #     x=[event_start_time, event_start_time, event_end_time, event_end_time],
        #     y=[area_height, area_height * 2, area_height * 2, area_height],
        #     parent="y_axis",
        #     fill=(1, 255, 1, 180),
        # )
        # dpg.add_text_point(label=event_name,parent="y_axis",x=[(event_start_time + event_end_time) / 2], y=[area_height*3.5/2])

def vision_thread():
    vision_thread = threading.Thread(target=get_vision_data, daemon=True)
    event_thread = threading.Thread(target=get_event_data, daemon=True)
    vision_thread.start()
    event_thread.start()
