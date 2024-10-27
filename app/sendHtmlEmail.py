from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

remitente = os.getenv('MY_EMAIL')
destinatario = 'erne01608@gmail.com'
asunto = 'AVISO Vision AI'

msg = MIMEMultipart()

msg['Subject'] = asunto
msg['From'] = remitente
msg['To'] = destinatario

with open('app/email.html', 'r', encoding='utf-8') as archivo:
    html = archivo.read()

msg.attach(MIMEText(html, 'html', 'utf-8'))

server = smtplib.SMTP(os.getenv('SMPT_SSL'), 587)
server.starttls()
server.login(remitente, os.getenv('MY_PASSWORD_EMAIL'))

server.sendmail(remitente, destinatario, msg.as_string())

server.quit()
