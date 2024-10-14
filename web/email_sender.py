import smtplib
from web.settings_loader import get_processor_settings
from logger import log_event
import requests

settings = get_processor_settings()

APIKEY = settings["APIKEY"]
NAMESPACE = settings["APINAMESPACE"]


def send_email_message_via_smtp(dest_email, message):
    """
    :param dest_email is a email where you send a mail:
    :param message eerrrm what else to say...:
    :return nothing, sends email:

    """
    smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
    smtpObj.starttls()
    smtpObj.login(settings['admin_mail'], settings['admin_mail_password'])
    try:
        log_event("trying to send a email message", 10, dest_email=dest_email, message=message)
        smtpObj.sendmail(settings['admin_mail'], dest_email, message)
    except:
        log_event("failed to send a email message", 30, dest_email=dest_email)
    smtpObj.quit()
