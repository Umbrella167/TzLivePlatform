import math
import src.UTILS.Utils as utils
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QBrush, QPolygon, QFont
from PyQt6.QtCore import QPoint, QRect
import numpy as np
import pygfx as gfx
from src.SHARE.ShareData import shareData
import dearpygui.dearpygui as dpg
import tzcp.ssl.rocos.zss_vision_detection_pb2 as detection
import pylinalg as la
import imageio.v3 as iio
from wgpu.gui.offscreen import WgpuCanvas

import copy


class Draw2D:
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

    def draw_start(self):
        self.clear()

        self.painter = QPainter(self.image)
        self.painter.translate(self.width / 2, self.height / 2)
        scale_width = self.width / 12000
        scale_height = self.height / 9000
        self.painter.scale(scale_width, scale_height)

    def draw_end(self):
        self.painter.end()

    def clear(self):

        self.image.fill(self.background_color)


class DrawSSL3D:
    def __init__(self, width, height) -> None:
        self._world = self.World()
        self._camera = self.Camera()
        self.width = width
        self.height = height
        self.robots = {}
        self.canvas = WgpuCanvas(size=(self.width, self.height), max_fps=888)
        self.renderer = gfx.renderers.WgpuRenderer(self.canvas)

    class ROBOT:
        def __init__(self, scene):
            self.scene = scene
            self.car = None

        def create(self):
            # Create a box geometry
            self.car = gfx.Group(visible=True)
            self.car_body = gfx.Mesh(
                gfx.box_geometry(130, 130, 130),
                gfx.MeshPhongMaterial(color=(0, 0, 1, 1), flat_shading=True),
            )
            self.car_eye = gfx.Mesh(
                gfx.box_geometry(10, 120, 50),
                gfx.MeshPhongMaterial(color=(0, 0, 1, 1), flat_shading=True),
            )

            self.car_eye.local.position = [70, 0, 50]
            self.car.add(self.car_body, self.car_eye)
            self.scene.add(self.car)

        def delete(self):
            self.scene.remove(self.car)
            self.car = None

        def set_position(self, pos):
            x, y = pos
            z = shareData.draw.ball_radius
            # print(x,y)
            self.car.local.position = [x, y, z]
            # self.car.local.position.y = y

        def set_rotation(self, dir):
            rot = la.quat_from_euler((-dir), order="Z")
            self.car.local.rotation = rot

        def set_color(self, color):
            self.car_body.material.color = color
            self.car_eye.material.color = (
                [1, 1, 1, 1] if color == "BLUE" else [0, 0, 0, 1]
            )

    class World:
        def __init__(self):
            self.scene = gfx.Group()
            self.objz = 50
            self.plane = gfx.Mesh(
                gfx.plane_geometry(12000, 9000),
                gfx.MeshBasicMaterial(color=(0, 1, 0, 0), flat_shading=True),
            )
            self.plane.local.position = [0, 0, 0]
            self.scene.add(self.plane)
            self.goal([0, 0, 1, 1], center=[-4500, 0], width=1000, depth=200)
            self.goal([1, 1, 0, 255], center=[4500, 0], width=1000, depth=200)
            self.field_boundary([0, 0], 10000, 7000, [0.2, 0.2, 0.2, 1])

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
            self.camera = gfx.PerspectiveCamera(70, 1)
            self.camera.local.position = [0, -2000, 5000]
            # self.camera.local.rotation = la.quat_from_euler((math.pi / 2), order="Z")

        def follow(self, follow_pos, move_y):
            follow_x, follow_y, follow_z = follow_pos
            error_x = follow_x - self.camera.local.x
            error_y = (move_y + follow_y) - self.camera.local.y
            if abs(error_x) > 100 and abs(error_x) < 500:
                self.camera.local.x += error_x / 80
            elif abs(error_x) > 500:
                self.camera.local.x += error_x / 20
            if abs(error_y) > 100 and abs(error_y) < 500:
                self.camera.local.y += error_y / 80
            elif abs(error_y) > 500:
                self.camera.local.y += error_y / 20

    def add_robot(self, tag, pos, dir, color):
        ROBOT = self.ROBOT(self._world.scene)
        ROBOT.create()
        ROBOT.set_position(pos)
        ROBOT.set_rotation(dir)
        ROBOT.set_color(color)
        return ROBOT

    def remove_robot(self, tag):
        if tag in self.robots:
            self.robots[tag].delete()
            del self.robots[tag]
            del self.car_data[tag]


class DrawSSL2D:

    def __init__(self):
        width = shareData.vision.vision_ssl_2d_image_width
        height = shareData.vision.vision_ssl_2d_image_height
        self._draw2D = Draw2D(height, width)

    def draw_robot(self, pos, radius, dir, color):
        angle = dir * (180 / math.pi)
        start_angle = 45 + angle
        end_angle = 315 + angle
        # 将角度转换为弧度
        start_radians = np.radians(start_angle)
        end_radians = np.radians(end_angle)
        # 计算每个分段的角度
        angles = np.linspace(start_radians, end_radians, 50)
        # 计算弧线上的点
        x = pos[0] + radius * np.cos(angles)
        y = pos[1] - radius * np.sin(angles)
        # 将点转换为列表格式
        points = np.column_stack((x, y)).tolist()
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

    def draw_all(self):

        if shareData.ui.now_msg is None:
            return

        now_msg = shareData.ui.now_msg
        package = detection.Vision_DetectionFrame()
        package.ParseFromString(now_msg)

        self._draw2D.draw_start()
        self.draw_field()
        robots_blue = package.robots_blue
        robots_yellow = package.robots_yellow
        ball = package.balls

        for robot in robots_blue:
            pos = [robot.x, -robot.y]
            dir = robot.orientation
            color = [0, 0, 255, 255]
            self.draw_robot(pos, 110, dir, color)

        for robot in robots_yellow:
            pos = [robot.x, -robot.y]
            dir = robot.orientation
            color = [255, 255, 0, 255]
            self.draw_robot(pos, 110, dir, color)

        self.draw_ball([ball.x, -ball.y], 47)
        image = self._draw2D.to_dpg_texture()
        dpg.set_value("ssl_2d_texture", image)
        self._draw2D.draw_end()


class DrawSSL:
    def __init__(self) -> None:
        self.switch_draw_2d = False
        self.switch_draw_3d = True
        self.width = shareData.vision.vision_ssl_2d_image_width
        self.height = shareData.vision.vision_ssl_2d_image_height
        self._initialize_2d()
        if self.switch_draw_3d:
            self._initialize_3d()
        self.robots = {}
        self.robots_3d = {}
        self.robots_last = {}

    def _initialize_2d(self):
        self._draw_ssl_2d = DrawSSL2D()
        self._draw_ssl_2d._draw2D.draw_start()
        self._draw_ssl_2d.draw_field()
        self.tex = self._draw_ssl_2d._draw2D.to_gfx_texture()

    def _initialize_3d(self):
        self._draw_ssl_3d = DrawSSL3D(self.width, self.height)
        self.ball = gfx.Mesh(
            gfx.sphere_geometry(43, 43, 43),
            gfx.MeshPhongMaterial(color=(1, 0.647, 0, 1), flat_shading=True),
        )
        self._draw_ssl_3d._world.plane.material.map = self.tex
        self._draw_ssl_3d._world.scene.add(gfx.AmbientLight())
        self._draw_ssl_3d._world.scene.add(self.ball)
        self.ball.local.position = [0, 0, shareData.draw.ball_radius]
        directional_light = gfx.DirectionalLight()
        directional_light.world.z = 4000
        self._draw_ssl_3d._world.scene.add(directional_light)
        self.controller = gfx.OrbitController(self._draw_ssl_3d._camera.camera)
        self._draw_ssl_3d.canvas.request_draw(
            lambda: self._draw_ssl_3d.renderer.render(
                self._draw_ssl_3d._world.scene, self._draw_ssl_3d._camera.camera
            )
        )

    def draw_all(self):
        if shareData.ui.now_msg is None:
            return

        now_msg = shareData.ui.now_msg
        package = detection.Vision_DetectionFrame()
        package.ParseFromString(now_msg)
        robots_blue = package.robots_blue
        robots_yellow = package.robots_yellow
        ball = package.balls

        if self.switch_draw_2d:
            self._draw_ssl_2d._draw2D.draw_start()
            self._draw_ssl_2d.draw_field()
        self.robots = {}
        self._process_robots(robots_blue, "BLUE", [0, 0, 255, 255])
        self._process_robots(robots_yellow, "YELLOW", [255, 255, 0, 255])

        
        self._draw_ball([ball.x, ball.y], shareData.draw.ball_radius)
        if self.switch_draw_3d:
            self._draw_ssl_3d._camera.follow(self.ball.local.position, 0)

        if self.switch_draw_2d:
            image_2d = self._draw_ssl_2d._draw2D.to_dpg_texture()
            dpg.set_value("ssl_2d_texture", image_2d)
            self._draw_ssl_2d._draw2D.draw_end()
        add, remove, modified = utils.compare_dicts(self.robots_last, self.robots)
        
        self.robots_last = self.robots.copy()


        if self.switch_draw_3d:
            self._update_robots_3d(add, remove, modified)
            image_3d = (
                np.array(self._draw_ssl_3d.canvas.draw()).ravel().astype(np.float32) / 255.0
            )
            dpg.set_value("ssl_3d_texture", image_3d)

    def _draw_ball(self, pos, radius):
        x, y = pos
        # 2d
        if self.switch_draw_2d:
            self._draw_ssl_2d.draw_ball([x, -y], 47)
        # 3D
        if self.switch_draw_3d:
            ball_smooth = self.ball.local.position - [x, y, 47]
            rate = 0.35
            self.ball.local.position.setflags(write=True)
            self.ball.local.position -= [
                ball_smooth[0] * rate,
                ball_smooth[1] * rate,
                0,
            ]

    def _process_robots(self, robots, team, color):
        for robot in robots:
            id = robot.robot_id
            pos = [robot.x, -robot.y]
            dir = robot.orientation
            tag = f"{team}_{id}"
            self.robots[tag] = {"pos": pos, "dir": dir, "color": color}
            if self.switch_draw_2d:
                self._draw_ssl_2d.draw_robot(pos, 110, dir, color)

    def _update_robots_3d(self, add, remove, modified):
        if self.switch_draw_3d:
            for tag in add:
                self._add_robot_3d(tag)

            for tag in remove:
                self._remove_robot_3d(tag)

            for tag in modified:
                self._modify_robot_3d(tag)

    def _add_robot_3d(self, tag):
        pos = [self.robots[tag]["pos"][0], -1 * self.robots[tag]["pos"][1]]
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
            pos = [self.robots[tag]["pos"][0], -1 * self.robots[tag]["pos"][1]]
            dir = -1 * self.robots[tag]["dir"]
            self.robots_3d[tag]["obj"].set_position(pos)
            self.robots_3d[tag]["obj"].set_rotation(dir)


drawSSL = DrawSSL()
