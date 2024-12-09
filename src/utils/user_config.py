#  WhatsApp messaging client project
#  User config JSON file utility
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import json
import os
# from init import log   Cannot import the logger as it causes cricular import.
from dataclasses import dataclass
from dotenv import dotenv_values, set_key, load_dotenv


# ------- Global variables -------
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRETS_ENV_FILE = os.path.join(FILE_DIR, "../secrets/user_vars.env")
USER_CONFIG_FILE_PATH = os.path.join(FILE_DIR, "../user_config.json")   # Cannot get these from config.py as it causes circular import.


# ------- Storage model -------
@dataclass
class UserConfigFile():
    SERVER_NAME: str
    SECURITY_EMAIL_SENDER_NAME: str
    SECURITY_EMAIL_SENDER: str
    WAAPI_WHATSAPP_FROM_NUMBER: str
    WAAPI_REQUEST_BASIC_AUTH_USER: str
    WAAPI_REQUEST_BASIC_AUTH_PASS_HASH: str
    ALLOWED_FILE_EXTENSIONS: list
    ANALYTICS_TAG_ID: str
    ANALYTICS_PROPERTY_ID: str
    MAX_FILE_UPLOAD_SIZE_MB: int
    SUPPORTED_LANGS: list
    DEFAULT_LANG: str
    MAX_AGENTS_PER_CUSTOMER: int
    MAX_CUSTOMERS_PER_DAY: int
    MULTISERVER_SERVERS_LIST: dict
    
    
    # ---- Read config file ----
    def read() -> "UserConfigFile":
        try:
            with open(USER_CONFIG_FILE_PATH, "r") as file:
                data = json.load(file)

            to_send = UserConfigFile(**data)
            return to_send

        except Exception:
            # log.exception("UserConfigReadException")
            return False
    
    
    # ---- Write to (update) config file ----
    def write(self) -> bool:
        json_data = self.__dict__

        try:
            with open(USER_CONFIG_FILE_PATH, "r") as file:
                data = json.load(file)

            data.update(json_data)

            with open(USER_CONFIG_FILE_PATH, "w") as file:
                json.dump(data, file, indent=4)
                
            return True

        except Exception:
            # log.exception("UserConfigWriteException")
            return False
        
        
@dataclass
class SecretVarsFile():
    MAILJET_API_KEY: str
    MAILJET_API_SECRET: str
    WAAPI_BASE_URL: str
    WAAPI_API_KEY: str
    WAAPI_REQUEST_PASSWORD: str
    ENABLE_MAINTENANCE: str
    
    
    # ---- Read config file ----
    def read() -> "SecretVarsFile":
        try:
            data = dotenv_values(SECRETS_ENV_FILE)
            to_send = SecretVarsFile(**data)
            return to_send

        except Exception:
            # log.exception("SecretVarsFileReadException")
            return False
    
    
    # ---- Write to (update) config file ----
    def write(self) -> bool:
        json_data = self.__dict__

        try:
            data = dotenv_values(SECRETS_ENV_FILE)
            data.update(json_data)

            for field in data:
                set_key(SECRETS_ENV_FILE, field, data[field])
                
            load_dotenv(SECRETS_ENV_FILE, override=True)
            return True

        except Exception:
            # log.exception("SecretVarsFileWriteException")
            return False