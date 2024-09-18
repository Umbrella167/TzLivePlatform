import numpy as np
import time


class ShareData:

    def __init__(self):
        self.input = self.Input()
        self.vision = self.Vision()
        self.ui = self.Ui()
        self.time = self.times()
        self.event = self.Event()
        self.draw = self.Draw()

    class Input:
        def __init__(self):
            self.switch_proto_received = False

    class Draw:
        def __init__(self):
            self.ball_radius = 43

    class Vision:
        def __init__(self):
            self.vision_data = {}
            self.vision_data_count = 0
            self.vision_ssl_2d_image_width = 600
            self.vision_ssl_2d_image_height = 900
            self.vision_ssl_3d_image_width = 600
            self.vision_ssl_3d_image_height = 900
            
            self.vision_ssl_2d_image = np.zeros(
                (self.vision_ssl_2d_image_width * self.vision_ssl_2d_image_height * 4),
                dtype=np.float32,
            )
            self.vision_ssl_3d_image = np.zeros(
                (self.vision_ssl_3d_image_height * self.vision_ssl_3d_image_width * 4),
                dtype=np.float32,
            )
    class Ui:
        def __init__(self):
            self.plot_timeshapes_x = [0]
            self.plot_timeshapes_y = [1]
            self.plot_original_area_height = 5
            self.plot_elapsed_time = 0
            self.now_msg = None
            self.real_msg = None

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
                # "index":0,
                # "color_rgba":(255,255,255,255),
                # "level": 0,
            }
            self.event_list = []


shareData = ShareData()
