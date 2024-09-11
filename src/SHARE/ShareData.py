import numpy as np
class ShareData:

    def __init__(self):
        self.input = self.Input()
        self.vision = self.Vision()
        self.ui = self.Ui()

    class Input:
        def __init__(self):
            self.switch_proto_received = False

    class Vision:
        def __init__(self):
            self.vision_data = {}
            self.vision_data_count = 0
            self.vision_ssl_2d_image_width = 400
            self.vision_ssl_2d_image_height = 600
            self.vision_ssl_2d_image = np.zeros((self.vision_ssl_2d_image_width * self.vision_ssl_2d_image_height * 4,), dtype=np.float32)
    class Ui:
        def __init__(self):
            self.plot_timeshapes_x = [0]
            self.plot_timeshapes_y = [1]
            self.plot_elapsed_time = 0
            self.now_tick = None

shareData = ShareData()
