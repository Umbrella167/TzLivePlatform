import math
import src.UTILS.Utils as utils
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QBrush, QPolygon, QFont
from PyQt6.QtCore import QPoint, QRect
import numpy as np
import pygfx as gfx
from src.SHARE.ShareData import shareData
import dearpygui.dearpygui as dpg
import cv2

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
        texture = arr.ravel().astype('float32') / 255.0
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


class DrawSSL2D:

    def __init__(self, ):
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
        index = shareData.ui.now_tick
        if index is None:
            index = shareData.ui.plot_elapsed_time
        if index in shareData.vision.vision_data:
            self._draw2D.draw_start()
            self.draw_field()
            packge = shareData.vision.vision_data[index]
            robots_blue = packge.robots_blue
            robots_yellow = packge.robots_yellow
            ball = packge.balls
            
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
            
        
