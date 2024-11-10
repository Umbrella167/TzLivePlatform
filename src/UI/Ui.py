import dearpygui.dearpygui as dpg
import src.UI.Theme as theme
from src.SHARE.ShareData import shareData
from src.UI.ConsoleWindow import ConsoleWindow
from src.UI.LayoutManager import layoutManager
from src.MESGLOGGER.Logger import log
import src.UTILS.Utils as utils
from src.UI.draw import drawSSL
import math
import copy
def dpg_init():
    dpg.create_context()


class UiData:
    def __init__(self):
        dpg_init()
        self.drawlist_height = 0
        self.drawlist_width = 0
        self.mouse_pos = [0, 0]
        self.mouse_pos_transform = [0, 0]
        self.mouse_pos_last = [0, 0]
        self.mouse_move = [0, 0]
        self.translation = [1920 // 2, 1080 // 2, 0]
        self.translation_matrix = dpg.create_translation_matrix(self.translation)
        self.scale = 1
        self.scale_matrix = dpg.create_scale_matrix([self.scale, self.scale, 1])
        self.transform = self.translation_matrix * self.scale_matrix


class MyComponents:
    def __init__(self, data: UiData):
        pass


class UiCallBack:
    def __init__(self, data: UiData, component: MyComponents):
        self._data = data
        pass

    def mouse_wheel_handler(self, sender, app_data):
        if dpg.get_item_alias(dpg.get_focused_item()) == "main_drawlist":
            step = 0.05
            mouse_x, mouse_y = self._data.mouse_pos
            translation_x, translation_y, _ = self._data.translation
            world_mouse_x = (mouse_x - translation_x) / self._data.scale
            world_mouse_y = (mouse_y - translation_y) / self._data.scale
            # 更新缩放比例
            self._data.scale += step if app_data > 0 else -step
            self._data.scale = max(0.3, self._data.scale)
            self._data.scale = min(3.5, self._data.scale)
            self._data.scale_matrix = dpg.create_scale_matrix(
                [self._data.scale, self._data.scale, 1]
            )
            # 计算新的平移值
            new_translation_x = mouse_x - world_mouse_x * self._data.scale
            new_translation_y = mouse_y - world_mouse_y * self._data.scale
            self._data.translation = [new_translation_x, new_translation_y, 0]
            self._data.translation_matrix = dpg.create_translation_matrix(
                self._data.translation
            )

    def mouse_move_callback(self):

        if dpg.is_mouse_button_down(dpg.mvMouseButton_Middle):
            translation_x, translation_y, _ = self._data.translation
            move_x, move_y = self._data.mouse_move
            new_x, new_y = utils.clamp(
                translation_x + move_x, 0, self._data.drawlist_width
            ), utils.clamp(translation_y + move_y, 0, self._data.drawlist_height)
            self._data.translation = [new_x, new_y, 0]
            self._data.translation_matrix = dpg.create_translation_matrix(
                self._data.translation
            )

    def save_layout(self, sender, app_data, user_data):
        if dpg.is_key_down(dpg.mvKey_Control) and dpg.is_key_down(dpg.mvKey_Control):
            layoutManager.save_layout()
            if shareData.input.switch_proto_received:
                log.save_to_disk()

    def main_drop_callback(self, item, texture):
        dpg.configure_item(item=item, texture_tag=texture)
        shareData.vision.main_ssl_image_width = (
            shareData.vision.vision_ssl_3d_image_width
            if (texture == "ssl_3d_texture")
            else shareData.vision.vision_ssl_2d_image_width
        )
        shareData.vision.main_ssl_image_height = (
            shareData.vision.vision_ssl_3d_image_height
            if (texture == "ssl_3d_texture")
            else shareData.vision.vision_ssl_2d_image_height
        )

    def switch_proto_recived(self, sender, app_data, user_data):
        shareData.input.switch_proto_received = (
            not shareData.input.switch_proto_received
        )

    def config_camera(self, sender, app_data, user_data):
        drawSSL._draw_ssl_3d._camera.config_camera(user_data, app_data)

    def reset_camera(self, sender, app_data, user_data):
        dpg.set_value("fov_sliderfloat", 60.0)
        dpg.set_value("aspect_sliderfloat", 16 / 9)
        dpg.set_value("zoom_sliderfloat", 1.0)
        dpg.set_value("position_sliderdoublex", [0, -2000, 3000])
        dpg.set_value("rotate_sliderdoublex", [math.pi / 5, 0, math.pi * 2])
        dpg.set_value("follow_checkbox", True)
        dpg.set_value("follow_speed_sliderdouble", 0.5)
        dpg.set_value("follow_obj_combo", "Ball")
        drawSSL._draw_ssl_3d._camera.reset()

class UI:
    def __init__(self):
        self._data = UiData()
        self._consoleWindow = ConsoleWindow()
        self._myComponents = MyComponents(self._data)
        self._callBack = UiCallBack(self._data, self._myComponents)
        self._theme = theme
        self._shareData = shareData
        self.darg_item = "ssl_2d_texture"

    def _set_drag_item(self, item):
        self.darg_item = item

    def show_ui(self):
        layoutManager.load_layout()
        dpg.setup_dearpygui()
        dpg.show_viewport()
    
    def run_loop(self, func=None):
        if func is not None:
            while dpg.is_dearpygui_running():
                self.update_drawlist()
                func()
                dpg.render_dearpygui_frame()
        else:
            dpg.start_dearpygui()

    def create_global_handler(self):
        with dpg.handler_registry() as global_hander:
            dpg.add_key_release_handler(
                label="save_layout", callback=self._callBack.save_layout
            )
            dpg.add_key_release_handler(
                label="switch_proto_recived",
                key=dpg.mvKey_Return,
                callback=self._callBack.switch_proto_recived,
            )
            dpg.add_key_release_handler(
                label="switch_proto_recived",
                key=dpg.mvKey_F2,
                callback=self.pop_camera_option_window,
            )
            dpg.add_key_release_handler(
                key=dpg.mvKey_F11, callback=dpg.toggle_viewport_fullscreen
            )
            dpg.add_mouse_wheel_handler(callback=self._callBack.mouse_wheel_handler)
            dpg.add_mouse_move_handler(callback=self._callBack.mouse_move_callback)

    def create_viewport(self, lable: str = "", width: int = 1920, height: int = 1080):
        self.create_global_handler()
        dpg.configure_app(
            docking=True,
            docking_space=True,
            init_file=layoutManager.dpg_window_config,
            load_init_file=True,
        )
        dpg.create_viewport(title=lable, width=width, height=height)
        dpg.set_viewport_vsync(False)
        self.create_viewport_menu()
        self.create_ssl_texture()

    def create_background_window(self):
        with dpg.window(
            label="SSL2D",
            width=1920,
            height=1080,
        ):
            pass

    def create_viewport_menu(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File", tag="file_menu"):
                dpg.add_menu_item(label="Save Layout")
                dpg.add_menu_item(label="Load Layout")
                dpg.add_menu_item(label="Exit")
            with dpg.menu(label="SSL3D", tag="ssl3d_menu"):
                dpg.add_menu_item(
                    label="Camera option  (F2)",
                    tag="camera_option_menutiem",
                    callback=self.pop_camera_option_window,
                )

    def pop_camera_option_window(self):
        follow_obj = ["BALL"] + list(drawSSL.robots_3d.keys())
        follow_obj.sort()
        if dpg.does_alias_exist("camera_option_window"):
            dpg.configure_item("follow_obj_combo", items=follow_obj)
            dpg.show_item("camera_option_window")
            return
        # center_pos = dpg.get_viewport_width() // 2, dpg.get_viewport_height() // 2
        dpg.add_window(
            tag="camera_option_window",
            no_title_bar=True,
            popup=True,
            pos=dpg.get_mouse_pos(),
            min_size=(300, 200),
        )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="FOV: ")
            dpg.add_slider_float(
                min_value=0.0,
                max_value=200.0,
                default_value=60.0,
                callback=self._callBack.config_camera,
                user_data="FOV",
                width=-1,
                tag="fov_sliderfloat",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Aspect: ")
            dpg.add_slider_float(
                min_value=0.005,
                max_value=2,
                default_value=16 / 9,
                callback=self._callBack.config_camera,
                user_data="ASPECT",
                width=-1,
                tag="aspect_sliderfloat",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Zoom: ")
            dpg.add_slider_float(
                min_value=0.05,
                max_value=5,
                default_value=1.0,
                callback=self._callBack.config_camera,
                user_data="ZOOM",
                width=-1,
                tag="zoom_sliderfloat",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Position: ")
            dpg.add_slider_doublex(
                default_value=[0, -2000, 3000],
                size=3,
                min_value=-6000,
                max_value=6000,
                callback=self._callBack.config_camera,
                user_data="POSITION",
                width=-1,
                tag="position_sliderdoublex",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Rotate: ")
            dpg.add_slider_doublex(
                default_value=[math.pi / 5, 0, math.pi * 2],
                size=3,
                min_value=0.0,
                max_value=math.pi * 2,
                callback=self._callBack.config_camera,
                user_data="ROTATE",
                width=-1,
                tag="rotate_sliderdoublex",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Follow: ")
            dpg.add_checkbox(
                default_value=True,
                callback=self._callBack.config_camera,
                user_data="FOLLOW",
                tag="follow_checkbox",
            )
            dpg.add_combo(
                default_value="TPP",
                items=["TPP", "FPP"],
                width=30,
                tag="follow_TYPE_combo",
                callback=self._callBack.config_camera,
                user_data="FOLLOWTYPE",
            )
            dpg.add_combo(
                default_value="Ball",
                items=follow_obj,
                width=-1,
                tag="follow_obj_combo",
                callback=self._callBack.config_camera,
                user_data="FOLLOWOBJ",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_text(default_value="Follow Speed: ")
            dpg.add_slider_double(
                default_value=0.5,
                min_value=0.00001,
                max_value=1.00000,
                callback=self._callBack.config_camera,
                user_data="FOLLOWSPEED",
                width=-1,
                tag="follow_speed_sliderdouble",
            )
        with dpg.group(horizontal=True, parent="camera_option_window"):
            dpg.add_spacer(width=280)
            dpg.add_button(label="Reset", callback=self._callBack.reset_camera)

    def create_console_window(self):
        self._consoleWindow.create_console_window()

    def update_console(self):
        x = self._shareData.ui.plot_timeshapes_x
        y = self._shareData.ui.plot_timeshapes_y
        elapsed_time = self._shareData.time.elapsed_time
        self._consoleWindow.update_console(x, y, elapsed_time)

    def update_main_windw(self):
        # get some value
        shareData.vision.main_ssl_image_width
        image_width = shareData.vision.main_ssl_image_width
        image_height = shareData.vision.main_ssl_image_height
        self._data.mouse_pos = dpg.get_drawing_mouse_pos()
        self._data.mouse_move = [
            self._data.mouse_pos[0] - self._data.mouse_pos_last[0],
            self._data.mouse_pos[1] - self._data.mouse_pos_last[1],
        ]
        width_main, height_main = dpg.get_item_rect_size("main_window")
        self._data.drawlist_width, self._data.drawlist_height = width_main, height_main

        dpg.configure_item(
            item="main_drawlist", width=width_main, height=height_main  - 20
        )
        dpg.delete_item(item="main_side_drawnode", children_only=True)
        
        
        # main side drawnode
        dpg.draw_rectangle(
            pmin=[-image_width // 2, -image_height // 2],
            pmax=[image_width // 2, image_height // 2],
            parent="main_side_drawnode",
        )

        # pygfx image
        dpg.configure_item(
            item="main_drawimage",
            pmin=[-image_width // 2, -image_height // 2],
            pmax=[image_width // 2, image_height // 2],
        )
        # main drawlist
        self._data.transform = self._data.translation_matrix * self._data.scale_matrix
        dpg.apply_transform("main_drawnode", self._data.transform)
        
        # mini map
        shareData.draw.scale_2d = self._data.scale * 0.025
        
        mini_map_translation = copy.copy(self._data.translation)
        
        mini_map_translation[1] = self._data.translation[1] + ((image_height * 0.4) * self._data.scale)
        
        transform_matrix_mini = dpg.create_translation_matrix(mini_map_translation) * dpg.create_scale_matrix([shareData.draw.scale_2d, shareData.draw.scale_2d, 1])
        dpg.apply_transform("mini_map_drawnode",transform_matrix_mini )
        
        self._data.mouse_pos_last = self._data.mouse_pos

    def update_drawlist(self):
        # # 2d
        # self.update_2d_window()
        # # 3d
        # self.update_3d_window()
        # # main
        self.update_main_windw()

    def create_ssl_texture(self):
        # width_2d = shareData.vision.vision_ssl_2d_image_width
        # height_2d = shareData.vision.vision_ssl_2d_image_height
        # with dpg.texture_registry(show=False, tag="ssl_2d_textureregistry"):
        #     dpg.add_raw_texture(
        #         default_value=shareData.vision.vision_ssl_2d_image,
        #         width=height_2d,
        #         height=width_2d,
        #         tag="ssl_2d_texture",
        #         format=dpg.mvFormat_Float_rgba,
        #     )
        width_3d = shareData.vision.vision_ssl_3d_image_width
        height_3d = shareData.vision.vision_ssl_3d_image_height
        with dpg.texture_registry(show=False, tag="ssl_3d_textureregistry"):
            dpg.add_raw_texture(
                default_value=shareData.vision.vision_ssl_3d_image,
                width=width_3d,
                height=height_3d,
                tag="ssl_3d_texture",
                format=dpg.mvFormat_Float_rgba,
            )

    def create_show_window(self):

        with dpg.window(width=1930, height=1080, tag="main_window"):
            with dpg.group(
                drop_callback=lambda: self._callBack.main_drop_callback(
                    "main_drawimage", self.darg_item
                )
            ):
                with dpg.drawlist(width=0, height=0, tag="main_drawlist"):
                    with dpg.draw_node(tag="main_drawnode"):
                        dpg.draw_image(
                            texture_tag="ssl_3d_texture",
                            pmin=[0, 0],
                            pmax=[800, 600],
                            tag="main_drawimage",
                        )
                        with dpg.draw_node(tag="main_side_drawnode"):
                            pass
                    with dpg.draw_node(tag = "mini_map_drawnode"):
                        pass

ui = UI()
