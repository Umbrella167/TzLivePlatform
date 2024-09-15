# -*- coding: utf-8 -*-
"""
@Brief: This is a vision module(single robot) for RoboCup Small Size League 
@Version: grSim 4 camera version
@author: Wang Yunkai
"""

import socket
# import src.VISION.vision_detection_pb2 as detection
# import src.VISION.zss_debug_pb2 as debugs
import tzcp.ssl.rocos.zss_vision_detection_pb2 as detection
import tzcp.ssl.rocos.zss_debug_pb2 as debugs
from src.EVENT.event_pb2 import EventMessage
class VisionModule:
    def __init__(self, VISION_PORT=23333, SENDERIP = '0.0.0.0'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
        self.sock.bind((SENDERIP,VISION_PORT))
        self.robot_info = [0, 0, 0, 0, 0, 0]
        self.ball_info = [0, 0, 0, 0]
        # self.logger = log.Logger()
    def receive(self):
        data, addr = self.sock.recvfrom(65535)
        # self.logger.log(message_data = data, save_module="Chunking", size=1000)
        return data

    def data_to_str(self,data):
        package = detection.Vision_DetectionFrame()
        package.ParseFromString(data)
        return package

    def get_info(self):
        data = self.receive()
        # return self.data_to_str(data)   
        return data

    
class DEBUG:
    def __init__(self, VISION_PORT=23333, SENDERIP='0.0.0.0'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SENDERIP, VISION_PORT))
        self.robot_info = [0, 0, 0, 0, 0, 0]
        self.ball_info = [0, 0, 0, 0]

    def receive(self):
        data, addr = self.sock.recvfrom(65535)
        return data

    def get_info(self):
        data = self.receive()
        debug_message = debugs.Debug_Msgs()
        debug_message.ParseFromString(data)
        return debug_message
    
    
    
class EVENT:
    def __init__(self, VISION_PORT=1670, SENDERIP='0.0.0.0'):
        # Initialize a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SENDERIP, VISION_PORT))

    def receive(self):
        # Receive data from the socket
        data, addr = self.sock.recvfrom(65535)
        return data

    def get_info(self):
        # Receive the data
        data = self.receive()

        # Parse the data assuming it's an EventMessage
        try:
            event = EventMessage()
            event.ParseFromString(data)
            # Return the parsed event for further processing if needed
            return event
        except Exception as e:
            print(f"Failed to parse EventMessage: {e}")
            return None