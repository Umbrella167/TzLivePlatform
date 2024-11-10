import math
import src.UTILS.Utils as utils
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QBrush, QPolygon, QFont
from PyQt6.QtCore import QPoint, QRect
import numpy as np
import pygfx as gfx
from src.SHARE.ShareData import shareData
import dearpygui.dearpygui as dpg
import pylinalg as la
import imageio.v3 as iio
from wgpu.gui.offscreen import WgpuCanvas


class Draw2DQT:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background_color = QColor(50, 50, 50, 1)
        self.image = QImage(width, height, QImage.Format.Format_RGB32)
        self.image.fill(self.background_color)
        self.painter = QPainter(self.image)
        self.color_transform = [
            [255, 255, 255, 255],
            [255, 0, 0, 255],
            [255, 165, 0, 255],
            [255, 255, 0, 255],
            [0, 255, 0, 255],
            [0, 255, 255, 255],
            [0, 0, 255, 255],
            [160, 32, 240, 255],
            [128, 128, 128, 255],
            [0, 0, 0, 255],
        ]

    def translate(self, dx, dy):
        self.painter.translate(dx, dy)

    def scale(self, sx, sy):
        self.painter.scale(sx, sy)

    def draw_line(self, start, end, color, width: int):
        start = QPoint(int(start[0]), int(start[1]))
        end = QPoint(int(end[0]), int(end[1]))
        pen = QPen(QColor(color[0], color[1], color[2], color[3]), width)
        self.painter.setPen(pen)
        self.painter.drawLine(start, end)

    def draw_arc(self, rect_points, start_angle, span_angle, color, width: int):
        top_left = QPoint(int(rect_points[0][0]), int(rect_points[0][1]))
        bottom_right = QPoint(int(rect_points[1][0]), int(rect_points[1][1]))
        rect = QRect(top_left, bottom_right)
        pen = QPen(QColor(color[0], color[1], color[2], color[3]), width)
        self.painter.setPen(pen)
        start_angle_16 = int(start_angle * 16)
        span_angle_16 = int(span_angle * 16)
        self.painter.drawArc(rect, start_angle_16, span_angle_16)

    def draw_rect(self, rect_points, color, width: int):
        top_left = QPoint(int(rect_points[0][0]), int(rect_points[0][1]))
        bottom_right = QPoint(int(rect_points[1][0]), int(rect_points[1][1]))
        rect = QRect(top_left, bottom_right)
        pen = QPen(QColor(color[0], color[1], color[2], color[3]), width)
        self.painter.setPen(pen)
        self.painter.drawRect(rect)

    def draw_text(self, pos, text, size, color):
        font = QFont()
        font.setPointSize(int(size))
        self.painter.setFont(font)
        pen = QPen(QColor(color[0], color[1], color[2], color[3]))
        self.painter.setPen(pen)
        position = QPoint(int(pos[0]), int(pos[1]))
        self.painter.drawText(position, text)

    def draw_polygon(self, points, color, width: int, fill=True):
        polygon = QPolygon([QPoint(int(point[0]), int(point[1])) for point in points])
        pen = QPen(QColor(color[0], color[1], color[2], color[3]), width)
        self.painter.setPen(pen)
        if fill:
            brush = QBrush(QColor(color[0], color[1], color[2], color[3]))
            self.painter.setBrush(brush)
            self.painter.drawPolygon(polygon)
        else:
            self.painter.drawPolygon(polygon)

    def draw_filled_circle(self, center, radius, color):
        center = QPoint(int(center[0]), int(center[1]))
        brush = QBrush(QColor(color[0], color[1], color[2], color[3]))
        self.painter.setBrush(brush)
        self.painter.setPen(QPen(QColor(color[0], color[1], color[2], color[3])))
        self.painter.drawEllipse(center, int(radius), int(radius))

    def to_image(self):
        ptr = self.image.constBits()
        ptr.setsize(self.image.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape(self.height, self.width, 4)
        arr = arr[:, :, [2, 1, 0, 3]]
        return arr

    def to_dpg_texture(self):
        arr = self.to_image()
        texture = arr.ravel().astype("float32") / 255.0
        return texture

    def to_gfx_texture(self):
        arr = self.to_image()
        texture = gfx.Texture(arr, dim=2)
        return texture

    def draw_start(self, init=False):
        self.clear()
        canvas_size = (12000, 9000)
        if not init:
            self.painter = QPainter(self.image)
            canvas_size = (9500, 6500)
        self.painter.translate(self.width / 2, self.height / 2)
        scale_width = self.width / canvas_size[0]
        scale_height = self.height / canvas_size[1]
        self.painter.scale(scale_width, scale_height)

    def draw_end(self):
        self.painter.end()

    def clear(self):

        self.image.fill(self.background_color)


class DrawSSL2DQT:

    def __init__(
        self,
        width=shareData.vision.vision_ssl_2d_image_width,
        height=shareData.vision.vision_ssl_2d_image_height,
    ):

        self._draw2D = Draw2DQT(height, width)

    def draw_robot(self, pos, radius, dir, color):
        angle = dir * (180 / math.pi)
        start_angle = 45 + angle
        end_angle = 315 + angle
        # 将角度转换为弧度
        start_radians = np.radians(start_angle)
        end_radians = np.radians(end_angle)
        # 计算每个分段的角度，减少分段数量
        angles = np.linspace(start_radians, end_radians, 30)
        # 计算弧线上的点
        x = pos[0] + radius * np.cos(angles)
        y = pos[1] - radius * np.sin(angles)
        # 直接使用NumPy数组，假设draw_polygon可以接受NumPy数组
        points = np.column_stack((x, y))
        self._draw2D.draw_polygon(points, color, 10)

    def draw_field(self):
        color = [255, 255, 255, 200]
        P1 = [-4500, 3000]
        P2 = [4500, 3000]
        P3 = [4500, -3000]
        P4 = [-4500, -3000]
        width = 10
        self._draw2D.draw_line(P1, P2, color, width)
        self._draw2D.draw_line(P2, P3, color, width)
        self._draw2D.draw_line(P3, P4, color, width)
        self._draw2D.draw_line(P4, P1, color, width)
        self._draw2D.draw_line(
            utils.middle_pos(P1, P4), utils.middle_pos(P2, P3), color, width
        )
        self._draw2D.draw_line(
            utils.middle_pos(P1, P2), utils.middle_pos(P3, P4), color, width
        )
        self._draw2D.draw_arc([[-500, 500], [500, -500]], 0, 360, color, width)
        self._draw2D.draw_rect([[-4500, 1000], [-3500, -1000]], color, width)
        self._draw2D.draw_rect([[3500, 1000], [4500, -1000]], color, width)

        self._draw2D.draw_rect([[-4700, 500], [-4500, -500]], color, width)
        self._draw2D.draw_rect([[4500, 500], [4700, -500]], color, width)

    def draw_ball(self, pos, radius):
        color = [255, 165, 0, 255]
        self._draw2D.draw_filled_circle(pos, radius, color)


class Draw2DDPG:
    def __init__(self, width, height, draw_node):
        self.width = width
        self.height = height
        self.parent = draw_node
        self.ball_radius = shareData.draw.ball_radius

    def draw_ball(self, pos):
        pos = pos
        color = [255, 165, 0, 255]
        dpg.draw_circle(
            center=pos,
            radius=self.ball_radius * shareData.draw.scale_2d,
            parent=self.parent,
            color=color,
            thickness=3 * shareData.draw.scale_2d,
            fill=color,
        )

    def draw_robot(self, pos, radius, dir, color, id):
        pos = [pos[0], pos[1]]
        angle = dir * (180 / math.pi)
        start_angle = 45 + angle
        end_angle = 315 + angle
        # 将角度转换为弧度
        start_radians = np.radians(start_angle)
        end_radians = np.radians(end_angle)
        # 计算每个分段的角度
        angles = np.linspace(start_radians, end_radians, 30 + 1)
        # 计算弧线上的点
        x = pos[0] + radius * np.cos(angles)
        y = pos[1] - radius * np.sin(angles)
        # 将点转换为列表格式
        points = np.column_stack((x, y)).tolist()
        with dpg.draw_node(parent=self.parent):
            dpg.draw_polygon(
                points, color=color, fill=color, thickness=2 * shareData.draw.scale_2d
            )
            # dpg.draw_text(
            #     text=id,
            #     pos=np.array(pos) + (np.array([-147, -220])),
            #     size=200 * shareData.draw.scale_2d,
            # )

    def draw_field(self):
        color = [255, 255, 255, 150]
        thickness = 13 * shareData.draw.scale_2d
        x, y = self.width * 10, self.height * 10
        x = x / 2
        y = y / 2
        dpg.draw_rectangle(
            pmax=[-x, y],
            pmin=[x, -y],
            parent=self.parent,
            color=color,
            thickness=thickness,
            fill=[50, 50, 50, 50],
        )
        dpg.draw_line(
            p1=[0, y], p2=[0, -y], parent=self.parent, color=color, thickness=thickness
        )
        dpg.draw_line(
            p1=[x, 0], p2=[-x, 0], parent=self.parent, color=color, thickness=thickness
        )
        dpg.draw_circle(
            center=[0, 0],
            radius=500 * shareData.draw.scale_2d,
            parent=self.parent,
            color=color,
            thickness=thickness,
        )
        if x == 4500:
            dpg.draw_rectangle(
                pmax=[-4500, 1000],
                pmin=[-3500, -1000],
                parent=self.parent,
                color=color,
                thickness=thickness,
            )
            dpg.draw_rectangle(
                pmax=[3500, 1000],
                pmin=[4500, -1000],
                parent=self.parent,
                color=color,
                thickness=thickness,
            )

    def draw_line(self, lines):
        for line in lines:
            dpg.draw_line(
                p1=line[0],
                p2=line[1],
                color=self.color_transform[line[2]],
                parent=self.parent,
            )

    def draw_text(self, debug_texts):
        for text in debug_texts:
            dpg.draw_text(
                pos=text[0],
                text=text[1],
                size=text[2] * shareData.draw.scale_2d * 1.5,
                color=self.color_transform[text[3]],
            )

    def draw_arc(self, arcs):
        for arc in arcs:
            # print(arc)
            posx, posy = utils.middle_pos(arc[0], arc[1])
            pos = [posx, -1 * posy]
            radius = (
                utils.calculate_distance(
                    [arc[0][0], -1 * arc[0][1]], [arc[1][0], -1 * arc[0][1]]
                )
                / 2
            )
            start_angle = arc[2]
            end_angle = arc[3]
            color = arc[4]
            # 将角度转换为弧度
            start_radians = np.radians(start_angle)
            end_radians = np.radians(end_angle)
            # 计算每个分段的角度
            angles = np.linspace(start_radians, end_radians, 40)
            # 计算弧线上的点
            x = pos[0] + radius * np.cos(angles)
            y = pos[1] - radius * np.sin(angles)
            # 将点转换为列表格式
            points = np.column_stack((x, y)).tolist()
            dpg.draw_polygon(
                points,
                color=self.color_transform[color],
                thickness=1 * self.scale,
            )


class DrawSSL3D:
    def __init__(self, width, height) -> None:
        self._world = self.World()
        self._camera = self.Camera()
        self._ball = self.BALL(self._world.scene)
        self.width = width / shareData.vision.pixel_ratio
        self.height = height / shareData.vision.pixel_ratio
        self.canvas = WgpuCanvas(
            size=(self.width, self.height),
            pixel_ratio=shareData.vision.pixel_ratio,
            max_fps=888,
        )
        self.robots = {}
        self.renderer = gfx.renderers.WgpuRenderer(self.canvas)

    class BALL:
        def __init__(self, scene):
            self.scene = scene
            self.ball = gfx.Mesh(
                gfx.sphere_geometry(43, 43, 43),
                gfx.MeshPhongMaterial(color=(1, 0.647, 0, 1), flat_shading=True),
            )
            self.scene.add(self.ball)
            self.ball.local.position = [0, 0, shareData.draw.ball_radius]

        def set_ball_position(self, pos):
            self.ball.local.position = pos

        def add_ball_position(
            self, pos, rate, threshold=shareData.draw.add_threshold_pos
        ):
            current_position = np.array(self.ball.local.position)
            pos = np.array(pos)

            # 计算当前位置与目标位置的差异
            difference = np.linalg.norm(current_position - pos)

            if difference > threshold:
                # 在当前位置和目标位置之间进行插值
                pos = current_position + (pos - current_position) * rate

            # 更新机器人的位置
            self.ball.local.position = pos

    class ROBOT:
        def __init__(self, scene):
            self.scene = scene
            self.robot = None
            self.robot_name = None

        def create(self):
            self.robot = gfx.Group(visible=True)
            self.robot_body = gfx.Mesh(
                gfx.box_geometry(130, 130, 130),
                gfx.MeshPhongMaterial(color=(0, 0, 1, 1), flat_shading=True),
            )
            self.robot_eye = gfx.Mesh(
                gfx.box_geometry(10, 120, 50),
                gfx.MeshPhongMaterial(color=(0, 0, 1, 1), flat_shading=True),
            )

            self.robot_name = gfx.Text(
                gfx.TextGeometry(
                    markdown=" Hello",
                    screen_space=True,
                    font_size=15,
                    anchor="bottomleft",
                ),
                gfx.TextMaterial(color="#0f4"),
            )
            self.robot_name.local.position = (0, 0, 100)

            self.robot_eye.local.position = [70, 0, 50]
            self.robot.add(self.robot_body, self.robot_eye, self.robot_name)
            self.scene.add(self.robot)

        def add_position(self, pos, rate, threshold=shareData.draw.add_threshold_pos):

            current_position = np.array(self.robot.local.position)
            pos = np.array(pos)

            # 计算当前位置与目标位置的差异
            difference = np.linalg.norm(current_position - pos)

            if difference > threshold:
                # 在当前位置和目标位置之间进行插值
                pos = current_position + (pos - current_position) * rate

            # 更新机器人的位置
            self.robot.local.position = pos

        def add_rotation(self, dir, rate, threshold=shareData.draw.add_threshold_dir):
            dir_robot = la.quat_to_euler(self.robot.local.rotation)
            error = -dir - dir_robot[2]
            error = (error + np.pi) % (2 * np.pi) - np.pi
            threshold = threshold * (np.pi / 180)
            if np.abs(error) < threshold:
                rate = 1
            res = error * rate
            rot = la.quat_from_euler((res), order="Z")
            self.robot.local.rotation = la.quat_mul(rot, self.robot.local.rotation)

        def delete(self):
            self.scene.remove(self.robot)
            self.robot = None

        def set_name(self, name):
            self.robot_name.geometry.set_markdown(name[0] + name.split("_")[-1])

        def set_position(self, pos):
            x, y, z = pos
            self.robot.local.position = [x, y, z]

        def set_rotation(self, dir):
            rot = la.quat_from_euler((-dir), order="Z")
            self.robot.local.rotation = rot

        def set_color(self, color):
            self.robot_body.material.color = color
            self.robot_eye.material.color = (
                [1, 1, 1, 1] if color == [0.0, 0.0, 1.0, 1.0] else [0, 0, 0, 1]
            )
            self.robot_name.material.color = (
                [1, 1, 1, 1] if color == [0.0, 0.0, 1.0, 1.0] else [0, 0, 0, 1]
            )

    class World:
        def __init__(self):
            self.scene = gfx.Group()
            self.objz = 50
            self.plane = gfx.Mesh(
                gfx.plane_geometry(12000, 9000),
                gfx.MeshBasicMaterial(color=(0.2, 0.5, 0.2, 0.99), flat_shading=True),
            )
            self.plane.local.position = [0, 0, 0]
            self.scene.add(self.plane)
            self.draw_field()
            self.goal([0, 0, 1, 1], center=[-4500, 0], width=1000, depth=200)
            self.goal([1, 1, 0, 255], center=[4500, 0], width=1000, depth=200)
            self.field_boundary([0, 0], 10000, 7000, [0.2, 0.2, 0.2, 1])
            self.add_background("bg.jpg")

        def load_image(self, path):  # 读取并调整图像形状
            im = iio.imread(path)
            if len(im.shape) == 2:  # 如果图像是灰度图像，将其转换为RGB
                im = np.stack((im,) * 3, axis=-1)
            if im.shape[2] == 3:  # 如果图像没有Alpha通道，添加一个全不透明的Alpha通道
                im = np.concatenate(
                    [im, 255 * np.ones((*im.shape[:2], 1), dtype=np.uint8)], axis=2
                )
            width = im.shape[1]
            height = im.shape[0]
            # 确保调整后的形状是正确的
            im = im.reshape((height, width, 4))
            tex_size = (width, height, 1)  # 更改为2D纹理大小
            tex = gfx.Texture(im, dim=2, size=tex_size)
            return tex

        def draw_field(self):
            # 定义颜色和宽度
            color = (1.0, 1.0, 1.0, 0.8)  # 归一化到[0, 1]范围
            width = 2
            # 定义点
            Z = 1
            P1 = [-4500, 3000, Z]
            P2 = [4500, 3000, Z]
            P3 = [4500, -3000, Z]
            P4 = [-4500, -3000, Z]
            # 绘制线条
            positions = np.array([P1, P2, P3, P4, P1], dtype=np.float32)
            line = gfx.Line(
                gfx.Geometry(positions=positions),
                gfx.LineMaterial(thickness=width, color=color),
            )
            self.scene.add(line)

            # 中线和中竖线
            middle_line_positions = np.array(
                [
                    utils.middle_pos(P1, P4) + [Z],
                    utils.middle_pos(P2, P3) + [Z],
                    utils.middle_pos(P1, P2) + [Z],
                    utils.middle_pos(P3, P4) + [Z],
                ],
                dtype=np.float32,
            )

            for i in range(0, len(middle_line_positions), 2):
                line = gfx.Line(
                    gfx.Geometry(positions=middle_line_positions[i : i + 2]),
                    gfx.LineMaterial(thickness=width, color=color),
                )
                self.scene.add(line)

            # 圆弧 - 近似为一个多边形
            arc_points = []
            for angle in np.linspace(0, 2 * np.pi, 100):
                x = 500 * np.cos(angle)
                y = 500 * np.sin(angle)
                arc_points.append([x, y, Z])

            arc = gfx.Line(
                gfx.Geometry(positions=np.array(arc_points, dtype=np.float32)),
                gfx.LineMaterial(thickness=width, color=color),
            )
            self.scene.add(arc)

            # 矩形
            rect_positions = [
                [
                    [-4500, 1000, Z],
                    [-4500, -1000, Z],
                    [-3500, -1000, Z],
                    [-3500, 1000, Z],
                    [-4500, 1000, Z],
                ],
                [
                    [3500, 1000, Z],
                    [3500, -1000, Z],
                    [4500, -1000, Z],
                    [4500, 1000, Z],
                    [3500, 1000, Z],
                ],
                [
                    [-4700, 500, Z],
                    [-4700, -500, Z],
                    [-4500, -500, Z],
                    [-4500, 500, Z],
                    [-4700, 500, Z],
                ],
                [
                    [4500, 500, Z],
                    [4500, -500, Z],
                    [4700, -500, Z],
                    [4700, 500, Z],
                    [4500, 500, Z],
                ],
            ]

            for rect in rect_positions:
                rect_line = gfx.Line(
                    gfx.Geometry(positions=np.array(rect, dtype=np.float32)),
                    gfx.LineMaterial(thickness=width, color=color),
                )
                self.scene.add(rect_line)

        def add_background(self, path):
            # 读取并调整图像形状
            tex = self.load_image(path)

            background = gfx.Background(None, gfx.BackgroundSkyboxMaterial(map=tex))
            self.scene.add(background)

        def goal(self, color, center, width, depth):
            # 球门的三个板面
            z = 60
            dir = -1 if center[0] > 0 else 1
            goal_up = gfx.Mesh(
                gfx.box_geometry(10, depth, 140),
                gfx.MeshBasicMaterial(color=color, flat_shading=True),
            )
            rot = la.quat_from_euler((math.pi / 2), order="Z")
            goal_up.local.rotation = rot
            goal_up.local.position = [
                center[0] - dir * (depth / 2),
                center[1] + dir * (width / 2),
                z,
            ]

            goal_middle = gfx.Mesh(
                gfx.box_geometry(10, width, 140),
                gfx.MeshBasicMaterial(color=color, flat_shading=True),
            )
            goal_middle.local.position = [center[0] - dir * depth, center[1], z]
            goal_down = gfx.Mesh(
                gfx.box_geometry(10, depth, 140),
                gfx.MeshBasicMaterial(color=color, flat_shading=True),
            )
            rot = la.quat_from_euler((-math.pi / 2), order="Z")
            goal_down.local.rotation = rot
            goal_down.local.position = [
                center[0] - dir * (depth / 2),
                center[1] - dir * (width / 2),
                z,
            ]
            self.scene.add(goal_up, goal_middle, goal_down)

        def field_boundary(self, center, width, height, color):

            thickness = 30
            height_boundary = 1000
            z = self.objz + height_boundary / 2
            dir = -1 if center[0] > 0 else 1
            # tx = self.load_image("g1.png")

            boundary_up = gfx.Mesh(
                gfx.box_geometry(width, thickness, height_boundary),
                # gfx.MeshBasicMaterial(map = tx,color=color, flat_shading=True),
            )
            boundary_up.local.position = [center[0], center[1] + dir * (height / 2), z]
            rot = la.quat_from_euler((-math.pi), order="X")
            boundary_up.local.rotation = rot

            boundary_down = gfx.Mesh(
                gfx.box_geometry(width, thickness, height_boundary),
                # gfx.MeshBasicMaterial(map = tx,color=color, flat_shading=True),
            )
            rot = la.quat_from_euler((-math.pi), order="X")
            boundary_down.local.rotation = rot
            boundary_down.local.position = [
                center[0],
                center[1] - dir * (height / 2),
                z,
            ]

            boundary_left = gfx.Mesh(
                gfx.box_geometry(thickness, height, height_boundary),
                # gfx.MeshBasicMaterial(map = tx,color=color, flat_shading=True),
            )
            rot = la.quat_from_euler((-math.pi), order="X")
            boundary_left.local.rotation = rot
            boundary_left.local.position = [center[0] + dir * width / 2, center[1], z]

            boundary_right = gfx.Mesh(
                gfx.box_geometry(thickness, height, height_boundary),
                # gfx.MeshBasicMaterial(map = tx,color=color, flat_shading=True),
            )
            rot = la.quat_from_euler((-math.pi), order="X")
            boundary_up.local.rotation = rot
            boundary_right.local.position = [center[0] - dir * width / 2, center[1], z]

            self.scene.add(boundary_up, boundary_down, boundary_left, boundary_right)

    class Camera:
        def __init__(self):
            self.camera = gfx.PerspectiveCamera(fov=60, aspect=16 / 9, zoom=1)
            self.reset()

        def reset(self):
            self.camera.local.position = shareData.camera.position
            self.camera.local.rotation = shareData.camera.rotation
            self.follow_switch = shareData.camera.follow_switch
            self.follow_speed = shareData.camera.follow_speed
            self.camera.aspect = shareData.camera.aspect
            self.camera.fov = shareData.camera.fov
            self.camera.zoom = shareData.camera.zoom
            self.follow_obj = shareData.camera.follow_obj
            self.follow_type = shareData.camera.follow_type

        def follow(self, follow_pos, dir=0):
            if not self.follow_switch:
                return
            if self.follow_type == "TPP":

                follow_x, follow_y, follow_z = follow_pos
                new_y = self.camera.local.position[2] * math.tan(
                    la.quat_to_euler(self.camera.local.rotation)[0]
                )
                # 计算目标位置
                target_x = follow_x
                target_y = follow_y - new_y

                # 平滑地插值摄像机的位置，使其靠近目标位置
                self.camera.local.x += (
                    target_x - self.camera.local.x
                ) * self.follow_speed
                self.camera.local.y += (
                    target_y - self.camera.local.y
                ) * self.follow_speed
            else:
                # 设置摄像机的旋转
                rot = la.quat_from_euler(
                    (math.pi / 2, dir - math.pi / 2, 0), order="XYZ"
                )
                self.camera.local.rotation = rot
                # 将相机移出机器人内部
                distance = 98
                dx = math.cos(dir) * distance
                dy = math.sin(dir) * distance
                # 更新相机位置
                follow_pos[0] += dx
                follow_pos[1] += dy
                follow_pos[2] += 40  # 保持z方向的位置不变
                self.camera.local.position = follow_pos

        def config_camera(self, flag, value):
            if flag == "FOV":
                self.camera.fov = value
            elif flag == "ZOOM":
                self.camera.zoom = value
            elif flag == "ASPECT":
                self.camera.aspect = value
            elif flag == "POSITION":
                self.camera.local.position = value[:3]
            elif flag == "ROTATE":
                self.camera.local.rotation = la.quat_from_euler(value[:3], order="XYZ")
            elif flag == "FOLLOW":
                self.follow_switch = value
            elif flag == "FOLLOWSPEED":
                self.follow_speed = value / 5
            elif flag == "FOLLOWOBJ":
                self.follow_obj = value
                print(self.follow_obj)
            elif flag == "FOLLOWTYPE":
                self.follow_type = value
                self.camera.local.z = 3000
                self.camera.local.rotation = la.quat_from_euler(
                    (math.pi / 5), order="X"
                )

    def add_robot(self, tag, pos, dir, color):
        ROBOT = self.ROBOT(self._world.scene)
        ROBOT.create()
        ROBOT.set_position(pos)
        ROBOT.set_rotation(dir)
        ROBOT.set_color(color)
        ROBOT.set_name(tag)
        return ROBOT

    def remove_robot(self, tag):
        if tag in self.robots:
            self.robots[tag].delete()
            del self.robots[tag]
            del self.robot_data[tag]


class DrawSSL:
    def __init__(self) -> None:
        self.switch_draw_2d = True
        self.switch_draw_3d = True
        self.width = shareData.vision.vision_ssl_2d_image_width
        self.height = shareData.vision.vision_ssl_2d_image_height
        self.width_3d = shareData.vision.vision_ssl_3d_image_width
        self.height_3d = shareData.vision.vision_ssl_3d_image_height
        self._initialize_2d()
        if self.switch_draw_3d:
            self._initialize_3d()

        self.robot_height = shareData.draw.robot_height
        self.ball_radius = shareData.draw.ball_radius
        self.robots = {}
        self.robots_3d = {}
        self.robots_last = {}

    def _initialize_2d(self):

        self._draw_ssl_2d = Draw2DDPG(900, 600, "mini_map_drawnode")

    def _initialize_3d(self):
        self._draw_ssl_3d = DrawSSL3D(self.width_3d, self.height_3d)
        self._draw_ssl_3d._world.scene.add(gfx.AmbientLight(intensity=1))
        directional_light = gfx.DirectionalLight(
            color="#ffffff", intensity=1, cast_shadow=False
        )
        directional_light.world.z = 2000
        self._draw_ssl_3d._world.scene.add(directional_light)
        self._draw_ssl_3d.canvas.request_draw(
            lambda: self._draw_ssl_3d.renderer.render(
                self._draw_ssl_3d._world.scene, self._draw_ssl_3d._camera.camera
            )
        )

    def draw_all(self):
        if shareData.ui.now_detection_data is None:
            return
        dpg.delete_item(item="mini_map_drawnode", children_only=True)

        now_msg = shareData.ui.now_detection_data

        robots_blue = now_msg.robots_blue
        robots_yellow = now_msg.robots_yellow
        ball = now_msg.balls
        ball_pos_3d = [ball.x, ball.y, self.ball_radius]
        if self.switch_draw_2d:
            self._draw_ssl_2d.draw_field()
        self.robots = {}
        self._process_robots(robots_blue, "BLUE", [0, 0, 255, 255])
        self._process_robots(robots_yellow, "YELLOW", [255, 255, 0, 255])

        self._draw_ball(ball_pos_3d)

        if self.switch_draw_3d:
            follow_obj = self._draw_ssl_3d._camera.follow_obj

            if follow_obj == "BALL":
                follow_obj_pos = ball_pos_3d[:]
                follow_obj_dir = math.atan2(ball.vel_y, ball.vel_x)
            else:
                follow_obj_pos = self.robots[follow_obj]["pos"][:]
                follow_obj_pos[1] = -1 * follow_obj_pos[1]
                follow_obj_dir = self.robots[follow_obj]["dir"]

            self._draw_ssl_3d._camera.follow(follow_obj_pos, follow_obj_dir)

        add, remove, modified = utils.compare_dicts(self.robots_last, self.robots)
        self.robots_last = self.robots.copy()
        if self.switch_draw_3d:
            self._update_robots_3d(add, remove, modified)
            image_3d = np.asarray(self._draw_ssl_3d.canvas.draw())
            image_3d = image_3d.ravel().astype(np.float32) / 255.0
            dpg.set_value("ssl_3d_texture", image_3d)

    def _draw_ball(self, pos):
        x, y, z = pos
        # 2d
        if self.switch_draw_2d:
            self._draw_ssl_2d.draw_ball([x, -y])
        # 3D
        if self.switch_draw_3d:
            self._draw_ssl_3d._ball.add_ball_position(pos, shareData.draw.add_rate_pos)

    def _process_robots(self, robots, team, color):
        for robot in robots:
            id = robot.robot_id
            pos = [robot.x, -robot.y, self.robot_height]
            dir = robot.orientation
            tag = f"{team}_{id}"
            self.robots[tag] = {"pos": pos, "dir": dir, "color": color}
            if self.switch_draw_2d:
                self._draw_ssl_2d.draw_robot(
                    pos, shareData.draw.robot_radius, dir, color, id
                )

    def _update_robots_3d(self, add, remove, modified):
        if self.switch_draw_3d:
            for tag in add:
                self._add_robot_3d(tag)

            for tag in remove:
                self._remove_robot_3d(tag)

            for tag in modified:
                self._modify_robot_3d(tag)

    def _add_robot_3d(self, tag):
        pos = [
            self.robots[tag]["pos"][0],
            -1 * self.robots[tag]["pos"][1],
            self.robot_height,
        ]
        dir = -1 * self.robots[tag]["dir"]
        color = [x / 255.0 for x in self.robots[tag]["color"]]
        obj = self._draw_ssl_3d.add_robot(tag, pos, dir, color)
        self.robots_3d[tag] = {"pos": pos, "dir": dir, "color": color, "obj": obj}

    def _remove_robot_3d(self, tag):
        if tag in self.robots_3d:
            self.robots_3d[tag]["obj"].delete()
            del self.robots_3d[tag]

    def _modify_robot_3d(self, tag):
        if tag in self.robots and tag in self.robots_3d:
            pos = [
                self.robots[tag]["pos"][0],
                -1 * self.robots[tag]["pos"][1],
                self.robot_height,
            ]
            dir = -1 * self.robots[tag]["dir"]

            self.robots_3d[tag]["obj"].add_position(pos, shareData.draw.add_rate_pos)
            self.robots_3d[tag]["obj"].add_rotation(dir, shareData.draw.add_rate_dir)


drawSSL = DrawSSL()
