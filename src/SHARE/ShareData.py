import numpy as np
import time
import math
import pylinalg as la

class ShareData:

    def __init__(self):
        self.input = self.Input()
        self.vision = self.Vision()
        self.ui = self.Ui()
        self.time = self.times()
        self.event = self.Event()
        self.draw = self.Draw()
        self.camera = self.Camera()
    class Camera:
        def __init__(self):
            self.position = [0, -2000, 3000]
            self.rotation = la.quat_from_euler((math.pi / 5), order="X")
            self.aspect = 2 / 1
            self.fov = 75
            self.zoom = 1
            self.follow_switch = True
            self.follow_speed = 0.1
            self.follow_obj = "BALL"
            self.follow_type = "TPP"
    class Input:
        def __init__(self):
            self.switch_proto_received = False

    class Draw:
        def __init__(self):
            self.ball_radius = 43
            self.robot_radius = 110
            self.robot_height = 50
            self.add_rate_pos = 0.5
            self.add_rate_dir = 0.5
            self.add_threshold_pos = 1.0
            self.add_threshold_dir = 5
            self.scale_2d = 1.0
    class Vision:
        def __init__(self):
            self.vision_data = {}
            self.vision_data_count = 0
            height = 800
            width = 1600
            
            self.vision_ssl_2d_image_width = width
            self.vision_ssl_2d_image_height = height
            self.pixel_ratio = 2
            self.vision_ssl_3d_image_height = 400 * self.pixel_ratio
            self.vision_ssl_3d_image_width = 800 * self.pixel_ratio
            self.main_ssl_image_width = width
            self.main_ssl_image_height = height
            self.vision_ssl_2d_image = np.zeros(
                (self.vision_ssl_2d_image_width * self.vision_ssl_2d_image_height * 4),
                dtype=np.float32,
            )
            self.vision_ssl_3d_image = np.zeros(
                (int(self.vision_ssl_3d_image_width) * int(self.vision_ssl_3d_image_height) * 4),
                dtype=np.float32,
            )
    class Ui:
        def __init__(self):
            self.plot_timeshapes_x = [0]
            self.plot_timeshapes_y = [1]
            self.plot_original_area_height = 5
            self.plot_elapsed_time = 0
            self.now_detection_data = None
            self.detection_data_real_tiem = None
            self.interpolate_frames = []
            self.play_speed = 1.0
    class times:
        def __init__(self):
            self.start_time = time.time()
            self.elapsed_time = 0

    class Event:
        def __init__(self):
            self.event = {
                # "name": "",
                # "start_time": 0,
                # "end_time":0,
                # "type": "",
                # "tag":"",
                # "color_rgba":(255,255,255,255),
                # "level": 0,
            }
            self.event_list = []


shareData = ShareData()
