# -*- coding: utf-8 -*-
from src.UI.Ui import ui
import dearpygui.dearpygui as dpg
from src.UI.draw import drawSSL
import src.VISION.visionmodule
def loop():
    ui.update_console()
    drawSSL.draw_all()
    

if __name__ == "__main__":
    dpg.create_context()
    ui.create_viewport()
    ui._theme.set_theme("Dark")
    ui._theme.set_font(20)
    ui.create_show_window()
    
    ui.create_console_window()
    ui.show_ui()
    ui.run_loop(loop)
