from flask import render_template
from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_user_email(user):
    token = user.get_utoken()
    send_email(
        '[Marketlnx] Verify your account',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.username],
        text_body=render_template('username/confirm_account.txt', user=user, token=token),
        html_body=render_template('username/confirm_account.htm', user=user, token=token)
    )

