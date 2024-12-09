#  WhatsApp messaging client project
#  MailJet mailing API utility
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
from flask import abort
from flask_security import MailUtil
from init import mailjet, debug_log, log
from typing import Union
from config import AppConfig


# -=-=-= Mail util classes =-=-=-

# ---- Custom mail util for Flask-Security ----
class SecurityMailUtil(MailUtil):
    def send_mail(self, template: str, subject: str, recipient: str, sender: Union[str, tuple], body: str, html: str, user, **kwargs) -> None:
        mail_data = {
            "Messages":
            [{
                "From":
                {
                    "Email": sender,
                    "Name": AppConfig.SECURITY_EMAIL_SENDER_NAME
                },
                    
                "To":
                [{
                    "Email": recipient
                }],
                
                "Subject": subject,
                "TextPart": body,
                "HTMLPart": html
            }]
        }

        result = mailjet.send.create(data=mail_data)
        debug_log.debug(f"Sent security mail, Mailjet responded with status code [{result.status_code}]")
        
        if result.status_code != 200:
            debug_log.debug(f"Attempted to send security mail but Mailjet responded with error code [{result.status_code}]")
            log.critical(f"Attempted to send security mail but Mailjet responded with error code [{result.status_code}]")
            abort(500)