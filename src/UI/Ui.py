import dearpygui.dearpygui as dpg
import src.UI.Theme as theme
import src.VISION.VisionThread as VisionThread
from src.SHARE.ShareData import shareData
from src.UI.ConsoleWindow import ConsoleWindow
from src.UI.LayoutManager import layoutManager


class UiData:
    def __init__(self):
        pass


class MyComponents:
    def __init__(self, data: UiData):
        pass


class UiCallBack:
    def __init__(self, data: UiData, component: MyComponents):
        pass

    def save_layout(self, sender, app_data, user_data):
        if dpg.is_key_down(dpg.mvKey_Control) and dpg.is_key_down(dpg.mvKey_Control):
            layoutManager.save_layout()
    def switch_proto_recived(self,sender,app_data,user_data):
        shareData.input.switch_proto_received = not shareData.input.switch_proto_received
        # print(shareData.input.switch_proto_received)

class UI:
    def __init__(self):
        self._data = UiData()
        self._consoleWindow = ConsoleWindow()
        self._myComponents = MyComponents(self._data)
        self._callBack = UiCallBack(self._data, self._myComponents)
        self._theme = theme
        self._shareData = shareData
    def show_ui(self):
        layoutManager.load_layout()
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def run_loop(self, func=None):
        if func is not None:
            while dpg.is_dearpygui_running():
                self.update_drawlist_size()
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
                label="switch_proto_recived", key=dpg.mvKey_Return,callback=self._callBack.switch_proto_recived
            )
    def create_viewport(self, lable: str = "", width: int = 1920, height: int = 1080):
        self.create_global_handler()
        dpg.configure_app(
            docking=True,
            docking_space=True,
            init_file=layoutManager.dpg_window_config,
            load_init_file=True,
        )
        dpg.create_viewport(title=lable, width=width, height=height)
        self.create_viewport_menu()
        self.create_ssl_2d_texture()
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

    def create_ssl2d_window(self):
        with dpg.window(
            label="SSL2D",
            width=1920,
            height=1080,
            tag = "ssl2d_window"
        ):
            dpg.add_text("SSL2D")
            with dpg.drawlist(width=0, height=0,tag= "ssl_2d_drawlist"):
                with dpg.draw_node(tag="ssl2d_drawnode"):
                    dpg.draw_image(texture_tag="ssl_2d_texture",pmin=[0,0],pmax=[800,600],tag = "ssl_2d_drawimage")
                
    def create_sslar_window(self):
        with dpg.window(label="SSLAR", width=1920, height=1080):
            dpg.add_text("SSLAR")

    def create_ssl3d_window(self):
        with dpg.window(label="SSL3D", width=1920, height=1080):
            dpg.add_text("SSL3D")
    def create_console_window(self):
        self._consoleWindow.create_console_window()
    def update_console(self):
        x = self._shareData.ui.plot_timeshapes_x
        y = self._shareData.ui.plot_timeshapes_y
        elapsed_time = self._shareData.ui.plot_elapsed_time
        self._consoleWindow.update_plot(x,y,elapsed_time)
    def update_drawlist_size(self):
        width,height = dpg.get_item_rect_size( "ssl2d_window")
        dpg.configure_item(item= "ssl_2d_drawlist",width=width,height=height - 50)
        dpg.configure_item(item= "ssl_2d_drawimage",pmin=[0,0],pmax=[width,height])
        
    def create_ssl_2d_texture(self):
        width = shareData.vision.vision_ssl_2d_image_width
        height = shareData.vision.vision_ssl_2d_image_height
        with dpg.texture_registry(show=False):
            dpg.add_raw_texture(default_value=shareData.vision.vision_ssl_2d_image,width=height,height=width,tag="ssl_2d_texture",format=dpg.mvFormat_Float_rgba)
ui = UI()
