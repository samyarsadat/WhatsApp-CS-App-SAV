#  WhatsApp messaging client project
#  Application/library init file
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries -------
import logging
import os
from flask_socketio import SocketIO
from flask import Flask, request, session
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from infobip_channels import WhatsAppChannel
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from mailjet_rest import Client
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from config import AppConfig


# -=-=-= Functions =-=-=-
# ---- Custom locale selector for Babel ----
def localeselector():
    lang = session.get("lang")

    if lang:
        return lang

    session["lang"] = request.accept_languages.best_match(AppConfig.SUPPORTED_LANGS, AppConfig.DEFAULT_LANG)
    return session.get("lang")


# -=-=-= Logging init =-=-=-
formatter = logging.Formatter("[%(asctime)s] [%(threadName)s/%(levelname)s] [%(module)s/%(funcName)s]: %(message)s")

# ---- Get a logger with custom settings ----
def get_logger(name, log_file, level):
    handler = logging.FileHandler(os.path.join(AppConfig.LOG_FILE_PATH, log_file))        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


log = get_logger("main", "WACApp_MainPyLog.log", AppConfig.LOG_LEVEL)
debug_log = get_logger("debug", "WACApp_DebugPyLog.log", logging.DEBUG)
socketio_log = get_logger("socketio", "WACAPP_SocketioPyLog.log", logging.DEBUG)


# ------- Flask and Flask plug-in init -------
app = Flask(__name__)
app.config.from_object(AppConfig)
cache = Cache(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app, locale_selector=localeselector)
csrf = CSRFProtect(app)
mailjet = Client(auth=(AppConfig.MAILJET_API_KEY, AppConfig.MAILJET_API_SECRET), version="v3.1")
waapi = WhatsAppChannel.from_auth_params({"base_url": AppConfig.WAAPI_BASE_URL, "api_key": AppConfig.WAAPI_API_KEY})
socketio = SocketIO(app, logger=socketio_log, engineio_logger=socketio_log)
ga = None

if AppConfig.ENABLE_ANALYTICS:
    ga = BetaAnalyticsDataClient()