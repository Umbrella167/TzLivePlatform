# -*- coding: utf-8 -*-
"""
@Brief: This is an action module to control grSim's robots
@Version: grSim 4 camera version
@author: Wang Yunkai
"""

import socket
import numpy as np
from time import sleep
import VISION.grSim_Packet_pb2 as sim_pkg

ACTION_IP = '127.0.0.1' # local host grSim
ACTION_PORT = 20011 # grSim command listen port

class ActionModule:
    def __init__(self, ACTION_IP='127.0.0.1', ACTION_PORT=20011):
        self.address = (ACTION_IP, ACTION_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send_start_package(self):
        self.socket.sendto(self.start_package, self.address)
    
    def send_action(self, robot_num=0, vx=0, vy=0, w=0):
        package = sim_pkg.grSim_Packet()
        commands = package.commands
        
        commands.timestamp = 0
        commands.isteamyellow = False
        command = commands.robot_commands.add()
        command.id = robot_num
        command.kickspeedx = 0
        command.kickspeedz = 0
        command.veltangent = vx
        command.velnormal = vy
        command.velangular = w
        command.spinner = 0
        command.wheelsspeed = False
        
        self.socket.sendto(package.SerializeToString(), self.address)
        
    def reset(self, robot_num):
        package = sim_pkg.grSim_Packet()
        replacement = package.replacement
        #ball_rep = replacement.ball
        bot_rep = replacement.robots.add()
        
        #ball_rep.x = 100.0
        #ball_rep.y = 0.0
        #ball_rep.vx = 0.0
        #ball_rep.vy = 0.0
        
        bot_rep.x = 0.0
        bot_rep.y = 0.0
        bot_rep.dir = 0.0
        bot_rep.id = robot_num
        bot_rep.yellowteam = False
        
        self.socket.sendto(package.SerializeToString(), self.address)
        
    def reset_ball(self):
        package = sim_pkg.grSim_Packet()
        replacement = package.replacement
        ball_rep = replacement.ball
        ball_rep.x = np.random.randint(-600, 600)/100.0
        ball_rep.y = np.random.randint(-450, 450)/100.0
        ball_rep.vx = 0.0
        ball_rep.vy = 0.0
        self.socket.sendto(package.SerializeToString(), self.address)

    def reset_bot(self, robot_num):
        package = sim_pkg.grSim_Packet()
        replacement = package.replacement
        bot_rep = replacement.robots.add()
        
        bot_rep.x = np.random.randint(-600, 600)/100.0
        bot_rep.y = np.random.randint(-450, 450)/100.0
        bot_rep.dir = np.pi*np.random.randint(-180, 180)/180.0
        bot_rep.id = robot_num
        bot_rep.yellowteam = False
        
        self.socket.sendto(package.SerializeToString(), self.address)
        
if __name__ == "__main__":
    action = ActionModule(ACTION_IP, ACTION_PORT)
    action.reset(robot_num=1)
    while(True):
        action.send_action(robot_num=6, vx=3, vy=0, w=0)
        sleep(0.015)