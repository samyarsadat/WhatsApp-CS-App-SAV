#  WhatsApp messaging client project
#  Messaging API enpoints and SocketIO event handlers
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import os
import bleach
import uuid
import secrets
from config import AppConfig
from modules.multiserver import multiserv_handle_message_change
from msg_dsp_text import WA_SYSTEM_RESPONSES
from flask import Blueprint, abort, request, url_for
from flask_security import auth_required, current_user
from modules.database import Agent, Message, PhoneNumber, RedirectRule
from init import socketio, db, debug_log
from flask_socketio import disconnect
from utils.whatsapp import WhatsApp
from utils.global_helpers import get_cid_phone_num, get_phone_num_cid, validate_e164_phone_num, get_cid_display_name, get_display_name_cid
from utils.whatsapp_interface import MessageStatus, MessageType


# ------- Blueprint init -------
messaging = Blueprint("messaging", __name__, template_folder="../templates", static_folder="../static")


# ------- Global variables -------
API_PREFIX = AppConfig.MESSAGING_API_PREFIX


# ------- Functions -------
def ext_allowed(filename):
    return ("." in filename) and (filename.rsplit(".", 1)[1].lower() in AppConfig.ALLOWED_FILE_EXTENSIONS)


# ---- This function handles WhatsApp phone message redirects ----
def whatsapp_redirect(client_number: str, msg_obj: Message) -> bool:
    customer_id = get_cid_phone_num(client_number)
    redirect_rules = RedirectRule.query.filter_by(phone_number=client_number).all()
    agent = Agent.query.filter_by(phone_number=client_number).first()
    fs_user_rule = False
    
    for rule in redirect_rules:
        agent = Agent.query.get(rule.agent_id)
            
        if agent.type == "fs_user":
            fs_user_rule = True
                
        if agent.type == "phone":
            debug_log.debug(f"Received message has phone redirect rule. Redirecting message to agent via WhatsApp. {[client_number, agent.name]}") 
            
            pn_database = PhoneNumber.query.filter_by(number=client_number).first()
            
            if pn_database:
                pn_database.unread_msgs = pn_database.unread_msgs - 1
                db.session.commit()
            
            if msg_obj.type.lower() == "text":
                body = msg_obj.content.get("text")
                msg_obj.content["text"] = f"*{get_display_name_cid(customer_id).title()}*" + (":\n" + body if body else "")
                WhatsApp.send_freeform_message(msg_obj.content, MessageType.from_str(msg_obj.type), agent.phone_number, True, client_number)
                
            elif msg_obj.type.lower() in ["image", "video"]:
                body = msg_obj.content.get("caption")
                msg_obj.content["caption"] = f"*{get_display_name_cid(customer_id).title()}*" + (":\n" + body if body else "")
                WhatsApp.send_freeform_message(msg_obj.content, MessageType.from_str(msg_obj.type), agent.phone_number, True, client_number)
                
            elif msg_obj.type.lower() in ["audio", "voice", "location", "sticker", "document"]: 
                WhatsApp.send_freeform_message({"text": f"*{get_display_name_cid(customer_id).title()}*:"}, MessageType.TEXT, agent.phone_number, True, client_number)
                WhatsApp.send_freeform_message(msg_obj.content, MessageType.from_str(msg_obj.type), agent.phone_number, True, client_number)
                
    if agent and agent.phone_number == client_number:
        redirect_rules = RedirectRule.query.filter_by(agent_id=agent.id).all()
        agent_single_customer = False
        agent_no_customers = False
        media_unsupported = False
        body = ""
            
        if len(redirect_rules) == 0:
            agent_no_customers = True
            debug_log.debug(f"Received message from phone agent however the agent has no assigned customers. {[client_number, agent.name, customer_id]}")
            WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.AGENT_NO_CUSTOMERS)}, MessageType.TEXT, client_number, True, None)
                
        elif len(redirect_rules) == 1:
            agent_single_customer = True
            display_name = get_display_name_cid(get_cid_phone_num(redirect_rules[0].phone_number)) 
                
        else:
            if msg_obj.type.lower() == "text":
                body = msg_obj.content.get("text")
            
            elif msg_obj.type.lower() in ["document", "image", "video"]:
                body = msg_obj.content.get("caption")
                
            elif msg_obj.type.lower() in ["audio", "voice", "location", "sticker", "contact"]:
                media_unsupported = True
            
            display_name = body.split("\n")[0].lower().strip() if body else None
        
        if not agent_no_customers:
            if not media_unsupported:
                cid = get_cid_display_name(display_name)
                
                if display_name and cid:
                    phone_num = get_phone_num_cid(cid)
                        
                    if validate_e164_phone_num(phone_num):
                        redirect_rules = RedirectRule.query.filter_by(phone_number=phone_num).all()
                        msg_sent = False
                        body_send = body
                            
                        if not agent_single_customer:
                            body_send = body.split("\n")
                            del body_send[0]
                            body_send = "\n".join(body_send)
                                    
                            if msg_obj.type.lower() == "text":
                                msg_obj.content["text"] = body_send
                                    
                            elif msg_obj.type.lower() in ["document", "image", "video"]:
                                msg_obj.content["caption"] = body_send
                        
                        for rule in redirect_rules:
                            r_agent = Agent.query.get(rule.agent_id)
                                
                            if (agent.id == r_agent.id) and (("\n" in body) or msg_obj.type.lower() in ["document", "image", "audio", "voice", "video", "sticker"] or agent_single_customer):
                                debug_log.debug(f"Received message from phone agent. Redirecting message to client via WhatsApp. {[client_number, agent.name, phone_num, customer_id]}")
                                WhatsApp.send_freeform_message(msg_obj.content, MessageType.from_str(msg_obj.type), phone_num, True, client_number)
                                msg_sent = True 
                                    
                        if not msg_sent:
                            debug_log.debug(f"Received message from phone agent however the client the message is addressed to does not belong to agent. {[client_number, agent.name, phone_num, customer_id]}")
                            WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.CLIENT_NOT_BELONG)}, MessageType.TEXT, client_number, True, None)
                                
                    else:
                        debug_log.debug(f"Received message from phone agent however the Customer ID is invalid. {[client_number, agent.name, phone_num, customer_id]}")
                        WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.INVALID_RESPONSE_CUSTOMER_ID)}, MessageType.TEXT, client_number, True, None)
                        
                else:
                    debug_log.debug(f"Received message from phone agent however the Customer ID is invalid. {[client_number, agent.name, customer_id]}")
                    WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.INVALID_RESPONSE_CUSTOMER_ID)}, MessageType.TEXT, client_number, True, None)
                    
            else:
                debug_log.debug(f"Received message from phone agent however the media is unsupported. {[client_number, agent.name, customer_id]}")
                WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.MEDIA_UNSUPPORTED)}, MessageType.TEXT, client_number, True, None)
            
    return fs_user_rule


# ---- This function handles message reidrect status responses ----
def msg_redirect_status_resp(msg_obj: Message, status: MessageStatus):
    if msg_obj.origin_phone_number:
        if status == MessageStatus.FAILED:
            debug_log.debug(f"Received message status update for a message with an origin number and the message send has failed. Informing origin number. {[msg_obj.origin_phone_number, msg_obj.client_number]}")
            WhatsApp.send_freeform_message({"text": str(WA_SYSTEM_RESPONSES.ORIGIN_MESSAGE_RESEND_FAILED)}, MessageType.TEXT, msg_obj.origin_phone_number, True, None)


# ---- This function is called whenever a message is sent, received or a message's status is updated ----
def message_status_change(client_number: str, change: str, msg_db_id: int, msg_obj: Message):
    fs_user_send = False
    
    if change == "msg_received":
        fs_user_send = whatsapp_redirect(client_number, msg_obj)
            
    debug_log.debug(f"[SocketIO] Emitting message update event! {[client_number, change, msg_db_id]}")
    multiserv_handle_message_change(change)
    socketio.emit("message_change", {"client_number": client_number, "change": change, "msg_db_id": msg_db_id})


# ------- API routes -------
@messaging.route(API_PREFIX + "/get_message_list/<customer_id>")
@auth_required("session")
def get_msg_list(customer_id):
    phone_number = get_phone_num_cid(bleach.clean(customer_id))
    
    if phone_number:
        user_id = current_user.id 
        agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
        redirect_rules = db.session.query(RedirectRule).filter_by(phone_number=phone_number).all()
        rule_avail = False
        
        for rule in redirect_rules:
            if agent and rule.agent_id == agent.id:
                rule_avail = True
                
        if rule_avail or current_user.has_role("admin"):
            msg_list = Message.query.filter_by(client_number=phone_number).all()
            msg_list_dict = []
            
            if msg_list:
                for msg in msg_list:
                    delattr(msg, "_sa_instance_state")
        
                    msg_dict = msg.__dict__
                    msg_dict.pop("client_number", None)
                    msg_dict.pop("origin_phone_number", None)
                    msg_dict.pop("sid", None)
                    
                    msg_list_dict.append(msg_dict)
            
            ret = sorted(msg_list_dict, key=lambda d: d.get("datetime", float("inf")), reverse=False)
            return ret, 200
    
    debug_log.debug(f"[{request.remote_addr}] Attempted to request messages list for a number that is not in their redirects list. [{phone_number}]")
    abort(404)
    
    
@messaging.route(API_PREFIX + "/get_phones_list")
@auth_required("session")
def get_pns_list():
    user_id = current_user.id 
    agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
    redirect_rules = []
    
    if agent:
        redirect_rules = db.session.query(RedirectRule).filter_by(agent_id=agent.id).all()
    
    phone_nums_belong = []
    
    if current_user.has_role("admin"):
        phones = PhoneNumber.query.all()
        
        for num in phones:
            if not Agent.query.filter_by(phone_number=num.number).first():
                delattr(num, "_sa_instance_state")
                
                num = num.__dict__
                num["display_name"] = num.get("display_name").title()
                phone_nums_belong.append(num)
        
    else:
        for rule in redirect_rules:
            phone_num = PhoneNumber.query.filter_by(number=rule.phone_number).first()
            
            if phone_num:
                if not Agent.query.filter_by(phone_number=phone_num.number).first():
                    delattr(phone_num, "_sa_instance_state")
                    
                    phone_num = phone_num.__dict__
                    phone_num["display_name"] = phone_num.get("display_name").title()
                    phone_num.pop("number", None)
                    phone_nums_belong.append(phone_num)
            
    ret = sorted(phone_nums_belong, key=lambda d: d.get("unread_msgs", float("inf")), reverse=True)
    return ret, 200
    
    
@messaging.route(API_PREFIX + "/get_message_db_id/<id>")
@auth_required("session")
def get_msg_db_id(id):
    id = int(id)
    msg = Message.query.get(id)
    
    if msg:
        phone_number = msg.client_number
        
        if phone_number:
            user_id = current_user.id 
            agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
            redirect_rules = db.session.query(RedirectRule).filter_by(phone_number=phone_number).all()
            rule_avail = False
            
            for rule in redirect_rules:
                if agent and rule.agent_id == agent.id:
                    rule_avail = True
                    
            if rule_avail or current_user.has_role("admin"):
                delattr(msg, "_sa_instance_state")
                    
                msg_dict = msg.__dict__
                msg_dict.pop("client_number", None)
                msg_dict.pop("origin_phone_number", None)
                msg_dict.pop("sid", None)
                        
                return msg_dict, 200
    
    debug_log.debug(f"[{request.remote_addr}] Attempted to request messages from a number that is not in their redirects list or provided db id is invalid. [{id}]")
    abort(404)


@messaging.route(API_PREFIX + "/upload_files", methods=["POST", "GET"])
@auth_required("session")
def handle_file_upload():
    files = request.files.getlist("files")
    file_urls = []
    
    try:
        if files[0].filename:
            folder_uuid = secrets.token_urlsafe()
            path = os.path.join(AppConfig.UPLOAD_FOLDER, f"message_media/{folder_uuid}")
            os.mkdir(path)
        
        for file in files:
            if file.filename != "":
                if ext_allowed(file.filename):
                    file_uuid = uuid.uuid4()
                    file.save(os.path.join(path, f"{file_uuid}.{file.filename.rsplit('.', 1)[1]}"))
                    file_urls.append(url_for("static", filename=f"{AppConfig.UPLOAD_FOLDER_STATIC_RELATIVE}/message_media/{folder_uuid}/{file_uuid}.{file.filename.rsplit('.', 1)[1]}", _external=True, _scheme=AppConfig.HTTP_SCHEME))
                    
        debug_log.debug(f"File upload for messages successful. Saved {len(files)} file(s).")
                    
    except Exception:
        debug_log.debug(f"Failed to save uploaded files for message!", exc_info=1)
        abort(500)
        
    return {"files": file_urls}, 200


# ------- SocketIO -------
@socketio.on("disconnect")
def handle_socket_connect():
    debug_log.debug(f"[SocketIO] [{request.remote_addr}] Disconnected.")


@socketio.on("connect")
def handle_socket_connect():
    debug_log.debug(f"[SocketIO] Received [connect] event from [{request.remote_addr}]")
    
    if not current_user.is_authenticated:
        debug_log.debug("[SocketIO] Connection attempt from unathenticated user, disconnecting.")
        disconnect()


@socketio.on("user_client_connect")
@auth_required("session")
def handle_client_connect(json: dict):
    print("User Connect Event: " + str(json))
    
    phone_number = get_phone_num_cid(bleach.clean(json.get("customer_id")))
    debug_log.debug(f"[SocketIO] Received [user_client_connect] event from [{request.remote_addr}] - [{phone_number}]")
    
    if phone_number:
        if current_user.has_role("admin") or phone_number == "NO_CHAT_PAGE":
            return
        
        user_id = current_user.id 
        agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
        redirect_rules = db.session.query(RedirectRule).filter_by(phone_number=phone_number).all()
        
        for rule in redirect_rules:
            if agent and rule.agent_id == agent.id:
                return
    
        debug_log.debug(f"[SocketIO] Connection attempt from a user who doesn't have the requested phone number in their redirects list, disconnecting. [{phone_number}]")
    disconnect()


@socketio.on("client_msg_send")
@auth_required("session")
def handle_client_msg_receive(json: dict, methods=["GET", "POST"]):
    print("Receive Client Message: " + str(json))
    debug_log.debug(f"[SocketIO] Received [client_msg_send] event from [{request.remote_addr}]")
    
    phone_number = get_phone_num_cid(bleach.clean(json.get("customer_id")))
    message = bleach.clean(json.get("message"))
    files = json.get("files")
    
    if phone_number and (message or files):
        user_id = current_user.id 
        agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
        redirect_rules = db.session.query(RedirectRule).filter_by(phone_number=phone_number).all()
        rule_avail = False
        
        for rule in redirect_rules:
            if agent and rule.agent_id == agent.id:
                rule_avail = True
                
        if rule_avail or current_user.has_role("admin"):
            if files:
                for i, file in enumerate(files):
                    file_ext = file.split(".")
                    file_ext.reverse()
                    file_ext = file_ext[0]
                    send_text = True if (i == 0 and message) else False
                    
                    if file_ext in AppConfig.FILE_MSG_TYPE_TABLE["audio"]:
                        WhatsApp.send_freeform_message({"text": message}, MessageType.TEXT, phone_number, False, None) if send_text else None
                        WhatsApp.send_freeform_message({"mediaUrl": file}, MessageType.AUDIO, phone_number, False, None)
                    
                    elif file_ext in AppConfig.FILE_MSG_TYPE_TABLE["image"]:
                        if send_text:
                            WhatsApp.send_freeform_message({"mediaUrl": file, "caption": message}, MessageType.IMAGE, phone_number, False, None)
                            
                        else:
                            WhatsApp.send_freeform_message({"mediaUrl": file}, MessageType.IMAGE, phone_number, False, None)
                    
                    elif file_ext in AppConfig.FILE_MSG_TYPE_TABLE["video"]:
                        if send_text:
                            WhatsApp.send_freeform_message({"mediaUrl": file, "caption": message}, MessageType.VIDEO, phone_number, False, None)
                            
                        else:
                            WhatsApp.send_freeform_message({"mediaUrl": file}, MessageType.VIDEO, phone_number, False, None)
                    
                    elif file_ext in AppConfig.FILE_MSG_TYPE_TABLE["sticker"]:
                        WhatsApp.send_freeform_message({"text": message}, MessageType.TEXT, phone_number, False, None) if send_text else None
                        WhatsApp.send_freeform_message({"mediaUrl": file}, MessageType.STICKER, phone_number, False, None)
                    
                    else:
                        WhatsApp.send_freeform_message({"text": message}, MessageType.TEXT, phone_number, False, None) if send_text else None
                        WhatsApp.send_freeform_message({"mediaUrl": file}, MessageType.DOCUMENT, phone_number, False, None)
                
                return
            
            else:
                WhatsApp.send_freeform_message({"text": message}, MessageType.TEXT, phone_number, False, None) if message else None
                return
        
        debug_log.debug(f"[{request.remote_addr}] Attempted to send a message to a number that is not in their redirects list, disconnecting. [{phone_number}]")
    disconnect()