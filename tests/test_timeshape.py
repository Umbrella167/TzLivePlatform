import dearpygui.dearpygui as dpg
import cv2
import time

dpg.create_context()


# 回调函数，用于更新竖直线的位置
def update_vline(sender, app_data):
    mouse_x = dpg.get_plot_mouse_pos()[0]
    # print(mouse_x)
    # print(dpg.get_value("dline1"))
    # dpg.set_value("dline1", mouse_x)
    dpg.configure_item("vline_series", x=[mouse_x])


def set_drag_line():
    mouse_x = dpg.get_plot_mouse_pos()[0]
    dpg.set_value("dline1", mouse_x)


fit = False


# 回调函数，用于更新竖直线的位置
def fit_callback():
    global fit
    fit = not (fit)


x = [0]
y = [50]

with dpg.window(
    label="Main docker window",
    no_scrollbar=True,
    width=800,
    height=800,
    no_collapse=True,
    no_close=True,
    no_focus_on_appearing=True,
    no_bring_to_front_on_focus=True,
    tag="main_window",
):
    with dpg.plot(
        no_menus=True,
        tag="plot",
        width=-1,  # 设置绘图区域的宽度
        height=-1,  # 设置绘图区域的高度
        pan_button=dpg.mvMouseButton_Middle,
        # query_button=dpg.mvMouseButton_Left,
        fit_button=dpg.mvMouseButton_Right,
        box_select_button=dpg.mvMouseButton_Right,
        crosshairs=True,
        query=True,
        equal_aspects=True,
    ):

        x_axis = dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis")
        dpg.add_drag_line(label="dline1", color=[255, 0, 0, 255], tag="dline1")

        dpg.add_plot_legend()
        with dpg.plot_axis(
            dpg.mvYAxis, no_tick_labels=True, tag="y_axis", lock_min=True, lock_max=True
        ):
            # dpg.add_image_series("texture_tag", [0, 0], [10, 10], label="static 1")
            dpg.add_line_series(x=x, y=y, tag="line")
            dpg.set_axis_limits("y_axis", 0, 30)

        # 添加竖直线到 x 轴
        dpg.add_vline_series(
            [0], label="Vertical Line", parent=x_axis, tag="vline_series"
        )
with dpg.window(width=200, height=200, tag="popup", show=False):
    with dpg.drawlist(width=200, height=200):
        with dpg.draw_node(tag="cc"):
            dpg.draw_circle(center=[50, 50], radius=30, color=[255, 0, 0, 255])

# 添加鼠标移动事件处理器到全局处理器注册表
with dpg.handler_registry() as global_handler:
    dpg.add_mouse_move_handler(callback=update_vline)
    dpg.add_key_press_handler(key=dpg.mvKey_Spacebar, callback=fit_callback)
    dpg.add_mouse_double_click_handler(
        button=dpg.mvMouseButton_Left, callback=set_drag_line
    )

dpg.create_viewport(title="Custom Title", width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
start_time = time.time()
dt = 0
while dpg.is_dearpygui_running():
    elapsed_time = time.time() - start_time
    # print(dpg.get_frame_rate(),elapsed_time)
    x.append(elapsed_time)
    y.append(1)
    # if dpg.is_item_hovered("plot"):
    #     x_mouse, y_mouse = dpg.get_mouse_pos()
    #     dpg.show_item("popup")
    #     dpg.set_item_pos("popup", [x_mouse + 30, y_mouse - 200])
    # elif dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
    #     dpg.hide_item("popup")

    if fit:
        dpg.set_axis_limits("x_axis", elapsed_time - 10, elapsed_time)

    else:
        dpg.set_axis_limits_auto("x_axis")
    dpg.configure_item(item="line", x=x, y=y)
    dpg.render_dearpygui_frame()


dpg.destroy_context()
