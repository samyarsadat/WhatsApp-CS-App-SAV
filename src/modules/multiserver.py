#  WhatsApp messaging client project
#  Handles multi-server SocketIO endpoints
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
from config import AppConfig
from flask import Blueprint, request
from init import socketio, debug_log
from modules.database import PhoneNumber


# ------- Blueprint init -------
multi_server = Blueprint("multi_server", __name__, template_folder="../templates", static_folder="../static")


# ------- Global variables -------
API_PREFIX = AppConfig.MULTISERVER_API_PREFIX


# ------- Functions -------
def get_total_unread_msgs() -> int:
    phone_numbers = PhoneNumber.query.all()
    total_unread_messages = 0
        
    for number in phone_numbers:
        total_unread_messages = total_unread_messages + int(number.unread_msgs)
        
    return total_unread_messages


# ------- SocketIO -------
@socketio.on("disconnect", namespace="/multiserver-socket")
def handle_socket_connect():
    debug_log.debug(f"[SocketIO-Multiserver] [{request.remote_addr}] Disconnected.")


@socketio.on("connect", namespace="/multiserver-socket")
def handle_socket_connect():
    debug_log.debug(f"[SocketIO-Multiserver] Received [connect] event from [{request.remote_addr}]")
    socketio.emit("unread_msgs_update", {"unread_msgs": get_total_unread_msgs()}, namespace="/multiserver-socket")
    
    
def multiserv_handle_message_change(change: str):
    if change == "msg_received":
        debug_log.debug(f"[SocketIO-Multiserver] Received message, emitting unread messages event.")
        socketio.emit("unread_msgs_update", {"unread_msgs": get_total_unread_msgs()}, namespace="/multiserver-socket")