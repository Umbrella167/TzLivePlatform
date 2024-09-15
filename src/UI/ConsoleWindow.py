import dearpygui.dearpygui as dpg
from src.SHARE.ShareData import shareData
from src.MESGLOGGER.Logger import logPlayer


class ConsoleCallback:
    def __init__(self):
        self.switch_log = False
        self.plot_realtime = True
        self.play_log = False
        self.log_tick = 0
        pass

    def console_resize_callback(self, sender, app_data, user_data):
        pass

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
                shareData.ui.now_msg = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )
        else:
            now_msg = logPlayer.get_previous_msg()
            if now_msg:
                shareData.ui.now_msg = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )

    def dragline_callback(self, sender, app_data, user_data):
        if user_data == "DRAG_LINE":
            value = dpg.get_value("time_dragline")
            findtime = value * 1e9 + shareData.time.start_time
            shareData.ui.now_msg = logPlayer.read_log_msg(findtime)["message"]
        if user_data == "MOUSE_DOWN":
            if (
                dpg.get_item_alias(dpg.get_focused_item()) == "plot"
                and self.switch_log == True
            ):
                mouse_x, mouse_y = dpg.get_plot_mouse_pos()
                if mouse_x > 0 and mouse_y > 0:
                    dpg.set_value("time_dragline", mouse_x)
                    value = mouse_x
                    findtime = value * 1e9 + shareData.time.start_time
                    shareData.ui.now_msg = logPlayer.read_log_msg(findtime)["message"]

    def switch_log_callback(self, sender, app_data, user_data):
        self.switch_log = not self.switch_log
        if self.switch_log:
            # dpg.show_item("time_dragline")
            pass
        else:
            self.play_log = False
            shareData.ui.now_msg = None


class ConsoleWindow:
    def __init__(self):
        self._callback = ConsoleCallback()
        self.event_area_height = shareData.ui.plot_original_area_height
    def create_console_window(self):
        with dpg.window(label="Console", tag="console_window", width=1920, height=1080):
            dpg.add_text("FPS: ", tag="fps_text")
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
    def level2pos(self,level,event_start_time,event_end_time):
        
        area_height = self.event_area_height
        x = [event_start_time, event_start_time, event_end_time, event_end_time]
        y = [level*area_height,level*area_height + area_height,level*area_height + area_height,level*area_height]
        return x,y
    
    def new_event_block(self,event:dict,parent="y_axis"):
        if event:
            area_height = self.event_area_height
            event_name = event["name"]
            event_type = event["type"]
            event_tag = event["tag"]
            event_start_time = event["start_time"]
            event_end_time = event["end_time"]
            event_color = event["color_rgba"]
            event_index = event["index"]
            event_level = event["level"]
            area_x, area_y = self.level2pos(event_level,event_start_time,event_end_time)
            if dpg.does_alias_exist(event_tag):
                dpg.delete_item(event_tag)
                dpg.delete_item(f"{event_tag}_text")
            event_color = [int(event_color[0]), int(event_color[1]), int(event_color[2]), 255]
            dpg.add_area_series(x=area_x, y=area_y, parent=parent, tag=event_tag, fill=event_color)
            dpg.add_text_point(x=[(event_start_time + event_end_time) / 2],y=[area_height/2 + area_height*event_level],label=event_name,tag=f"{event_tag}_text",parent=parent)



    def create_console_handler(self, tag="console_handler"):
        with dpg.handler_registry():
            # 实时更新进度条
            dpg.add_key_release_handler(
                key=dpg.mvKey_Spacebar, callback=self._callback.console_plot_realtime
            )

            dpg.add_mouse_down_handler(
                dpg.mvMouseButton_Left,
                callback=self._callback.dragline_callback,
                user_data="MOUSE_DOWN",
            )
            # 直播模式

            dpg.add_key_release_handler(
                key=dpg.mvKey_1, callback=self._callback.switch_log_callback
            )
            # 播放log
            dpg.add_key_release_handler(
                key=dpg.mvKey_2, callback=self._callback.play_log_callback
            )

            dpg.add_key_press_handler(
                key=dpg.mvKey_Right,
                callback=self._callback.play_next_tick,
                user_data="RIGHT",
            )
            dpg.add_key_press_handler(
                key=dpg.mvKey_Left,
                callback=self._callback.play_next_tick,
                user_data="LEFT",
            )
        dpg.bind_item_handler_registry("console_window", "console_handler")

    def update_plot(self, x, y, elapsed_time):
        self.new_event_block(shareData.event.event)
        shareData.event.event = {}
        # fps更新
        dpg.set_value("fps_text", "FPS: " + str(dpg.get_frame_rate()))
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
            # dpg.set_axis_limits("x_axis",elapsed_time-30,elapsed_time)
            # dpg.set_value("time_dragline", elapsed_time)
        else:
            dpg.set_axis_limits_auto("x_axis")

        if not self._callback.switch_log:
            shareData.ui.now_msg = shareData.ui.real_msg
            dpg.set_value("time_dragline", elapsed_time)

        # log播放
        if self._callback.play_log and self._callback.switch_log:
            now_msg = logPlayer.get_next_msg()
            if now_msg:
                shareData.ui.now_msg = now_msg["message"]
                dpg.set_value(
                    "time_dragline",
                    (now_msg["timestamp"] - shareData.time.start_time) / 1e9,
                )
