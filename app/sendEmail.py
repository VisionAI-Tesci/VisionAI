from dotenv import load_dotenv
import os
import secrets
import string
from email.message import EmailMessage
import smtplib

######################################################################################################################################
# Función generar codigos de restauración de contraseña
def Code_Generate():
    letras = string.ascii_letters
    numeros = string.digits
    Alfabeto = letras + numeros
    psw_tam = 8
    password = ''
    for i in range(psw_tam):
        password += ''.join(secrets.choice(Alfabeto)).upper()
    return password
######################################################################################################################################

# Carfar variables de entorno
load_dotenv()

######################################################################################################################################
# Función enviar Correos planos
def SendFlatEmail(remitente, destinatario, mensaje, asunto):

    email = EmailMessage()
    email['Subject'] = asunto
    email['From'] = remitente
    email['To'] = destinatario
    email.set_content(mensaje)

    flatServer = smtplib.SMTP_SSL(os.getenv('SMPT_SSL'))
    flatServer.login(remitente, os.getenv('MY_PASSWORD_EMAIL'))
    flatServer.sendmail(remitente, destinatario, email.as_string())
    flatServer.quit()
######################################################################################################################################
