#  WhatsApp messaging client project
#  Program configuration file
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023



# ------- Libraries -------
import logging
import os
import pkg_resources
from dotenv import load_dotenv
from utils.user_config import UserConfigFile, SecretVarsFile


# ------- Global variables -------
WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(WORKING_DIR, "instance")
SECRETS_ENV_FILE = os.path.join(WORKING_DIR, "secrets/vars.env")
USER_SECRETS_ENV_FILE = os.path.join(WORKING_DIR, "secrets/user_vars.env")
GA_SECRET_CREDS_FILE = os.path.join(WORKING_DIR, "secrets/ga_creds.json")


# ------- Load environment variables -------
load_dotenv(SECRETS_ENV_FILE, override=True)
load_dotenv(USER_SECRETS_ENV_FILE, override=True)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GA_SECRET_CREDS_FILE


# ------- Config classes -------
class ProductionConfig():
    USER_CONFIG_FILE = UserConfigFile.read()
    
    # ------- Flask config -------
    SERVER_NAME = USER_CONFIG_FILE.SERVER_NAME
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    DEBUG = False

    # ------- Flask-Caching config -------
    CACHE_DEFAULT_TIMEOUT = 2*60
    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = "__pycache__/FLASK_CACHE"

    # ------- Flask-SQLAlchemy config -------
    SQLALCHEMY_DATABASE_URI = "sqlite:///data/database/main.sqlite3"
    SQLALCHEMY_BINDS = {
        "accounts": "sqlite:///data/database/account.sqlite3",
        "messages": "sqlite:///data/database/messages.sqlite3",
        "agents": "sqlite:///data/database/agents.sqlite3"}
    
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # "client_encoding": "utf8"
    }

    # ------- Flask-Security config -------
    SECURITY_PASSWORD_SALT = os.getenv("PASSWORD_ENCRYPT_SALT")
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = "zxcvbn"
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_BREACHED_COUNT = 2
    SECURITY_REDIRECT_ALLOW_SUBDOMAINS = True
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = False
    SECURITY_I18N_DIRNAME = ["translations", pkg_resources.resource_filename("flask_security", "translations")]
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_RESET_PASSWORD_WITHIN = "2 days"
    SECURITY_TRACKABLE = True
    SECURITY_EMAIL_SENDER = USER_CONFIG_FILE.SECURITY_EMAIL_SENDER
    SECURITY_EMAIL_SENDER_NAME = USER_CONFIG_FILE.SECURITY_EMAIL_SENDER_NAME

    # ------- Mailjet config -------
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
    
    # ------- WhatsApp API config -------
    WAAPI_API_KEY = os.getenv("WAAPI_API_KEY")
    WAAPI_BASE_URL = os.getenv("WAAPI_BASE_URL")
    WAAPI_WHATSAPP_FROM_NUMBER = USER_CONFIG_FILE.WAAPI_WHATSAPP_FROM_NUMBER
    WAAPI_REQUEST_BASIC_AUTH_USER = USER_CONFIG_FILE.WAAPI_REQUEST_BASIC_AUTH_USER
    WAAPI_REQUEST_BASIC_AUTH_PASS_HASH = USER_CONFIG_FILE.WAAPI_REQUEST_BASIC_AUTH_PASS_HASH
    WAAPI_REQUEST_BASIC_AUTH_PASS = os.getenv("WAAPI_REQUEST_PASSWORD")

    # ------- Flask-WTF config -------
    WTF_CSRF_CHECK_DEFAULT = False
    
    # ------- Flask-Admin config -------
    FLASK_ADMIN_SWATCH = "cerulean"

    # ------- Module configs -------
    HTTP_SCHEME = "https"
    ADMIN_USER_DEFAULT_PASS = "kP28cDwx5Xm8*$a"
    ADMIN_USER_DEFAULT_USER = "administrator"
    ADMIN_USER_DEFAULT_MAIL = "defaultwhatsappadmin@gigawhat.net"
    DEV_USER_DEFAULT_PASS = "devUserPass1387"
    DEV_USER_DEFAULT_USER = "developer"
    DEV_USER_DEFAULT_MAIL = "whatsappclientdevacc@gigawhat.net"
    USER_CONFIG_FILE_PATH = os.path.join(WORKING_DIR, "user_config.json")
    ADMIN_MANAGE_URL_PREFIX = "/manage"
    MESSAGING_API_PREFIX = "/api/messaging"
    WAAPI_URL_PREFIX = "/api/waapi"
    MULTISERVER_API_PREFIX = "/api/multiserver"
    LOG_FILE_PATH = os.path.join(INSTANCE_DIR, "logs")
    LOG_LEVEL = logging.INFO
    ENABLE_ANALYTICS = False
    ANALYTICS_TAG_ID = USER_CONFIG_FILE.ANALYTICS_TAG_ID
    ANALYTICS_PROPERTY_ID = USER_CONFIG_FILE.ANALYTICS_PROPERTY_ID
    TEMPORARY_FILE_DIR = os.path.join(INSTANCE_DIR, "data/temporary")
    RENDER_CACHE_TIMEOUT = CACHE_DEFAULT_TIMEOUT
    STATIC_FOLDER_ABS_PATH = os.path.join(WORKING_DIR, "static")
    UPLOAD_FOLDER_STATIC_RELATIVE = "user-uploaded"
    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER_ABS_PATH, UPLOAD_FOLDER_STATIC_RELATIVE)
    ALLOWED_FILE_EXTENSIONS = USER_CONFIG_FILE.ALLOWED_FILE_EXTENSIONS
    MAX_CONTENT_LENGTH = USER_CONFIG_FILE.MAX_FILE_UPLOAD_SIZE_MB * 1000 * 1000
    CUSTOMER_ID_FORMAT = "Customer-{date}-{day_id}"
    SUPPORTED_LANGS = USER_CONFIG_FILE.SUPPORTED_LANGS
    DEFAULT_LANG = USER_CONFIG_FILE.DEFAULT_LANG
    MAX_AGENTS_PER_CUSTOMER = USER_CONFIG_FILE.MAX_AGENTS_PER_CUSTOMER
    MAX_CUSTOMERS_PER_DAY = USER_CONFIG_FILE.MAX_CUSTOMERS_PER_DAY
    MULTISERVER_SERVERS_LIST = USER_CONFIG_FILE.MULTISERVER_SERVERS_LIST
    FILE_MSG_TYPE_TABLE = {
        "image": ["jpg", "jpeg", "png"],
        "audio": ["aac", "amr", "mp3", "opus"],
        "video": ["mp4", "3gpp"],
        "sticker": ["webp"]
    }
    
    # ------- Form configs -------
    ADD_ANNOUNCEMENT_MESSAGE_FORM_LEVEL_OPTS = [("info", "Info"), ("success", "Success"), ("warning", "Warning"), ("danger", "Danger")]
    ADD_ANNOUNCEMENT_MESSAGE_FORM_DURATION_OPTS = [("inf", "Infinite"), ("30-mt", "30 Minutes"), ("12-hr", "12 Hours"), ("24-hr", "24 Hours"), ("48-hr", "48 Hours"), ("1-wk", "1 Week"), ("2-wk", "2 Weeks")]
    ADD_AGENT_FORM_TYPE_OPTS = [("phone", "WhatsApp Numara Ajanı"), ("fs_user", "Web Arayüz Ajanı")]
    
    @classmethod
    def update_user_settings(self):
        new_user_configs = UserConfigFile.read().__dict__
        new_secret_configs = SecretVarsFile.read().__dict__
        
        for config in new_user_configs:
            setattr(self, config, new_user_configs.get(config))
            
        for config in new_secret_configs:
            setattr(self, config, os.getenv(config))


class TestingConfig(ProductionConfig):
    pass


class LocalConfig(ProductionConfig):
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:samyar4100@localhost:5432/whatsapp_client"
    # SQLALCHEMY_BINDS = {
    #     "accounts": "postgresql://postgres:samyar4100@localhost:5432/whatsapp_client",
    #     "messages": "postgresql://postgres:samyar4100@localhost:5432/whatsapp_client",
    #     "agents": "postgresql://postgres:samyar4100@localhost:5432/whatsapp_client"}
    
    CACHE_DEFAULT_TIMEOUT = 1
    RENDER_CACHE_TIMEOUT = 1
    SERVER_NAME = "optimum-socially-collie.ngrok-free.app"
    HTTP_SCHEME = "https"
    DEBUG = True
    ENABLE_ANALYTICS = False


class AppConfig(ProductionConfig):
    # ------- Website config -------
    PROGRAM_VERSION = "v1.2.6"
    WEBSITE_DISPLAY_NAME = "WACSA"
    WEBSITE_NAV_LOGO = "img/logos/test_logo.png"
    WEBSITE_FOOTER_LOGO = "img/logos/test_logo.png"
    WEBSITE_FAVICON = "img/logos/test_logo.svg"
    
    # ------- Flask-Security config -------
    SECURITY_CHANGE_URL = "/change-pass"
    SECURITY_RESET_URL = "/reset-pass"
    SECURITY_URL_PREFIX = "/account"
    
    # ------- Flask-Security view overrides -------
    SECURITY_POST_LOGIN_VIEW = "index"
    SECURITY_POST_LOGOUT_VIEW = "index"
    SECURITY_CONFIRM_ERROR_VIEW = "login"
    SECURITY_POST_REGISTER_VIEW = "index"
    SECURITY_POST_CONFIRM_VIEW = "index"
    SECURITY_POST_RESET_VIEW = "login"
    SECURITY_POST_CHANGE_VIEW = "index"
    
    # ------- Flask-Security message overrides -------
    SECURITY_MSG_ALREADY_CONFIRMED = ("Your email has already been confirmed.", "info")
    SECURITY_MSG_API_ERROR = ("Input not appropriate for requested API", "danger")
    SECURITY_MSG_ANONYMOUS_USER_REQUIRED = ("You can only access this endpoint when not logged in.", "danger")
    SECURITY_MSG_CONFIRMATION_EXPIRED = ("You did not confirm your email within %(within)s. New instructions to confirm your email have been sent to %(email)s.", "danger")
    SECURITY_MSG_CONFIRMATION_REQUEST = ("Confirmation instructions have been sent to %(email)s.", "info")
    SECURITY_MSG_CONFIRMATION_REQUIRED = ("Email requires confirmation.", "danger")
    SECURITY_MSG_CONFIRM_REGISTRATION = ("Thank you. Confirmation instructions have been sent to %(email)s.", "success")
    SECURITY_MSG_DISABLED_ACCOUNT = ("Account is disabled.", "danger")
    SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED = ("%(email)s is already associated with an account.", "danger")
    SECURITY_MSG_EMAIL_CONFIRMED = ("Thank you. Your email has been confirmed.", "success")
    SECURITY_MSG_EMAIL_NOT_PROVIDED = ("Email not provided", "danger")
    SECURITY_MSG_FAILED_TO_SEND_CODE = ("Failed to send code. Please try again later", "danger")
    SECURITY_MSG_FORGOT_PASSWORD = ("Forgot password?", "info")
    SECURITY_MSG_IDENTITY_ALREADY_ASSOCIATED = ("Identity attribute '%(attr)s' with value '%(value)s' is already associated with an account.", "danger")
    SECURITY_MSG_INVALID_CODE = ("Invalid code", "danger")
    SECURITY_MSG_INVALID_CONFIRMATION_TOKEN = ("Invalid confirmation token.", "danger")
    SECURITY_MSG_INVALID_EMAIL_ADDRESS = ("Invalid email address", "danger")
    SECURITY_MSG_INVALID_LOGIN_TOKEN = ("Invalid login token.", "danger")
    SECURITY_MSG_INVALID_PASSWORD = ("Invalid password", "danger")
    SECURITY_MSG_INVALID_PASSWORD_CODE = ("Password or code submitted is not valid", "danger")
    SECURITY_MSG_INVALID_REDIRECT = ("Redirections outside the domain are forbidden", "danger")
    SECURITY_MSG_INVALID_RESET_PASSWORD_TOKEN = ("Invalid reset password token.", "danger")
    SECURITY_MSG_LOGIN = ("Please log in to access this page.", "info")
    SECURITY_MSG_LOGIN_EMAIL_SENT = ("Instructions to login have been sent to %(email)s.", "success")
    SECURITY_MSG_LOGIN_EXPIRED = ("You did not login within %(within)s. New instructions to login have been sent to %(email)s.", "danger")
    SECURITY_MSG_PASSWORDLESS_LOGIN_SUCCESSFU = ("You have successfully logged in.", "success")
    SECURITY_MSG_PASSWORD_BREACHED = ("Password on breached list", "danger")
    SECURITY_MSG_PASSWORD_BREACHED_SITE_ERROR = ("Failed to contact breached passwords site", "danger")
    SECURITY_MSG_PASSWORD_CHANGE = ("You successfully changed your password.", "success")
    SECURITY_MSG_PASSWORD_INVALID_LENGTH = ("Password must be at least %(length)s characters", "danger")
    SECURITY_MSG_PASSWORD_IS_THE_SAME = ("Your new password must be different than your previous password.", "danger")
    SECURITY_MSG_PASSWORD_MISMATCH = ("Password does not match", "danger")
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = ("Password not provided", "danger")
    SECURITY_MSG_PASSWORD_NOT_SET = ("No password is set for this user", "danger")
    SECURITY_MSG_PASSWORD_RESET = ("You successfully reset your password and you have been logged in automatically.", "success")
    SECURITY_MSG_PASSWORD_RESET_EXPIRED = ("You did not reset your password within %(within)s. New instructions have been sent to %(email)s.", "danger")
    SECURITY_MSG_PASSWORD_RESET_REQUEST = ("Instructions to reset your password have been sent to %(email)s.", "info")
    SECURITY_MSG_PASSWORD_TOO_SIMPLE = ("Password not complex enough", "danger")
    SECURITY_MSG_PHONE_INVALID = ("Phone number not valid e.g. missing country code", "danger")
    SECURITY_MSG_REAUTHENTICATION_REQUIRED = ("You must re-authenticate to access this endpoint", "danger")
    SECURITY_MSG_REAUTHENTICATION_SUCCESSFUL = ("Reauthentication successful", "info")
    SECURITY_MSG_REFRESH = ("Please reauthenticate to access this page.", "info")
    SECURITY_MSG_RETYPE_PASSWORD_MISMATCH = ("Passwords do not match", "danger")
    SECURITY_MSG_TWO_FACTOR_INVALID_TOKEN = ("Invalid Token", "danger")
    SECURITY_MSG_TWO_FACTOR_LOGIN_SUCCESSFUL = ("Your token has been confirmed", "success")
    SECURITY_MSG_TWO_FACTOR_CHANGE_METHOD_SUCCESSFUL = ("You successfully changed your two-factor method.", "success")
    SECURITY_MSG_TWO_FACTOR_PERMISSION_DENIED = ("You currently do not have permissions to access this page", "danger")
    SECURITY_MSG_TWO_FACTOR_METHOD_NOT_AVAILABLE = ("Marked method is not valid", "danger")
    SECURITY_MSG_TWO_FACTOR_DISABLED = ("You successfully disabled two factor authorization.", "success")
    SECURITY_MSG_UNAUTHORIZED = ("You do not have permission to view this resource.", "danger")
    SECURITY_MSG_UNAUTHENTICATED = ("You are not authenticated. Please supply the correct credentials.", "danger")
    SECURITY_MSG_US_METHOD_NOT_AVAILABLE = ("Requested method is not valid", "danger")
    SECURITY_MSG_US_SETUP_EXPIRED = ("Setup must be completed within %(within)s. Please start over.", "danger")
    SECURITY_MSG_US_SETUP_SUCCESSFUL = ("Unified sign in setup successful", "info")
    SECURITY_MSG_US_SPECIFY_IDENTITY = ("You must specify a valid identity to sign in", "danger")
    SECURITY_MSG_USE_CODE = ("Use this code to sign in: %(code)s.", "info")
    SECURITY_MSG_USER_DOES_NOT_EXIST = ("Specified user does not exist", "danger")
    SECURITY_MSG_USERNAME_INVALID_LENGTH = ("Username must be at least %(min)d characters and less than %(max)d characters", "danger")
    SECURITY_MSG_USERNAME_ILLEGAL_CHARACTERS = ("Username contains illegal characters", "danger")
    SECURITY_MSG_USERNAME_DISALLOWED_CHARACTERS = ("Username can contain only letters and numbers", "danger")
    SECURITY_MSG_USERNAME_NOT_PROVIDED = ("Username not provided", "danger")
    SECURITY_MSG_USERNAME_ALREADY_ASSOCIATED = ("%(username)s is already associated with an account.", "danger")