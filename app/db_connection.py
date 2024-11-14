import MySQLdb, os
from dotenv import load_dotenv
import datetime as dt
load_dotenv() #CARGAR VARIABLES DE ENTORNO

def create_connection():
    connection = MySQLdb.connect(
        host=os.getenv('MY_DB_HOST'),
        user=os.getenv('MY_DB_USER'),
        passwd=os.getenv('MY_DB_PASSWORD'),
        db=os.getenv('MY_DB')
    )
    return connection

def SearchDataPerson(connection, namePerson, ap1Person, ap2Person):
    cur = connection.cursor()
    cur.execute("SELECT Nombre, Apellido_1, Apellido_2, Puesto, HorarioEnt, HorarioSal FROM personalccai WHERE Nombre=%s AND Apellido_1=%s AND Apellido_2=%s", (namePerson, ap1Person, ap2Person))
    textForScanner = cur.fetchone()
    cur.close()
    return textForScanner

def InsertInLog (connection, namePerson, ap1Person, ap2Person, Job, startHour, endHour):
    cur = connection.cursor()
    dateNow = str(dt.datetime.now().strftime("%d-%b-%Y %H:%M:%S %p"))
    cur.execute("INSERT INTO personsdetections (Nombre, Apellido_1, Apellido_2, Puesto, HorarioEnt, HorarioSal, Fecha) VALUES (%s, %s, %s, %s, %s, %s, %s)",(namePerson, ap1Person, ap2Person, Job, startHour, endHour,dateNow))
    connection.commit()
    cur.close()
