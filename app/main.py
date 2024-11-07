from flask import Flask, Response, render_template, request, session, redirect, url_for, flash
import cv2, keyboard, secrets, bcrypt, os, smtplib, string, secrets, face_recognition, pickle
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
import ModeloDlib as MDlib
import faceRecognition as face_rec
import datetime as dt

# Response.headers['Strict-Transport-Security'] = 'max-age=31536000;' #Convierte las peticiones de http a https
# Response.headers['X-Content-Type-Options'] = 'nosniff' #no se deben cambiar ni seguir el contenido de Content-Type.
# Response.headers['X-Frame-Options'] = 'SAMEORIGIN' #No permite que la pagina se insertada en etiquetas iframe

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SECURE=True,  # Limita las cookies a solo el trafico por https
    SESSION_COOKIE_HTTPONLY=True,  # No permite que sean leidas por JS
    SESSION_COOKIE_SAMESITE='Lax')

# Response.set_cookie('UserName', 'flask', secure=True, httponly=True, samesite='Lax')

load_dotenv() #CARGAR VARIABLES DE ENTORNO
# Conexion base de datos mySQL
app.config["MYSQL_HOST"] = os.getenv('MY_DB_HOST')
app.config["MYSQL_USER"] = os.getenv('MY_DB_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MY_DB_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MY_DB')

app.secret_key = secrets.token_urlsafe(32)  
MySqlDB = MySQL(app)
#rutaCam = "http://192.168.1.156:8080" 

######################################################################################################################################
def SendEmail(remitente, destinatario, asunto, rutaEmail):
    msg = MIMEMultipart()
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    with open(rutaEmail, 'r', encoding='utf-8') as archivo:
        html = archivo.read()

    msg.attach(MIMEText(html, 'html', 'utf-8'))
    server = smtplib.SMTP(os.getenv('SMPT_SSL'), 587)
    server.starttls()
    server.login(remitente, os.getenv('MY_PASSWORD_EMAIL'))
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

######################################################################################################################################

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

# Ruta principal
@app.route("/")
def index():
    return render_template("index.html")

#función LOGIN (INICIO DE SESIÓN)
@app.route("/Login_User", methods=["POST"])
def btn_Login():
    try:
        UserName = request.form["username"]
        Contraseña = request.form["contraseña"]

        if UserName != "" and Contraseña != "" and request.method == "POST":
            cur = MySqlDB.connection.cursor()
            cur.execute("Select UserName, Contraseña, Type_User from users Where UserName = %s", (UserName,))
            sql_Value = cur.fetchone()

            if sql_Value != None:
                user = sql_Value[0]
                passwordEncode = str(sql_Value[1])
                typeuser = sql_Value[2]
                isChecked =bcrypt.checkpw(Contraseña.encode('utf-8'),passwordEncode.encode('utf-8') )

                if isChecked == True and typeuser == "Administrador":
                    session["userName"] = user
                    session["is_Admin"] = True
                    return render_template("Seccion_Camara.html",Admin= session.get("is_Admin"))
                elif isChecked == True and typeuser == "SuperUsuario":
                    session["userName"] = user
                    session["is_Super"] = True
                    return render_template("Seccion_Camara.html",Super= session.get("is_Super"))
                else:
                    flash('El usuario o la contraseña no coinciden', 'error')
                    cur.close()

            else:
                cur.close()
                flash('El usuario o la contraseña no coinciden', 'error')

        else:
            flash('No coloco todos los datos', 'warning')

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))

#función LOG OUT (INICIO DE SESIÓN)
@app.route("/Log_Out", methods=["GET"])
def Log_Out():
    # face_rec.camara.release()
    # face_rec.saveVideo.release()
    # face_rec.cv2.destroyAllWindows()

    session.pop("userName", None)
    session.pop("userNombre", None)
    session.pop("userAp1", None)
    session.pop("userAp2", None)
    session.pop("is_Super", None)
    session.pop("is_Admin", None)
    session.pop("fullNameCCAI", None)
    flash("Sesión cerrada con éxito.","message")
    return redirect(url_for("index"))

#SECCIÓN CÁMARA
@app.route("/Seccion_Camara")
def Seccion_Camara():
    try:        
        if 'is_Admin' in session:
            return render_template("Seccion_Camara.html",Admin= session.get("is_Admin"))
        elif 'is_Super' in session:
            return render_template("Seccion_Camara.html",Super= session.get("is_Super"))
        else:
            flash('No se pudo asignar un tipo de usuario', 'error')

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))   

@app.route("/Seccion_Fotos")
def Seccion_Fotos():
    try:        
        if 'userName' in session:
            return render_template("Seccion_Fotos.html",Admin= session.get("is_Admin"))

        else:
            flash('No se pudo asignar un tipo de usuario', 'error')

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))  
#Seccion PERSONAL CCAI
@app.route("/Seccion_PersonalCCAI")
def Seccion_PersonalCCAI():
    try:
        if 'userName' in session:
            cur = MySqlDB.connection.cursor()
            cur.execute("SELECT * FROM personalccai")
            all_PersonsCCAI = cur.fetchall()

            if all_PersonsCCAI != None:
                tam = len(all_PersonsCCAI)
                # print(all_PersonsCCAI)
                # print(tam)
                if 'is_Admin' in session:
                    return render_template("Seccion_PersonalCCAI.html",Size=tam, PersonsCCAI=all_PersonsCCAI, Admin=session.get("is_Admin"))
                elif 'is_Super' in session:
                    return render_template("Seccion_PersonalCCAI.html",Size=tam,PersonsCCAI=all_PersonsCCAI, Super=session.get("is_Super"))
                else:
                    flash('No se pudo asignar un tipo de usuario', 'error')
                cur.close()

        else:
            flash('No se ha iniciado sesión', 'error')
            return redirect(url_for("index"))

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))        
#SECCIÓN RECUPERAR CONTRASEÑA
@app.route("/Seccion_Recuperar")
def Seccion_Recuperar():
    try:
        session.pop('Code', None)
        session.pop('Res_User', None)
        return render_template("Seccion_Recuperar_Pass.html")
    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Recuperar"))

#Función ENVIAR EMIAIL PARA CREAR CONTRASEÑA
@app.route("/Send_Email_For_Password", methods=["POST"])
def Send_Email_For_Password():
    try:
        UserName = request.form["Up_User"]
        if request.method == "POST":
            if UserName != "":
                cur = MySqlDB.connection.cursor()
                cur.execute("Select Email from users Where UserName = %s", (UserName,))
                sql_Value = cur.fetchone()

                if sql_Value != None:
                    UserEmail = sql_Value
                    asunto = "AVISO DE CÓDIGO DE RESTAURACIÓN - Vision AI"
                    code = Code_Generate()
                    mensaje = f"Vision AI\nInteligencia Artificial para Videovigilancia\n\nEste es su código para restablecer su contraseña.\n\n{code}\n\n© 2024 Tecnológico de Estudios Superiores de Cuautitlán Izcalli."
                    SendFlatEmail(os.getenv('MY_EMAIL'), UserEmail, mensaje, asunto)
                    print("Correo enviado correctamente.")
                    session['Code'] = code
                    session['Res_User'] = UserName
                    cur.close()
                    return render_template("Seccion_Password.html")
                else:
                    flash("No se encontro un correo de este usuario", "error")

    except Exception as error:
        print(f"Error: {error}")
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Recuperar"))

#Función ACTUALIZAR CONTRASEÑAS 
@app.route("/Update_Password", methods=["POST"])
def Update_Password():
    try:
        if 'Res_User' in session:
            Contraseña = request.form["Nueva_Contraseña"]
            Clave = request.form["Clave"].upper()
            usuario = session.get('Res_User')
            code = session.get('Code')
            if request.method == "POST" and Contraseña !="" and Clave !="":
                if Clave == code:
                    Contraseña = Contraseña.encode('utf-8')
                    salt = bcrypt.gensalt(12)
                    hash_Password = bcrypt.hashpw(Contraseña, salt)
                    cur = MySqlDB.connection.cursor()
                    cur.execute("UPDATE users SET Contraseña = %s WHERE UserName = %s", (hash_Password, usuario))
                    MySqlDB.connection.commit()
                    #Mandar correos
                    cur.execute("SELECT Email from users WHERE UserName = %s", (usuario,))
                    correo_user = str(cur.fetchone()[0])
                    asuntoEmail = 'AVISO DE CONTRASEÑA CAMBIADA - Vision AI'
                    ruta = 'app/html/passwordEmail.html'
                    SendEmail(os.getenv('MY_EMAIL'),correo_user, asuntoEmail, ruta)
                    print("Correo enviado correctamente.")
                    session.pop('Code', None)
                    session.pop('Res_User', None)
                    cur.close()
                    flash(f"La contraseña de {usuario} fue actualizada.","message")
                    return redirect(url_for("Seccion_Recuperar"))
                else:
                    flash("El código no coincide", "error")
                
            else:
                flash('No coloco todos los datos', 'warning')
        else:
            flash("No ha llenado los datos.", "error")
            return redirect(url_for("Seccion_Recuperar"))

    except Exception as error:
        print(f"Error: {error}")
        flash(f"HA OCURRIDO UN ERROR: {str(error)}", 'error')


    return redirect(url_for("index"))

#SECCIÓN USUARIO
@app.route("/Seccion_Pass")
def Seccion_Pass():
    try:
        if 'Res_User' in session:
            return render_template("Seccion_Password.html")
        else:
            flash('No coloco todos los datos', 'warning')
    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Recuperar"))

#SECCIÓN USUARIO
@app.route("/Seccion_Usuario")
def Seccion_Usuario():
    try:
        if 'userName' in session:
            cur = MySqlDB.connection.cursor()
            cur.execute("Select Nombre, Apellido_1, Apellido_2, Email from users Where UserName = %s", (session.get('userName'),))
            sql_Value = cur.fetchone()

            if sql_Value != None:
                user_nombre, user_ap1, user_ap2, user_email = sql_Value
                cur.close()

                if 'is_Admin' in session:
                    return render_template("Seccion_Usuario.html", User = session.get('userName'), name = user_nombre, ap_1 = user_ap1, ap_2 = user_ap2, Admin = session.get("is_Admin"), Correo = user_email)
                elif 'is_Super' in session:
                    return render_template("Seccion_Usuario.html", User = session.get('userName'), name = user_nombre, ap_1 = user_ap1, ap_2 = user_ap2, Super = session.get("is_Super"), Correo = user_email)
                else:
                    flash('No se pudo asignar un tipo de usuario', 'error')

        else:
            flash('No se ha iniciado sesión', 'error')
            return redirect(url_for("index"))

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))

# Función ACTUALIZAR DATOS DEL USUARIO
@app.route("/Change_data_user", methods=["POST"])
def btn_changeDataUser():
    try:
        if request.method == "POST":
            if 'userName' in session:
                # Verificar si todos los campos necesarios están llenos
                if all([request.form["username"], request.form["name"], request.form["ap1"], request.form["ap2"], request.form["correo"]]):
                    Update_user = request.form["username"]
                    Update_name = request.form["name"].upper()
                    Update_ap1 = request.form["ap1"].upper()
                    Update_ap2 = request.form["ap2"].upper()
                    Update_email = request.form["correo"]

                    cur = MySqlDB.connection.cursor()
                    cur.execute("SELECT UserName, Email FROM users WHERE (UserName = %s OR Email = %s) AND UserName != %s", (Update_user, Update_email, session.get('userName')))
                    sql_Value = cur.fetchone()

                    if sql_Value is None:
                        # Si no existe ni el usuario ni el correo, actualizar todos los datos
                        cur.execute("UPDATE users SET UserName = %s, Nombre = %s, Apellido_1 = %s, Apellido_2 = %s, Email = %s WHERE UserName = %s", (Update_user, Update_name, Update_ap1, Update_ap2, Update_email, session.get('userName')))
                        MySqlDB.connection.commit()
                        session["userName"] = Update_user
                        flash("Sus datos fueron actualizados.", "info")

                    else:
                        existing_user, existing_email = sql_Value
                        
                        if Update_user == existing_user and Update_email == existing_email:
                            cur.execute("UPDATE users SET  Nombre = %s, Apellido_1 = %s, Apellido_2 = %s WHERE UserName = %s", (Update_name, Update_ap1, Update_ap2, session.get('userName')))
                            MySqlDB.connection.commit()
                            cur.close()
                            flash("El usuario y correo ya existen, solo se actualizaron los demas datos.", "info")

                        elif Update_user != existing_user and Update_email == existing_email:
                            # Si el correo ya existe pero el nombre de usuario no, actualizamos solo los datos permitidos
                            cur.execute("UPDATE users SET UserName = %s, Nombre = %s, Apellido_1 = %s, Apellido_2 = %s WHERE UserName = %s", (Update_user, Update_name, Update_ap1, Update_ap2, session.get('userName')))
                            MySqlDB.connection.commit()
                            session["userName"] = Update_user
                            flash("El correo ya existía, se actualizaron los demás datos.", "info")

                        elif Update_user == existing_user and Update_email != existing_email:
                            # Si el nombre de usuario ya existe pero no el correo, actualizamos solo los datos permitidos
                            cur.execute("UPDATE users SET Nombre = %s, Apellido_1 = %s, Apellido_2 = %s, Email = %s WHERE UserName = %s", (Update_name, Update_ap1, Update_ap2, Update_email, session.get('userName')))
                            MySqlDB.connection.commit()
                            flash("El nombre de usuario ya existía, se actualizaron los demás datos.", "info")

                    cur.close()

                else:
                    flash("Tiene que colocar todos los datos.", "warning")

            else:
                flash("El usuario no está en la sesión.", "error")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Usuario"))


#SECCIÓN AYUDA
@app.route("/Seccion_Ayuda")
def Seccion_Ayuda():
    try:
        if 'userName' in session and 'is_Admin' in session:
            return render_template("Seccion_Ayuda.html", Admin = session.get("is_Admin"))
        elif 'userName' in session and 'is_Super' in session:
            return render_template("Seccion_Ayuda.html", Super = session.get("is_Super"))
        else:
            flash("No se ha iniciado sesión", "error")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))

#SECCIÓN REGISTRAR USUARIOS
@app.route("/Seccion_Registrar")
def Seccion_Registrar():
    try:

        if'userName' in session and 'is_Super' in session:
            cur = MySqlDB.connection.cursor()
            cur.execute("SELECT ID_User, UserName, Nombre, Apellido_1, Apellido_2, Email, Type_User FROM users")
            allUsers = cur.fetchall()
            cur.close()
            return render_template("Seccion_Registrar_User.html", Super = session.get("is_Super"), users = allUsers)
        else:
            flash("No se ha iniciado sesión", "error")

    except Exception as error:
        print(error)
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("index"))

#Función Eliminar Usuario]
@app.route("/Delete_User", methods=["POST"])
def Delete_User():
    user_id = request.form["user_id"]
    try:
        if request.method == "POST" and 'userName' in session:
            if user_id != "":
                cur = MySqlDB.connection.cursor()
                cur.execute("DELETE FROM users WHERE ID_User = %s", (user_id,))
                MySqlDB.connection.commit()
                cur.close()
                flash("El usuario se elimino del sistema.","info")
            else:
                flash("No se obtuvo la información del usuario.", "error")
        else:
            flash("No se ha iniciado sesión", "error")

    except Exception as error:
        print("ERROR ", error)
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Registrar"))

#Función Registrar un usuario 
@app.route("/Register_User", methods=["POST"])
def Register_User():
    try:
        newUserName = request.form["newusername"]
        newName = request.form["newname"].upper()
        newAp1 = request.form["newap1"].upper()
        newAp2 = request.form["newap2"].upper()
        newCorreo = request.form["newcorreo"].lower()
        newType = request.form["newtype"]
        newPassword = request.form["newpass"]

        if request.method == "POST":
            if all([newUserName and newName and newAp1 and newAp2 and newCorreo and newType and newPassword]):
                cur = MySqlDB.connection.cursor()
                cur.execute("SELECT UserName FROM users WHERE Email = %s OR UserName = %s", (newCorreo, newUserName))
                sql_Value = cur.fetchone()

                if sql_Value is None: #SI ES NONE NO ESTA EN LOS REGISTROS 
                    newPassword = newPassword.encode('utf-8')
                    salt = bcrypt.gensalt(12)
                    newHash_Password = bcrypt.hashpw(newPassword, salt)
                    cur.execute("INSERT INTO users (UserName, Nombre, Apellido_1, Apellido_2, Contraseña, Type_User, Email) VALUES (%s, %s, %s, %s, %s, %s, %s)",(newUserName, newName, newAp1, newAp2, newHash_Password, newType, newCorreo ))
                    MySqlDB.connection.commit()
                    cur.close()
                    #ImageGenerate(newUserName)
                    asuntoEmail = 'BIENVENIDO(A) - Vision AI'
                    ruta = 'app/html/welcomeEmail.html'
                    SendEmail(os.getenv('MY_EMAIL'), newCorreo, asuntoEmail, ruta)

                    flash(f"Se registro el usuario {newUserName} con éxito.","info")
                else:
                    flash("El usuario o correo electrónico ya estan en uso.","error")
            else:
                    flash("El usuario o correo electrónico ya estan en uso.","error")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')

    return redirect(url_for("Seccion_Registrar"))

#Funcion Registrar Personal del CCAI
@app.route("/Register_PersonCCAI", methods=["POST"])
def Register_PersonCCAI():
    try:
        newPersonName = request.form["newPersonName"].upper()
        newPersonAp1 = request.form["newPersonAp1"].upper()
        newPersonAp2 = request.form["newPersonAp2"].upper()
        newJobPerson = request.form["newJobPerson"].upper()
        newSHPerson = int(request.form["newSHPerson"])
        newEHPerson = int(request.form["newEHPerson"])

        if request.method == "POST":
            if all([newPersonName and newPersonAp1 and newPersonAp2 and newJobPerson and newSHPerson and newEHPerson]):
                cur = MySqlDB.connection.cursor()
                cur.execute("SELECT * FROM personalccai WHERE Nombre = %s AND Apellido_1 = %s AND Apellido_2 = %s", (newPersonName, newPersonAp1, newPersonAp2))
                sql_Value = cur.fetchone()

                if sql_Value is None: #SI ES NONE NO ESTA EN LOS REGISTROS 
                    cur.execute("INSERT INTO personalccai (Nombre, Apellido_1, Apellido_2, Puesto, HorarioEnt, HorarioSal) VALUES (%s, %s, %s, %s, %s, %s)",(newPersonName, newPersonAp1, newPersonAp2, newJobPerson, newSHPerson, newEHPerson))
                    MySqlDB.connection.commit()
                    cur.close()
                    flash(f"Se registro la persona {newPersonName} {newPersonAp1} con éxito.","info")
                else:
                    flash("Ya existe una persona con el mismo nombre.","error")
            else:
                flash("No estan llenos todos los campos","warning")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')
        print(error)

    return redirect(url_for("Seccion_PersonalCCAI"))

#Función ELIMINAR PERSONA DEL CCAI
@app.route('/Delete_PersonCCAI', methods = ["POST"])
def Delete_PersonCCAI():
    try:

        if request.method == "POST" and 'username' in session:
            id_PersonCCAI = request.form["person_id"]

            if id_PersonCCAI != "":
                cur = MySqlDB.connection.cursor()
                cur.execute("DELETE FROM personalccai WHERE ID = %s", (id_PersonCCAI,))
                MySqlDB.connection.commit()
                cur.close() 
                flash(f"Se elimino con éxito.","info")
            else:
                flash("No estan llenos todos los campos","warning")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')
        print(error)

    return redirect(url_for("Seccion_PersonalCCAI"))

#Función ACtualizar Personal del CCAI
@app.route("/Change_Data_Person", methods=["POST"])
def Change_Data_Person():
    try:
        if request.method == "POST":
            if 'userName' in session:
                IDPerson = request.form["person_id"]
                upPersonName = request.form["NamePersonCCAI"].upper()
                upPersonAp1 = request.form["Ap1PersonalCCAI"].upper()
                upPersonAp2 = request.form["Ap2PersonalCCAI"].upper()
                upJobPerson = request.form["JobPersonCCAI"].upper()
                upSHPerson = int(request.form["SHPersonCCAI"])
                upEHPerson = int(request.form["EHPersonCCAI"])

                if all([upPersonName and upPersonAp1 and upPersonAp2 and upJobPerson and upSHPerson and upEHPerson]):
                    cur = MySqlDB.connection.cursor()
                    cur.execute("SELECT ID FROM personalccai WHERE Nombre = %s AND Apellido_1 = %s AND Apellido_2 = %s AND ID != %s", (upPersonName, upPersonAp1, upPersonAp2, IDPerson))
                    sql_Value = cur.fetchone()

                    if sql_Value is not None:
                        cur.execute("UPDATE personalccai SET Puesto = %s, HorarioEnt = %s, HorarioSal = %s WHERE ID = %s",(upJobPerson, upSHPerson, upEHPerson, IDPerson))
                        MySqlDB.connection.commit()
                        cur.close()
                        flash(f"Ya hay alguien con el mismo nombre, se actualizaron los demás datos.","info")
                    else:
                        cur.execute("SELECT Nombre, Apellido_1, Apellido_2 FROM personalccai WHERE ID = %s", (IDPerson,))
                        sql_Value = cur.fetchone()
                        dbName, dbAp1, dbAp2 = sql_Value

                        dbName = dbName.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                        dbAp1 = dbAp1.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                        dbAp2 = dbAp2.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                        cur.execute("UPDATE personalccai SET Nombre = %s, Apellido_1 = %s, Apellido_2 = %s, Puesto = %s, HorarioEnt = %s, HorarioSal = %s WHERE ID = %s",(upPersonName, upPersonAp1, upPersonAp2, upJobPerson, upSHPerson, upEHPerson, IDPerson))
                        MySqlDB.connection.commit()

                        upName = upPersonName.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                        upAp1 = upPersonAp1.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                        upAp2 = upPersonAp2.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")

                        os.rename(f"app/personal_CCAI/{dbName} {dbAp1} {dbAp2}", f"app/personal_CCAI/{upName} {upAp1} {upAp2}" )
                        cur.close()
                        flash(f"Todos los datos de {upPersonName} {upPersonAp1} fueron actualizados.","info")
                        
                else:
                    flash("No estan llenos todos los campos","warning")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')
        print(error)

    return redirect(url_for("Seccion_PersonalCCAI"))

#Función ACTIVAR CÁMARA
@app.route('/Camera_Activate')
def Camera_Activate():
        return Response(face_rec.process_Camara(), mimetype='multipart/x-mixed-replace; boundary=frame')

#Función Tomar fotos (Sacar datos de sql)
@app.route('/Face_Capture', methods=["POST"])
def Face_Capture():
    try:
        if request.method == "POST" and 'userName' in session:
            IDPerson = request.form["person_id"]

            if IDPerson != "":
                cur = MySqlDB.connection.cursor()
                cur.execute("SELECT Nombre, Apellido_1, Apellido_2 FROM personalccai WHERE ID = %s", (IDPerson,))
                sql_Value = cur.fetchone()
                cur.close()
                if sql_Value != None:
                    dbName, dbAp1, dbAp2 = sql_Value
                    fullName = f"{dbName} {dbAp1} {dbAp2}"
                    fullName = fullName.replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                    session['fullNameCCAI'] = fullName
                else:
                    flash("No coincide con ninguna persona.","error")

            else:
                flash("No estan llenos todos los campos","warning")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')
        print(error)

    return redirect(url_for("Seccion_PersonalCCAI"))
#Función Tomar fotos de rostros
@app.route('/Face_Photos_Capture')
def Face_Photos_Capture():
        return Response(MDlib.Face_Capture(session.get('fullNameCCAI')), mimetype='multipart/x-mixed-replace; boundary=frame')

#Función ACTUALIZAR BD DE IMAGENES DE LOS ROSTROS
@app.route("/DB_Img_Update", methods=["POST"])
def DB_Img_Update():
    try:
        if request.method == "POST" and 'userName' in session:
            os.remove("app\Binary_Data\encodings.pkl")
            dataPath = "app/Personal_CCAI"
            personalCCAIList = os.listdir(dataPath)
            known_names, known_faces_encodings = face_rec.load_encodings_from_file()

            if not known_faces_encodings:  #Si no existen datos cargados, calcula y guarda
                for nameDirectory in personalCCAIList:
                    personPath = os.path.join(dataPath, nameDirectory)

                    for imageName in os.listdir(personPath):
                        image_path = os.path.join(personPath, imageName)
                        image = cv2.imread(image_path)
                        face_loc = face_recognition.face_locations(image, model="hog")
                        face_encodings = face_recognition.face_encodings(image, known_face_locations=face_loc)

                        for encoding in face_encodings:
                            known_faces_encodings.append(encoding)
                            known_names.append(nameDirectory)
                        print(f"Cargada la imagen: {image_path}")

                # Guarda los datos en el archivo después de cargarlos todos
                face_rec.save_encodings_to_file(known_names, known_faces_encodings)
                print("Datos guardados en archivo para evitar cálculos repetidos.")
                flash("Las imagenes fueron cargadas con éxito.","info")

    except Exception as error:
        flash(f"HA OCURRIDO UN ERROR: {error}", 'error')
        print(error)

    return redirect(url_for("Seccion_PersonalCCAI"))
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)
