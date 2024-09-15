# unset PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION
# export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
import sys 
sys.path.append("src/EVENT")
# sys.path.append("..")

# from src.UI.Ui import ui
import event_pb2
import dearpygui.dearpygui as dpg
import time
import sys
import socket
import time


# Global variables for start and end times
start_time = time.time()
end_time = time.time()

# Create Dear PyGui context
dpg.create_context()

def start(sender, app_data):
    global start_time
    start_time = time.time() * 1e9
    print(start_time)

def end(sender, app_data):
    global end_time
    end_time = time.time() * 1e9
    print(end_time)

def send(sender, app_data,user_data):
    name = dpg.get_value("name")
    type = dpg.get_value("type")
    tag = dpg.get_value("tag")
    color = dpg.get_value("color")
    index = dpg.get_value("index")
    level = dpg.get_value("level")
    # Create an EventMessage
    event_message = event_pb2.EventMessage()
    event_message.name = name
    event_message.type = type
    event_message.tag = tag
    event_message.color_rgba.extend(color)
    event_message.index = index
    event_message.start_time = int(start_time)
    event_message.end_time = int(end_time)
    event_message.level = int(level)
    
    # extend([255, 0, 0, 255])
    # Serialize the message to a string
    message_data = event_message.SerializeToString()
    
    # Define the UDP address and port
    udp_ip = "127.0.0.1"  # Localhost for testing
    udp_port = 1670      # Port number
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Send the serialized message
    sock.sendto(message_data, (udp_ip, udp_port))
    print("Message sent to {}:{}".format(udp_ip, udp_port))

# Create the GUI layout
with dpg.window(width=500, height=300, tag="main"):
    dpg.add_spacer(height=20)
    
    with dpg.group(horizontal=True):
        dpg.add_text("Name: ")
        dpg.add_input_text(tag = "name")
        
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True):
        dpg.add_text("Tyep: ")
        dpg.add_input_text(tag = "type")
    
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True):
        dpg.add_text("Tag : ")
        dpg.add_input_text(tag = "tag")
    
    
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True):
        dpg.add_text("Color: ")
        dpg.add_color_picker(tag = "color",width=150, height=300)
        
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True):
        dpg.add_text("Index: ")
        dpg.add_input_int(tag = "index")
        
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True):
        dpg.add_text("Level: ")
        dpg.add_input_int(tag = "level")
    dpg.add_spacer(height=30)

    with dpg.group(horizontal=True):
        dpg.add_button(label="start", width=250, height=250, tag="start", callback=start)
        dpg.add_button(label="end", width=250, height=250, tag="end", callback=end)
        dpg.add_button(label="send", width=250, height=250, tag="send", callback=send)

# Setup the viewport
dpg.create_viewport(width=800, height=600, title="")
dpg.set_primary_window("main", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()