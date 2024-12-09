#  WhatsApp messaging client project
#  Global helper functions file
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import os
import phonenumbers
from modules.database import PhoneNumber
from init import debug_log
from typing import Union


# ------- Functions -------
# ---- Validates an E.164 formatted phone number ----
def validate_e164_phone_num(phone_number: str) -> bool:          
    try:
        phone_number = phonenumbers.parse(phone_number, None)
                    
        if phonenumbers.is_possible_number(phone_number) and phonenumbers.is_valid_number(phone_number):
            return True
                    
    except Exception:
        pass
    
    return False


# ---- Gets a PhoneNumber database entry's customer ID based on an E.164 formatted phone number ----
def get_cid_phone_num(phone_number: str) -> Union[str, None]:
    if phone_number == "NO_CHAT_PAGE":
        return "NO_CHAT_PAGE"
    
    query = PhoneNumber.query.filter_by(number=phone_number).first()
    
    if query:
        return query.customer_id
    
    return None


# ---- Gets a PhoneNumber database entry's phone number based on a customer ID ----
def get_phone_num_cid(customer_id: str) -> Union[str, None]:
    if customer_id == "NO_CHAT_PAGE":
        return "NO_CHAT_PAGE"
    
    query = PhoneNumber.query.filter_by(customer_id=customer_id.capitalize()).first()
    
    if query:
        return query.number
    
    return None


# ---- Gets a PhoneNumber database entry's display name based on a customer ID ----
def get_display_name_cid(customer_id: str) -> Union[str, None]:
    if customer_id == "NO_CHAT_PAGE":
        return "NO_CHAT_PAGE"
    
    query = PhoneNumber.query.filter_by(customer_id=customer_id.capitalize()).first()
    
    if query:
        return query.display_name
    
    return None


# ---- Gets a PhoneNumber database entry's customer ID based on a display name ----
def get_cid_display_name(display_name: str) -> Union[str, None]:
    if display_name == "NO_CHAT_PAGE":
        return "NO_CHAT_PAGE"
    
    query = PhoneNumber.query.filter_by(display_name=display_name).first()
    
    if query:
        return query.customer_id
    
    return None


# ---- Saves a file at the provided path with the provided binary data in it ----
def save_binary_file(dir_path: str, filename: str, data: bytes) -> bool:
    full_path = os.path.join(dir_path, filename)
    
    try:
        with open(full_path, "xb") as file:
            file.write(data)
            file.close()
            
        debug_log.debug("[Binary File Saving Util] Wrote binary file successfully.")
        return True
            
    except Exception:
        debug_log.debug("[Binary File Saving Util] Unable to write binary file!", exc_info=1)
        return False