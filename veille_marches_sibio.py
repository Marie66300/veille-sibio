import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def envoyer_email(html_content):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = 465  # Port SSL sécurisé pour Gmail
    sender_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient_email = os.environ.get("EMAIL_RECIPIENT")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Rapport de Veille Marchés Publics - SI BIO"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    # Connexion SSL sécurisée pour Gmail
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
