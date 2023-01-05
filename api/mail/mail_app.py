from flask import Blueprint, current_app, render_template
from flask_mail import Mail, Message
from ..config.mail_config import *
from ..consts.responses import SuccessResponse, ErrorResponse
from ..consts.error_enum import ErrorEnum

mail = Mail()

email_blueprint = Blueprint("mail", __name__)

# Configure the mail extension
def configure_mail():
    app = current_app
    app.config["MAIL_SERVER"] = MAIL_SERVER
    app.config["MAIL_PORT"] = MAIL_PORT
    app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = MAIL_USE_SSL
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_USERNAME"] = MAIL_DEFAULT_SENDER
    mail.init_app(app)


def send_verification_email(user, verification_url):
    configure_mail()
    msg = Message(
        subject=SUBJECT_EMAIL_VERIFICATION + user["username"],
        sender=MAIL_DEFAULT_SENDER,
        recipients=[user["email"]],
    )
    try:
        msg.html = render_template(
            "email_verification.html",
            username=user["username"],
            verification_url=verification_url,
        )
    except Exception as e:
        print("Error rendering email template: ", e)
        return ErrorResponse(ErrorEnum.MAIL_SEND_ERROR).internal_server_error()
    try:
        mail.send(msg)
        return SuccessResponse({"message": "Verification email sent"}).ok()
    except Exception as e:
        print("Error sending email: ", e)
        return ErrorResponse(ErrorEnum.MAIL_SEND_ERROR).internal_server_error()


def send_reset_password_email(user, password_reset_url):
    configure_mail()
    msg = Message(
        subject=SUBJECT_PASSWORD_RESET + user["username"],
        sender=MAIL_DEFAULT_SENDER,
        recipients=[user["email"]],
    )
    try:
        msg.html = render_template(
            "password_reset.html",
            username=user["username"],
            password_reset_url=password_reset_url,
        )
    except Exception as e:
        print("Error rendering email template: ", e)
        return ErrorResponse(ErrorEnum.MAIL_SEND_ERROR).internal_server_error()
    try:
        mail.send(msg)
        return SuccessResponse({"message": "Password reset email sent"}).ok()
    except Exception as e:
        print("Error sending email: ", e)
        return ErrorResponse(ErrorEnum.MAIL_SEND_ERROR).internal_server_error()
