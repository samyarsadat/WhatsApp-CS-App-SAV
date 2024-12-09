#  WhatsApp messaging client project
#  Database module
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
from dataclasses import dataclass
from flask import Blueprint
from flask_security import RoleMixin, SQLAlchemySessionUserDatastore, UserMixin
from init import db


# ------- Blueprint init -------
database = Blueprint("database", __name__)


# ------- Database models -------

# -=-=-= Accounts database =-=-=-
# ---- User roles table ----
roles_users = db.Table("roles_users",
                       db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
                       db.Column("role_id", db.Integer(), db.ForeignKey("role.id")), 
                       bind_key="accounts")


# ---- Roles table ----
class Role(db.Model, RoleMixin):
    __bind_key__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __init__(self, name, description):
        self.name = name 
        self.description = description
        

# ---- User table ----
class User(db.Model, UserMixin):
    __bind_key__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    pp_url = db.Column(db.String(512), default="img/logos/default_pp.png")
    password = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))
    tf_phone_number = db.Column(db.String(128), nullable=True)
    tf_primary_method = db.Column(db.String(64), nullable=True)
    tf_totp_secret = db.Column(db.String(255), nullable=True)


# -=-=-= General database =-=-=-
# ---- Agents table ----
@dataclass
class Agent(db.Model):
    __bind_key__ = "agents"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    type = db.Column(db.String(10))
    phone_number = db.Column(db.String(128), unique=True, nullable=True)
    fs_user_id = db.Column(db.Integer, unique=True, nullable=True)


# ---- Incoming message redirect rules table ----
@dataclass
class RedirectRule(db.Model):
    __bind_key__ = "agents"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5000))
    phone_number = db.Column(db.String(128))
    agent_id = db.Column(db.Integer)
    
    
# ---- Messages table ----
@dataclass
class Message(db.Model):
    __bind_key__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(256), unique=True)
    direction = db.Column(db.Integer)  # 1: Outgoing, 0: Incoming
    client_number = db.Column(db.String(128))
    agents_resp = db.Column(db.JSON)
    origin_phone_number = db.Column(db.String(128), nullable=True)
    datetime = db.Column(db.DateTime)
    status = db.Column(db.String(128))
    content = db.Column(db.JSON)
    type = db.Column(db.String(128))
    is_redirect = db.Column(db.Boolean)
    

# ---- Phone numbers table ----
@dataclass
class PhoneNumber(db.Model):
    __bind_key__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    unread_msgs = db.Column(db.Integer)
    last_msg = db.Column(db.String(100000))
    number = db.Column(db.String(128), unique=True)
    customer_id = db.Column(db.String(30), unique=True)
    display_name = db.Column(db.String(256), unique=True)
    
    
# ---- Announcement messages table ----
@dataclass 
class AnnouncementMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(10000))
    level = db.Column(db.String(15))
    duration = db.Column(db.String(20))
    start_time = db.Column(db.DateTime)


# ------- Flask-Security user datastore -------
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
