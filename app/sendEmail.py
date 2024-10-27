from dotenv import load_dotenv
import os
import secrets
import string
from email.message import EmailMessage
import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


def Code_Generate():
    letras = string.ascii_letters
    numeros = string.digits
    Alfabeto = letras + numeros
    psw_tam = 8
    password = ''
    for i in range(psw_tam):
        password += ''.join(secrets.choice(Alfabeto)).upper()
    return password


load_dotenv()
remitente = os.getenv('MY_EMAIL')
destinatario = 'erne01608@gmail.com'
code = Code_Generate()
mensaje = f"""Vision AI
Inteligencia Artificial para Videovigilancia

Este es su código para restablecer su contraseña.

{code}

© 2024 Tecnológico de Estudios Superiores de Cuautitlán Izcalli."""

email = EmailMessage()
email['Subject'] = 'Código de confirmación | Vision AI'
email['From'] = remitente
email['To'] = destinatario
email.set_content(mensaje)

server = smtplib.SMTP_SSL(os.getenv('SMPT_SSL'))
server.login(remitente, os.getenv('MY_PASSWORD_EMAIL'))

server.sendmail(remitente, destinatario, email.as_string())

server.quit()
