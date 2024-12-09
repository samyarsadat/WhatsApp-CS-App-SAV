#  WhatsApp messaging client project
#  WhatsApp API utility (uses whatsapp_interface.py)
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import os
from init import log, debug_log, db
from typing import Union
from config import AppConfig
from flask import abort, url_for
from modules.database import Message, RedirectRule, Agent, PhoneNumber, AnnouncementMessage
from datetime import datetime
from utils.whatsapp_interface import WhatsAppApiInterface, StandardMessageObject, MessageType
from utils.global_helpers import save_binary_file
from msg_dsp_text import SYSTEM_ANNOUNCEMENT_MESSAGES


# -=-=-= Functions =-=-=-
def get_agents_responsible(phone_number: str) -> list:
    redirect_rules = db.session.query(RedirectRule).filter_by(phone_number=phone_number).all()
    agents_resp = []
            
    if redirect_rules:
        for rule in redirect_rules:
            agent = db.session.query(Agent).filter_by(id=rule.agent_id).first()
                    
            if agent:
                agents_resp.append(agent.name)
                
    return agents_resp


def generate_customer_id() -> str:
    time = datetime.now()
    date_formatted = time.strftime("%d%m%Y")
    phone_numbers = PhoneNumber.query.all()
    highest_number = 0
    
    for i in range(20):
        for number in phone_numbers:
            cid_split = number.customer_id.split("-")
            
            if cid_split[1] == date_formatted:
                if int(cid_split[2]) > highest_number:
                    highest_number = int(cid_split[2])
                    
        msg_to_db = AnnouncementMessage(message=str(SYSTEM_ANNOUNCEMENT_MESSAGES.CUSTOMERS_PER_DAY_LIMIT_REACHED), level="danger", start_time=datetime.now(), duration="inf")
        msg_query = AnnouncementMessage.query.filter_by(message=msg_to_db.message).first()
              
        if highest_number >= AppConfig.MAX_CUSTOMERS_PER_DAY:
            if not msg_query:
                db.session.add(msg_to_db)
                db.session.commit()
            
            log.warning("Maximum number of customers per day reached! Please contact system administrator!")
            abort(423)
            
        if msg_query:
            db.session.delete(msg_query)
            db.session.commit()
                
        cid = AppConfig.CUSTOMER_ID_FORMAT.format(date=date_formatted, day_id=int(highest_number) + 1)
        query = PhoneNumber.query.filter_by(customer_id=cid).first()
        
        if not query:
            return cid
        
    abort(500)


# -=-=-= Main utility object =-=-=-
class WhatsApp():
    def send_freeform_message(content: dict, type: MessageType, to_number: str, is_redirect: bool, origin_phone_number: Union[str, None]) -> Union[any, None]:
        try:
            agents_resp = get_agents_responsible(to_number)
            agents_resp_dict = {}
            
            for id, agent in enumerate(agents_resp):
                agents_resp_dict.update({id: agent})
                
            now = datetime.now()
                
            message = WhatsAppApiInterface.send_freeform_message(StandardMessageObject(None, type, content, None, to_number, None, None))
            msg = Message(sid=message.message_id, direction=1, client_number=to_number, agents_resp=agents_resp_dict, origin_phone_number=origin_phone_number, datetime=now, status=message.status.name, content=content, type=type.name, is_redirect=is_redirect)
            
            db.session.add(msg)
            db.session.commit()
            
            debug_log.debug(f"[WhatsApp API] Sent freeform WhatsApp message to [{to_number}] successfully.")
            
            msg = Message.query.filter_by(sid=message.message_id).first()
            from modules.messaging import message_status_change
            message_status_change(to_number, "msg_sent", msg.id, msg)
            
            return message
            
        except Exception:
            debug_log.debug(f"[WhatsApp API] An exception occured whilst trying to send a freeform WhatsApp message to [{to_number}]:", exc_info=1)
            log.error(f"[WhatsApp API] An exception occured whilst trying to send a freeform WhatsApp message to [{to_number}]:", exc_info=1)
            return None
    

    def handle_message_status_call(results: list[StandardMessageObject]):
        for result in results:
            if result.status:
                msg = Message.query.filter_by(sid=result.message_id).first()
                
                if msg:
                    msg.status = result.status.name
                    db.session.commit()
                    debug_log.debug("[WhatsApp API] Received status update and wrote update to database successfuly.")
                
                    from modules.messaging import message_status_change, msg_redirect_status_resp
                    message_status_change(msg.client_number, "msg_stat_update", msg.id, msg)
                    msg_redirect_status_resp(msg, result.status)
                
                else:
                    debug_log.debug("[WhatsApp API] Received status update however the message which this status update is for does not exist!")
        
        return "OK", 200
    
    
    def handle_message_receive(results: list[StandardMessageObject]):
        for result in results:
            sid = result.message_id
            
            if not Message.query.filter_by(sid=sid).first():
                now = datetime.now()
                from_num = result.from_num_e164
                message = result.content
                    
                agents_resp = get_agents_responsible(from_num)
                agents_resp_dict = {}
                    
                for id, agent in enumerate(agents_resp):
                    agents_resp_dict.update({id: agent})
                    
                msg_type_name = result.type.name.lower()
                    
                if msg_type_name in ["document", "image", "audio", "voice", "video", "sticker"]:
                    media_file = WhatsAppApiInterface.get_inbound_media(message.get("url"))
                    
                    if media_file:
                        media_file_path = os.path.join(AppConfig.UPLOAD_FOLDER, "inbound_message_media")
                        media_file_name = message.get("url").split("/")
                        media_file_name.reverse()
                        media_file_name = f"{media_file_name[0]}_{media_file_name[2]}.{media_file[1]}"
                        
                        if save_binary_file(media_file_path, media_file_name, media_file[0]):
                            media_link = url_for("static", filename=f"{AppConfig.UPLOAD_FOLDER_STATIC_RELATIVE}/inbound_message_media/{media_file_name}", _external=True, _scheme=AppConfig.HTTP_SCHEME)
                            
                            if message.get("caption"):
                                content = {"mediaUrl": media_link, "caption": message.get("caption")}
                                
                            else:
                                content = {"mediaUrl": media_link}
                                
                            body_db = "Media File(s)"
                            
                        else:
                            content = {"text": "System Error: Media Download Failure"}
                            body_db = "System Error: Media Download Failure"
                            result.type = MessageType.TEXT
                        
                    else:
                        content = {"text": "System Error: Media Download Failure"}
                        body_db = "System Error: Media Download Failure"
                        result.type = MessageType.TEXT
                    
                elif msg_type_name == "text":
                    body_db = message.get("text")
                    content = {"text": message.get("text")}
                    
                elif msg_type_name == "location":
                    body_db = "Location"
                    content = {"longitude": message.get("longitude"), "latitude": message.get("latitude"), "name": message.get("name"), "address": message.get("address")}
                    
                else:
                    WhatsAppApiInterface.send_freeform_message(StandardMessageObject(None, MessageType.CONTACT, {}, None, from_num, None, None))  # To send an error message (MEDIA_UNSUPPORTED)
                    return "This is fine.", 200
                
                msg = Message(sid=sid, direction=0, client_number=from_num, agents_resp=agents_resp_dict, origin_phone_number=None, datetime=now, status=result.status, content=content, type=result.type.name, is_redirect=False)
                agent = db.session.query(Agent).filter_by(phone_number=msg.client_number).first()
                
                pn_database = PhoneNumber.query.filter_by(number=msg.client_number).first()
                    
                if not pn_database:
                    cid = generate_customer_id()
                    pn_database = PhoneNumber(unread_msgs=1, last_msg=body_db, number=msg.client_number, customer_id=cid, display_name=cid)
                    db.session.add(pn_database)
                    
                else:
                    pn_database.unread_msgs = pn_database.unread_msgs + 1
                    pn_database.last_msg = body_db
                
                db.session.add(msg)
                db.session.commit()
                
                debug_log.debug("[WhatsApp API] Received message and wrote message to database successfuly.")
                
                msg = Message.query.filter_by(sid=sid).first()
                from modules.messaging import message_status_change
                message_status_change(msg.client_number, "msg_received", msg.id, msg)
                
            else:
                debug_log.debug("[WhatsApp API] Received message but the SID is not unique.")
            
        return "OK", 200