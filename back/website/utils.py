import smtplib
from email.mime.text import MIMEText
from api_key import MAILTRAP_USERNAME, MAILTRAP_PASSWORD, MAILTRAP_HOST, MAILTRAP_PORT
from json_responses import *

def send_email(recipient, subject, message):
    sender = MAILTRAP_USERNAME
    password = MAILTRAP_PASSWORD
    server = MAILTRAP_HOST
    port = MAILTRAP_PORT
    
    try:
        # Connecting to Mailtrap's SMTP server
        smtp_server = smtplib.SMTP(server, port)
        smtp_server.starttls()
        smtp_server.login(sender, password)
        
        # Creating the email message
        msg = MIMEText(message)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Sending the email
        smtp_server.sendmail(sender, recipient, msg.as_string())
        smtp_server.quit()
        return successful_response(description='Email sent successfully.')
    except Exception as e:
        return error_response(description='Error sending email via MailTrap.', error_details=f'error: {e}')