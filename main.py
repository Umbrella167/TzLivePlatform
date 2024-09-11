# -*- coding: utf-8 -*-
from src.UI.Ui import ui
import dearpygui.dearpygui as dpg
import src.UI.draw as draw
import src.VISION.VisionThread as vision
draw = draw.DrawSSL2D()
def loop():
    ui.update_console()
    draw.draw_all()

if __name__ == "__main__":
    dpg.create_context()
    vision.vision_thread()
    ui.create_viewport()
    ui._theme.set_theme("Dark")
    ui._theme.set_font(20)
    ui.create_ssl2d_window()
    ui.create_ssl3d_window()
    ui.create_sslar_window()
    ui.create_console_window()
    
    ui.show_ui()
    ui.run_loop(loop)
