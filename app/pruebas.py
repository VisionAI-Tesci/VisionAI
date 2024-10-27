from flask import Flask, render_template
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # Cargar variables de entorno

# Configuración de la conexión a la base de datos MySQL
app.config["MYSQL_HOST"] = os.getenv('MY_DB_HOST')
app.config["MYSQL_USER"] = os.getenv('MY_DB_USER')  # Error corregido aquí
app.config["MYSQL_PASSWORD"] = os.getenv('MY_DB_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MY_DB')

MySqlDB = MySQL(app)

@app.route("/")
def index():
    email = "203107113@cuautitlan.tecnm.mx"
    user =  "Administrador_1"
    cur = MySqlDB.connection.cursor()
    cur.execute("Select UserName, Email from users WHERE Username = %s OR Email = %s", (user, email))
    sql_Value = cur.fetchone()
    print(sql_Value)
    if user in sql_Value:
        print("AQUI ESTA")
    else:
        print("NO ESTA")
    return render_template("index.html")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
