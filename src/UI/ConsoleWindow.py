import dearpygui.dearpygui as dpg
from src.SHARE.ShareData import shareData
from src.MESGLOGGER.Logger import logPlayer
from src.UTILS.Utils import get_nearest_event
from time import sleep, time

def level2pos(level, event_start_time, event_end_time):

    area_height = shareData.ui.plot_original_area_height
    x = [event_start_time, event_start_time, event_end_time, event_end_time]
    y = [
        level * area_height,
        level * area_height + area_height,
        level * area_height + area_height,
        level * area_height,
    ]
    return x, y


class ConsoleCallback:
    def __init__(self):
        self.switch_log = False
        self.plot_realtime = True
        self.play_log = False
        self.log_tick = 0
        self.play_back_end_time = 0
        self.play_back_switch = False

    def console_plot_realtime(self, sender, app_data, user_data):
        self.plot_realtime = not self.plot_realtime

    def play_log_callback(self, sender, app_data, user_data):
        if self.switch_log == True:
            self.play_log = not self.play_log

            value = dpg.get_value("time_dragline")
            value = float(f"{value:.2f}")

            if self.play_log:
                self.log_tick = value

    def play_next_tick(self, sender, app_data, user_data):
        if self.switch_log == False:
            return
        if user_data == "RIGHT":
            now_msg = logPlayer.get_next_msg()
            if now_msg:
                shareData.ui.now_detection_data = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )
        else:
            now_msg = logPlayer.get_previous_msg()
            if now_msg:
                shareData.ui.now_detection_data = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )

    def dragline_callback(self, sender, app_data, user_data):
        if not shareData.input.switch_proto_received:
            return
        if user_data == "DRAG_LINE":

            try:
                value = dpg.get_value("time_dragline")
                findtime = value * 1e9 + shareData.time.start_time
                shareData.ui.now_detection_data = logPlayer.read_log_msg(findtime)["message"]
            except:
                pass
        if user_data == "MOUSE_DOWN" and not dpg.is_key_down(dpg.mvKey_Control):

            if (
                dpg.get_item_alias(dpg.get_focused_item()) == "plot"
                and self.switch_log == True
            ):
                mouse_x, mouse_y = dpg.get_plot_mouse_pos()
                if mouse_x > 0 and mouse_y > 0:
                    dpg.set_value("time_dragline", mouse_x)
                    value = mouse_x
                    findtime = value * 1e9 + shareData.time.start_time
                    try:
                        shareData.ui.now_detection_data = logPlayer.read_log_msg(findtime)[
                            "message"
                        ]
                    except:
                        pass

    def switch_log_callback(self, sender, app_data, user_data):
        self.switch_log = not self.switch_log
        if self.switch_log:
            # dpg.show_item("time_dragline")
            pass
        else:
            self.play_log = False
            shareData.ui.now_detection_data = None

    def line_adsorption_callback(self, sender, app_data, user_data):
        mouse_x, mouse_y = dpg.get_plot_mouse_pos()

        if user_data == "PRESS":
            # print(mouse_x, mouse_y,dpg.get_focused_item(),dpg.get_mouse_pos())
            if dpg.does_item_exist("select_area"):
                dpg.delete_item("select_area")
            event = get_nearest_event(shareData.event.event_list, mindist=1)
            if event is None:
                return
            pos = event["pos"]
            area = event["area"]

            size = 0.001
            area_x, area_y = area

            dpg.add_area_series(
                x=area_x,
                y=area_y,
                parent="y_axis",
                tag="select_area",
                fill=[255, 255, 255, 180],
            )
            if dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
                print(dpg.get_frame_count())

                start_time = event["start_time"]
                end_time = event["end_time"]
                center_pos_x, _ = event["pos"]
                res = mouse_x
                if mouse_x < start_time:
                    res = start_time
                    dpg.set_value("time_dragline", start_time)

                elif mouse_x > end_time:
                    res = end_time
                    dpg.set_value("time_dragline", end_time)

                else:
                    pass
                    # 移动事件方块
                    # top = area_y[1]
                    # bottom = area_y[0]
                    # new_start_time = (
                    #     mouse_x - (event["end_time"] - event["start_time"]) / 2
                    # )
                    # new_end_time = (
                    #     mouse_x + (event["end_time"] - event["start_time"]) / 2
                    # )
                    # x, y = level2pos(event["level"], new_start_time, new_end_time)
                    # if mouse_y < top and mouse_y > bottom:
                    #     event_tag = event["tag"]
                    #     dpg.configure_item(event["tag"], x=x)
                    #     dpg.configure_item(f"{event_tag}_text", x=[mouse_x])
                    #     event["pos"] = [mouse_x, mouse_y]
                    #     event["area"] = [x, y]
                    #     event["start_time"] = new_start_time
                    #     event["end_time"] = new_end_time
                    #     shareData.event.event_list = [
                    #         event
                    #         for event in shareData.event.event_list
                    #         if event.get("tag") != event_tag
                    #     ]
                    #     shareData.event.event_list.append(event)
                    #     return
                shareData.ui.now_detection_data = logPlayer.read_log_msg(
                    (shareData.time.start_time + res * 1e9)
                )["message"]

        else:
            if dpg.does_item_exist("select_area"):
                dpg.delete_item("select_area")

    def play_back(self, sender, app_data, user_data):
        if not shareData.event.event_list:
            return
        event_list = shareData.event.event_list
        event = event_list[int(dpg.get_value("select_event_combo").split("_")[0])]
        follow_type = dpg.get_value("follow_type_radio")
        follow_mode = dpg.get_value("follow_mode_combo")
        start_time = event["start_time"]
        self.play_back_end_time = event["end_time"]
        
        self.switch_log = True
        dpg.set_value("time_dragline", start_time)
        shareData.ui.now_detection_data = logPlayer.read_log_msg(shareData.time.start_time + start_time * 1e9)["message"]
        
        self.play_back_switch = True
        self.play_log = True
        dpg.hide_item("playback_window")
        


class ConsoleWindow:
    def __init__(self):
        self._callback = ConsoleCallback()
        self.event_area_height = shareData.ui.plot_original_area_height
        self.interpolate_index = 0
    def create_console_window(self):
        with dpg.window(label="Console", tag="console_window", width=1920, height=1080):
            #     with dpg.theme() as slider_theme:
            #         with dpg.theme_component(dpg.mvKnobFloat):
            #             dpg.add_theme_style(dpg.mvStyleVar_FramePadding,100000,-5000)
            #             dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 20)
            with dpg.group(horizontal=True):
                dpg.add_text("FPS: ", tag="fps_text")
                # dpg.add_text("Speed :")
                # dpg.add_knob_float(tag="speed",default_value= 1.0,min_value = 0.0, max_value = 3.0,height= 500)
                # dpg.bind_item_theme("speed",slider_theme)
            with dpg.plot(
                no_menus=True,
                tag="plot",
                width=-1,  # 设置绘图区域的宽度
                height=-1,  # 设置绘图区域的高度
                pan_button=dpg.mvMouseButton_Middle,
                query_button=dpg.mvMouseButton_X1,
                fit_button=dpg.mvMouseButton_Right,
                box_select_button=dpg.mvMouseButton_Right,
                crosshairs=True,
                query=True,
                equal_aspects=True,
            ):
                dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis", no_gridlines=True)

                dpg.add_drag_line(
                    label="Time",
                    color=[255, 0, 0, 255],
                    tag="time_dragline",
                    callback=self._callback.dragline_callback,
                    user_data="DRAG_LINE",
                )
                with dpg.plot_axis(
                    dpg.mvYAxis,
                    no_tick_labels=True,
                    tag="y_axis",
                    lock_min=True,
                    lock_max=True,
                ):
                    dpg.set_axis_limits("y_axis", 0, 30)
                    dpg.add_line_series(x=[0], y=[1], tag="time_line")
                    dpg.add_area_series(
                        x=[0], y=[10], tag="original_area", fill=[255, 50, 100, 190]
                    )

        self.create_console_handler()

    def new_event_block(self, event: dict, parent="y_axis"):
        if event:
            area_height = self.event_area_height
            event_tag = event["tag"]
            event_start_time = event["start_time"]
            event_end_time = event["end_time"]
            event_color = event["color_rgba"]
            event_level = event["level"]
            area_x, area_y = level2pos(event_level, event_start_time, event_end_time)
            if dpg.does_alias_exist(event_tag) or dpg.delete_item(f"{event_tag}_text"):
                dpg.delete_item(event_tag)
                dpg.delete_item(f"{event_tag}_text")
                shareData.event.event_list = [
                    event
                    for event in shareData.event.event_list
                    if event.get("tag") != event_tag
                ]
            event_color = [
                int(event_color[0]),
                int(event_color[1]),
                int(event_color[2]),
                255,
            ]
            print(event_start_time, event_end_time)
            dpg.add_area_series(
                x=area_x, y=area_y, parent=parent, tag=event_tag, fill=event_color
            )
            center_x, center_y = (
                event_start_time + event_end_time
            ) / 2, area_height / 2 + area_height * event_level
            dpg.add_text_point(
                x=[center_x],
                y=[center_y],
                label=event["name"],
                tag=f"{event_tag}_text",
                parent=parent,
            )
            event["pos"] = [center_x, center_y]
            event["area"] = [area_x, area_y]
            event["index"] = len(shareData.event.event_list)
            
            shareData.event.event_list.append(event)
            return event

    def pop_playback_window(self):
        
        event_list = []
        for event in shareData.event.event_list:
            name = event["name"]
            tag = event["tag"]
            index = event["index"]
            start_time = event["start_time"]
            end_time = event["end_time"]
            event_list.append(f"{index}_{name}({start_time:.1f} ~ {end_time:.1f})")

        if dpg.does_alias_exist("playback_window"):
            dpg.configure_item(item="select_event_combo", items=event_list)
            dpg.show_item("playback_window")
            return
        dpg.add_window(
            tag="playback_window",
            no_title_bar=True,
            popup=True,
            pos=dpg.get_mouse_pos(),
            min_size=(300, 200),
        )
        dpg.add_text("Play Back", parent="playback_window")
        with dpg.group(horizontal=True, parent="playback_window"):
            dpg.add_text(default_value="Select Event:")
            dpg.add_combo(items=event_list, width=-1, tag="select_event_combo")

        with dpg.group(parent="playback_window"):
            follow_type = ["TPP", "FPP"]
            follow_mode = ["AUTO", "BALL", "ROBOT", "GOAL"]
            with dpg.child_window(width=-1, height=120):
                dpg.add_text(default_value="Camera Follow Mode:")
                dpg.add_radio_button(
                    items=follow_type, horizontal=True, tag="follow_type_radio"
                )
                dpg.add_combo(
                    items=follow_mode, default_value="AUTO", tag="follow_mode_combo"
                )
        
        with dpg.group(horizontal=True, parent="playback_window"):
            dpg.add_text("Play Speed: ")
            dpg.add_slider_double(default_value=1,max_value=3,min_value=0.1,width=-1,tag = "play_speed_slider")
            
        with dpg.group(horizontal=True, parent="playback_window"):
            dpg.add_spacer(width=200)
            dpg.add_button(
                label="Exit", callback=lambda: dpg.hide_item("playback_window")
            )
            dpg.add_button(
                label="Play",
                callback=self._callback.play_back,
            )
        
    def create_console_handler(self, tag="console_handler"):
        with dpg.handler_registry():
            # 实时更新进度条
            dpg.add_key_release_handler(
                key=dpg.mvKey_Spacebar, callback=self._callback.console_plot_realtime
            )
            # 进度条
            dpg.add_mouse_down_handler(
                dpg.mvMouseButton_Left,
                callback=self._callback.dragline_callback,
                user_data="MOUSE_DOWN",
            )
            # 直播模式
            dpg.add_key_release_handler(
                key=dpg.mvKey_1, callback=self._callback.switch_log_callback
            )
            # 回放设置
            dpg.add_key_release_handler(
                key=dpg.mvKey_F1, callback=self.pop_playback_window
            )
            # 播放log
            dpg.add_key_release_handler(
                key=dpg.mvKey_2, callback=self._callback.play_log_callback
            )
            # 下一帧
            dpg.add_key_press_handler(
                key=dpg.mvKey_Right,
                callback=self._callback.play_next_tick,
                user_data="RIGHT",
            )
            # 上一帧
            dpg.add_key_press_handler(
                key=dpg.mvKey_Left,
                callback=self._callback.play_next_tick,
                user_data="LEFT",
            )
            # CTRL + 鼠标左键 吸附
            dpg.add_key_down_handler(
                key=dpg.mvKey_Control,
                callback=self._callback.line_adsorption_callback,
                user_data="PRESS",
            )
            # CTRL 释放 删除白框（选中框）
            dpg.add_key_release_handler(
                key=dpg.mvKey_Control,
                callback=self._callback.line_adsorption_callback,
                user_data="RELEASE",
            )
        dpg.bind_item_handler_registry("console_window", "console_handler")

    def event_control(self):
        if not shareData.event.event:
            return
        # 新建一个事件块
        event = self.new_event_block(shareData.event.event)
        shareData.event.event = {}
    
    def update_console(self, x, y, elapsed_time):
        if self._callback.play_back_switch and self._callback.play_back_end_time:
            now_time = dpg.get_value("time_dragline")
            if now_time > self._callback.play_back_end_time:
                self._callback.play_back_end_time = 0
                self._callback.play_back_switch = False
                self._callback.play_log = False
                self._callback.switch_log = False
        self.event_control()
        # fps更新
        dpg.set_value("fps_text", "FPS: " + str(int(dpg.get_frame_rate())).zfill(3))
        dpg.configure_item(item="time_line", x=x, y=y)
        area_height = self.event_area_height
        dpg.configure_item(
            item="original_area",
            x=[0, 0, elapsed_time, elapsed_time],
            y=[0, area_height, area_height, 0],
        )

        # 进度条更新
        if self._callback.plot_realtime:
            dpg.fit_axis_data("x_axis")
        else:
            dpg.set_axis_limits_auto("x_axis")

        if not self._callback.switch_log:
            shareData.ui.now_detection_data = shareData.ui.detection_data_real_tiem
            dpg.set_value("time_dragline", elapsed_time)

        # log播放
        if self._callback.play_log and self._callback.switch_log:
            now_msg = logPlayer.get_next_msg()
            if now_msg:
                shareData.ui.now_detection_data = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )
            
