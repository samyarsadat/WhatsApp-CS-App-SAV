#  WhatsApp messaging client project
#  WhatsApp API interface module
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import uuid
import requests
from functools import wraps
from init import waapi, log, debug_log, app
from config import AppConfig
from flask_security import verify_password
from flask import Response, request, url_for
from msg_dsp_text import WA_SYSTEM_RESPONSES
from enum import Enum
from typing import Union


# ------- Global variables -------
API_URL_PREFIX = AppConfig.WAAPI_URL_PREFIX
API_CALLBACK_PREFIX = API_URL_PREFIX + "/callbacks"

# ---- Callback endpoints ----
MESSAGE_STATUS_CALLBACK = API_CALLBACK_PREFIX + "/message_status_update"
MESSAGE_RECEIVE_CALLBACK = API_CALLBACK_PREFIX + "/message_receive"
ALWAYS_200_FAKE_CALLBACK = API_CALLBACK_PREFIX + "/fake_200_callback"


# -=-=-= Functions =-=-=-
def check_call_creds(username: str, password: str) -> bool:
    if username == AppConfig.WAAPI_REQUEST_BASIC_AUTH_USER and verify_password(password, AppConfig.WAAPI_REQUEST_BASIC_AUTH_PASS_HASH):
        return True
    
    return False
            

# -=-=-= Decorators =-=-=-
def authenticate_http_basic(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.args.get("user")
        password = request.args.get("pass")
        
        if not (username and password) or not check_call_creds(username, password):
            debug_log.debug("[WhatsApp API Interface] Basic HTTP authentication for callback request failed. Responding with [WWW-Authenticate] header.")
            return Response("<h1>401 Unauthorized</h1>Please provide valid credentials.", 401, {"WWW-Authenticate": 'Basic realm="WaapiCallbacks"'})
        
        debug_log.debug("[WhatsApp API Interface] Callback request HTTP basic authentication successful.")
        return f(*args, **kwargs)
    return decorated_function


# -=-=-= Enums =-=-=-
class MessageType(Enum):
    TEXT = 0
    DOCUMENT = 1
    IMAGE = 2
    AUDIO = 3
    VOICE = 4
    VIDEO = 5
    STICKER = 6
    LOCATION = 7
    CONTACT = 8
    
    def from_str(string: str) -> Union["MessageType", None]:
        string = string.upper()
        
        if string == MessageType.TEXT.name: return MessageType.TEXT
        elif string == MessageType.DOCUMENT.name: return MessageType.DOCUMENT
        elif string == MessageType.IMAGE.name: return MessageType.IMAGE
        elif string == MessageType.AUDIO.name: return MessageType.AUDIO
        elif string == MessageType.VOICE.name: return MessageType.VOICE
        elif string == MessageType.VIDEO.name: return MessageType.VIDEO
        elif string == MessageType.STICKER.name: return MessageType.STICKER
        elif string == MessageType.LOCATION.name: return MessageType.LOCATION
        elif string == MessageType.CONTACT.name: return MessageType.CONTACT
        else: return None


class MessageStatus(Enum):
    PENDING = 0
    FAILED = 1
    SENT = 2
    DELIVERED = 3
    READ = 4
    
    def from_api_response(api_status_response: dict) -> Union["MessageStatus", None]:
        if api_status_response:
            API_STATUS_TO_ENUM_TABLE = {
                MessageStatus.PENDING: [{"groupName": "PENDING"}, {"group_name": "PENDING"}],
                MessageStatus.FAILED: [{"groupName": "EXPIRED"}, {"groupName": "REJECTED"}, {"groupName": "UNDELIVERABLE"}, {"group_name": "EXPIRED"}, {"group_name": "REJECTED"}, {"group_name": "UNDELIVERABLE"}],
                MessageStatus.SENT: [{"name": "DELIVERED_TO_OPERATOR"}],
                MessageStatus.DELIVERED: [{"name": "DELIVERED_TO_HANDSET"}],
                MessageStatus.READ: []
            }
            
            for key in API_STATUS_TO_ENUM_TABLE:
                for key_inner in API_STATUS_TO_ENUM_TABLE[key]:
                    api_resp = api_status_response.get(list(key_inner.keys())[0])
                    
                    if api_resp:
                        if api_resp.lower() == list(key_inner.values())[0].lower():
                            return key
                
        return None
    
    def from_str(string: str) -> Union["MessageStatus", None]:
        string = string.upper()
        
        if string == MessageStatus.PENDING.name: return MessageStatus.PENDING
        elif string == MessageStatus.FAILED.name: return MessageStatus.FAILED
        elif string == MessageStatus.SENT.name: return MessageStatus.SENT
        elif string == MessageStatus.DELIVERED.name: return MessageStatus.DELIVERED
        elif string == MessageStatus.READ.name: return MessageStatus.READ
        else: return None
                

# -=-=-= Models =-=-=-
class StandardMessageObject():
    message_id: str
    type: MessageType
    content: dict
    from_num_e164: str
    to_num_e164: str
    status: MessageStatus
    callback_url: str
    
    def __init__(self, message_id: str, type: MessageType, content: dict, from_num_e164: str, to_num_e164: str, status: MessageStatus, callback_url: str):
        self.message_id = message_id
        self.type = type
        self.content = content
        self.from_num_e164 = from_num_e164
        self.to_num_e164 = to_num_e164
        self.status = status 
        self.callback_url = callback_url


# -=-=-= Main utility object =-=-=-
class WhatsAppApiInterface():
    def send_freeform_message(message_obj: StandardMessageObject) -> Union[StandardMessageObject, None]:
        try:
            callback_url = url_for("handle_message_status_call", _external=True, _scheme=AppConfig.HTTP_SCHEME)
            callback_url = callback_url + f"?user={AppConfig.WAAPI_REQUEST_BASIC_AUTH_USER}&pass={AppConfig.WAAPI_REQUEST_BASIC_AUTH_PASS}"
            
            msg_id = uuid.uuid4()
            
            message = {
                "from": AppConfig.WAAPI_WHATSAPP_FROM_NUMBER.replace("+", ""),
                "to": message_obj.to_num_e164.replace("+", ""),
                "messageId": str(msg_id),
                "content": message_obj.content,
                "callbackData": "",
                "notifyUrl": callback_url
            }
            
            if message_obj.type == MessageType.TEXT:
                response = waapi.send_text_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp TEXT message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.DOCUMENT:
                response = waapi.send_document_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp DOCUMENT message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.IMAGE:
                response = waapi.send_image_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp IMAGE message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.AUDIO or message_obj.type == MessageType.VOICE:
                response = waapi.send_audio_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp AUDIO message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.VIDEO:
                response = waapi.send_video_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp VIDEO message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.STICKER:
                response = waapi.send_sticker_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp STICKER message to [{message_obj.to_num_e164}]")
                
            elif message_obj.type == MessageType.LOCATION:
                response = waapi.send_location_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp LOCATION message to [{message_obj.to_num_e164}]")
                
            # Contacts are not supported!
            # elif message_obj.type == MessageType.CONTACT:
            #     response = waapi.send_contact_message(message)
            #     debug_log.debug(f"[WhatsApp API Interface] Successfully sent a freeform WhatsApp CONTACT message to [{to_number}]")
            
            elif message_obj.type == MessageType.CONTACT:
                message["content"] = {"text": str(WA_SYSTEM_RESPONSES.MEDIA_UNSUPPORTED)}
                message["notifyUrl"] = url_for("always_200_fake_callback", _external=True, _scheme=AppConfig.HTTP_SCHEME)
                
                response = waapi.send_text_message(message)
                debug_log.debug(f"[WhatsApp API Interface] Unable to send CONTACT message as it is not supported by the system! [{message_obj.to_num_e164}]")
                
            else:
                raise Exception("Message type not supported!")
                
            return StandardMessageObject(response.message_id, message_obj.type, message_obj.content, AppConfig.WAAPI_WHATSAPP_FROM_NUMBER, message_obj.to_num_e164, MessageStatus.from_api_response(response.status.__dict__), callback_url)
            
        except Exception:
            debug_log.debug(f"[WhatsApp API Interface] An exception occured whilst trying to send a freeform WhatsApp message to [{message_obj.to_num_e164}]:", exc_info=1)
            log.error(f"[WhatsApp API Interface] An exception occured whilst trying to send a freeform WhatsApp message to [{message_obj.to_num_e164}]:", exc_info=1)
            return None
        
        
    def get_inbound_media(media_url: str) -> Union[tuple, None]:
        media_url.replace("api.infobip.com", AppConfig.WAAPI_BASE_URL)
        file = requests.get(media_url, headers={"Authorization": f"App {AppConfig.WAAPI_API_KEY}"})
        
        if file.status_code == 200:
            if type(file.content) == bytes:
                debug_log.debug(f"[WhatsApp API Interface] Successfully retrieved inbound media file. [{media_url}]")
                return (file.content, file.headers.get("Content-Type").split("/")[1])
            
        elif file.status_code == 404:
            debug_log.debug(f"[WhatsApp API Interface] Unable to retrieved inbound media file. (404 Not Found) [{media_url}]")
        
        elif file.status_code == 429:
            debug_log.debug(f"[WhatsApp API Interface] Unable to retrieved inbound media file. (429 Too Many Requests) [{media_url}]")
            
        else:
            debug_log.debug(f"[WhatsApp API Interface] Unable to retrieved inbound media file. (Error {file.status_code}) [{media_url}]")
        
        return None
    
    
    @app.route(MESSAGE_STATUS_CALLBACK, methods=["POST"])
    @authenticate_http_basic
    def handle_message_status_call():
        data = request.json
        debug_log.debug("[WhatsApp API Interface] Received status update.")
        message_objs = []
        
        for result in data.get("results"):
            message_objs.append(StandardMessageObject(result.get("messageId"), None, None, None, f'+{result.get("to")}', MessageStatus.from_api_response(result.get("status")), None))
        
        from utils.whatsapp import WhatsApp
        return WhatsApp.handle_message_status_call(message_objs)

    
    @app.route(MESSAGE_RECEIVE_CALLBACK, methods=["POST"])
    @authenticate_http_basic
    def handle_message_receive():
        data = request.json
        debug_log.debug("[WhatsApp API Interface] Received message.")
        message_objs = []
        
        for result in data.get("results"):
            message_objs.append(StandardMessageObject(result.get("messageId"), MessageType.from_str(result.get("message").get("type")), result.get("message"), f'+{result.get("from")}', f'+{result.get("to")}', "RECEIVED", None))
        
        from utils.whatsapp import WhatsApp
        return WhatsApp.handle_message_receive(message_objs)
    
    
    @app.route(ALWAYS_200_FAKE_CALLBACK, methods=["POST", "GET"])
    def always_200_fake_callback():
        return "This is fine.", 200