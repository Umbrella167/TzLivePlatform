# -- coding: utf-8 --
import sys
from ctypes import *
import cv2
import numpy as np
sys.path.append("src/UI/MvImport")

from MvCameraControl_class import *
cam = MvCamera()
device_list = MV_CC_DEVICE_INFO_LIST()
ret = cam.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, device_list)

def undistort_image(image, K, D):
    """
    校正图像的畸变

    参数:
    - image_path: 输入图像的路径
    - K: 相机内参矩阵 (3x3)
    - D: 畸变系数 (1x5 或 1x4)

    返回:
    - undistorted_image: 校正后的图像
    """
    # 获取图像尺寸
    h, w = image.shape[:2]
    # 计算校正后的图像尺寸和校正映射
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(K, D, (w, h), 1, (w, h))
    mapx, mapy = cv2.initUndistortRectifyMap(K, D, None, new_camera_matrix, (w, h), 5)

    # 使用映射校正图像
    undistorted_image = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

    # 裁剪结果图像
    x, y, w, h = roi
    undistorted_image = undistorted_image[y:y+h, x:x+w]

    return undistorted_image



def set_gain(value):

    #设置曝光增益
    ret = cam.MV_CC_SetFloatValue("Gain", value)
    if ret != 0:
        print("Start grabbing failed! ret[0x%x]" % ret)
        sys.exit()
def set_exposuretime(value):

    #设置曝光增益
    ret = cam.MV_CC_SetFloatValue("ExposureTime", value)
    if ret != 0:
        print("Start grabbing failed! ret[0x%x]" % ret)
        sys.exit()

def init_creame():
    # 枚举设备
    device_list = MV_CC_DEVICE_INFO_LIST()
    ret = cam.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, device_list)
    if ret != 0:
        print("Enum devices failed! ret[0x%x]" % ret)
        sys.exit()

    if device_list.nDeviceNum == 0:
        print("No devices found!")
        sys.exit()

    # 选择设备
    stDeviceList = cast(device_list.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents

    # 创建句柄
    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print("Create handle failed! ret[0x%x]" % ret)
        sys.exit()

    # 打开设备
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("Open device failed! ret[0x%x]" % ret)
        sys.exit()

    #设置曝光是时间
    ret = cam.MV_CC_SetFloatValue("ExposureTime", 10000)
    if ret != 0:
        print("Start grabbing failed! ret[0x%x]" % ret)
        sys.exit()

    #设置曝光增益
    ret = cam.MV_CC_SetFloatValue("Gain", 20)
    if ret != 0:
        print("Start grabbing failed! ret[0x%x]" % ret)
        sys.exit()
    # 开始取流
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print("Start grabbing failed! ret[0x%x]" % ret)
        sys.exit()
def get_frame_processing():
    # 设置数据帧缓存


    data_buf = (c_ubyte * (1920 * 1080 * 3))()  # Adjust buffer size based on your camera resolution
    frame_info = MV_FRAME_OUT_INFO_EX()
    ret = cam.MV_CC_GetImageForBGR(byref(data_buf), len(data_buf), frame_info, 1000)
    if ret == 0:
        # 将图像数据转换为 OpenCV 格式
        img = np.frombuffer(data_buf, count=frame_info.nWidth * frame_info.nHeight * 3, dtype=np.uint8)
        img = img.reshape((frame_info.nHeight, frame_info.nWidth, 3))
        # K = np.array([[1196.97842714,    0.        ,  823.80786268],
        #       [   0.        , 4310.70055051,  620.75243586],
        #       [   0.        ,    0.        ,    1.        ]])
        # K = np.array([[909.83196571   ,0.         ,799.57967403],
        #         [  0.         ,797.21441997 ,479.55851193],
        #         [  0.           ,0.           ,1.        ]])
        # # # 提供的畸变系数
        # D = np.array([[-0.04681881  ,0.01968327 ,-0.01421837  ,0.00456728  ,0.00063222]])
        # #         D = np.array([-0.55093027,  3.60085548, -0.01496787, -0.05253373, -16.95236632])
        # img = undistort_image(img, K, D)
        return img
    return None
def get_frame():
    while True:
        # 设置数据帧缓存
        data_buf = (c_ubyte * (1920 * 1080 * 3))()  # Adjust buffer size based on your camera resolution
        frame_info = MV_FRAME_OUT_INFO_EX()
        ret = cam.MV_CC_GetImageForBGR(byref(data_buf), len(data_buf), frame_info, 1000)
        if ret == 0:
            # 将图像数据转换为 OpenCV 格式
            img = np.frombuffer(data_buf, count=frame_info.nWidth * frame_info.nHeight * 3, dtype=np.uint8)
            img = img.reshape((frame_info.nHeight, frame_info.nWidth, 3))
            # K = np.array([[1196.97842714,    0.        ,  823.80786268],
            #       [   0.        , 4310.70055051,  620.75243586],
            #       [   0.        ,    0.        ,    1.        ]])
            # K = np.array([[909.83196571   ,0.         ,799.57967403],
            #         [  0.         ,797.21441997 ,479.55851193],
            #         [  0.           ,0.           ,1.        ]])
    # # # 提供的畸变系数
            # D = np.array([[-0.04681881  ,0.01968327 ,-0.01421837  ,0.00456728  ,0.00063222]])
    # #         D = np.array([-0.55093027,  3.60085548, -0.01496787, -0.05253373, -16.95236632])
            # img = undistort_image(img, K, D)
            data.camera = img
def creame_stop():
    # 停止取流D
    cam.MV_CC_StopGrabbing()
    # 关闭设备
    cam.MV_CC_CloseDevice()
    # 销毁句柄
    cam.MV_CC_DestroyHandle()
    cv2.destroyAllWindows()
# if __name__ == "__main__":
#     main()
global src_points
src_points = np.array([[-4500, -3000], [4500, -3000], [4500, 3000], [-4500, 3000]], dtype=np.float32)

def perspective_transform(point):
    global src_points
    """
    进行透视变换，将点从一个图像坐标映射到另一个图像坐标

    Args:
    point (tuple): 输入的点 (x, y)
    src_points (list): 原图像的四个点 [(p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y)]
    dst_points (list): 目标图像的四个点 [(p11x, p11y), (p22x, p22y), (p33x, p33y), (p44x, p44y)]
    
    Returns:
    tuple: 变换后点的坐标 (x', y')
    """
    dst_points = np.array([data.PARAM.field.p[0], data.PARAM.field.p[1], data.PARAM.field.p[2], data.PARAM.field.p[3]], dtype=np.float32)
    # 计算透视变换矩阵
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # 将输入的点转换为numpy数组并增加一个维度
    point = np.array([point], dtype=np.float32)
    point = np.array([point])

    # 使用透视变换矩阵进行变换
    transformed_point = cv2.perspectiveTransform(point, matrix)

    # 返回变换后的点
    return (transformed_point[0][0][0], transformed_point[0][0][1])

def perspective_transform_s(points):
    """
    进行透视变换，将点从一个图像坐标映射到另一个图像坐标

    Args:
    points (list): 输入的点列表 [[x1, y1], [x2, y2], ...]
    matrix (numpy.ndarray): 预计算的透视变换矩阵
    
    Returns:
    list: 变换后点的坐标列表 [[x1', y1'], [x2', y2'], ...]
    """
    dst_points = np.array([data.PARAM.field.p[0], data.PARAM.field.p[1], data.PARAM.field.p[2], data.PARAM.field.p[3]], dtype=np.float32)
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    points = np.array(points, dtype=np.float32)
    points = np.expand_dims(points, axis=0)
    transformed_points = cv2.perspectiveTransform(points, perspective_matrix)
    return transformed_points[0].tolist()

def perspective_transform_s_line(points,p):
    """
    进行透视变换，将点从一个图像坐标映射到另一个图像坐标

    Args:
    points (list): 输入的点列表 [[x1, y1], [x2, y2], ...]
    matrix (numpy.ndarray): 预计算的透视变换矩阵
    
    Returns:
    list: 变换后点的坐标列表 [[x1', y1'], [x2', y2'], ...]
    """
    dst_points = np.array(p, dtype=np.float32)
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    points = np.array(points, dtype=np.float32)
    points = np.expand_dims(points, axis=0)
    transformed_points = cv2.perspectiveTransform(points, perspective_matrix)
    return transformed_points[0].tolist()
    