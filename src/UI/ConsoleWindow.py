import dearpygui.dearpygui as dpg
from src.SHARE.ShareData import shareData


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
            
    def dragline_callback(self, sender, app_data, user_data):
        if user_data == "DRAG_LINE":
            value = dpg.get_value("time_dragline")
            value = float(f"{value:.2f}")
            shareData.ui.now_tick = value
        if user_data == "MOUSE_DOWN":
            if (dpg.get_item_alias(dpg.get_focused_item()) == "plot" and self.switch_log == True):
                mouse_x,mouse_y = dpg.get_plot_mouse_pos()
                if mouse_x > 0 and mouse_y > 0:
                    dpg.set_value("time_dragline", mouse_x)
                    value = float(f"{mouse_x:.2f}")
                    shareData.ui.now_tick = value
                
    def switch_log_callback(self, sender, app_data, user_data):
        self.switch_log = not self.switch_log
        if self.switch_log:
           dpg.show_item("time_dragline")
        else:
            dpg.hide_item("time_dragline")
            self.play_log = False
            shareData.ui.now_tick = None

            
class ConsoleWindow:
    def __init__(self):
        self._callback = ConsoleCallback()

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
                    label="Time", color=[255, 0, 0, 255], tag="time_dragline",callback=self._callback.dragline_callback,user_data="DRAG_LINE"
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
                    # dpg.add_series
        self.create_console_handler()

            
            
    def create_console_handler(self, tag="console_handler"):
        with dpg.handler_registry():
            # 实时更新进度条
            dpg.add_key_release_handler(
                key=dpg.mvKey_Spacebar, callback=self._callback.console_plot_realtime
            )


            dpg.add_mouse_down_handler(dpg.mvMouseButton_Left, callback=self._callback.dragline_callback,user_data="MOUSE_DOWN")
            # 直播模式

            dpg.add_key_release_handler(
                key=dpg.mvKey_1, callback=self._callback.switch_log_callback
            )
            # 播放log
            dpg.add_key_release_handler(
                key=dpg.mvKey_2, callback=self._callback.play_log_callback
            )
        dpg.bind_item_handler_registry("console_window", "console_handler")

    def update_plot(self, x, y, elapsed_time):
        # fps更新
        dpg.set_value("fps_text", "FPS: " + str(dpg.get_frame_rate()))
        dpg.configure_item(item="time_line", x=x, y=y)

        # 进度条更新
        if self._callback.plot_realtime:
            dpg.fit_axis_data("x_axis")
            # dpg.set_axis_limits("x_axis",elapsed_time-30,elapsed_time)
            # dpg.set_value("time_dragline", elapsed_time)
        else:
            dpg.set_axis_limits_auto("x_axis")

        if not self._callback.switch_log:
            dpg.set_value("time_dragline", elapsed_time)
            
        # log播放
        if self._callback.play_log and self._callback.switch_log:
            self._callback.log_tick += 0.01
            self._callback.log_tick = float(f"{self._callback.log_tick:.2f}")
            print(self._callback.log_tick)
            
            if self._callback.log_tick in shareData.vision.vision_data:
                shareData.ui.now_tick = self._callback.log_tick
                dpg.set_value("time_dragline", self._callback.log_tick)

        