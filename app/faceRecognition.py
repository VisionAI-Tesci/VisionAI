import face_recognition, cv2, os, keyboard, pickle
from db_connection import create_connection, SearchDataPerson, InsertInLog
import datetime as dt

connection = create_connection()
# url = "http://localhost:8080/stream"
dataPath = "app/Personal_CCAI"
personalCCAIList = os.listdir(dataPath)
#Crear carpeta de grabaciones y inicializar videowritter()
# monthYear = dt.datetime.now().strftime("%B-%Y")
# if not os.path.exists(f"app/Grabaciones/{monthYear}"):
#     os.makedirs("app/Grabaciones/"+ monthYear)
#     print("Carpeta de grabaciones ",monthYear, " creada.")

# dirRecord = f"app/Grabaciones/{monthYear}"
camara = None
#######################################################################
# Función para guardar los encodings y nombres en un archivo (Binario)
def save_encodings_to_file(known_names, known_faces_encodings):
    with open("app\Binary_Data\encodings.pkl", "wb") as f:
        pickle.dump((known_names, known_faces_encodings), f)
#######################################################################
# Función para cargar los encodings y nombres desde un archivo (Binario)
def load_encodings_from_file():
    if os.path.exists("app\Binary_Data\encodings.pkl"):
        with open("app\Binary_Data\encodings.pkl", "rb") as f:
            return pickle.load(f)
    return [], []
#######################################################################
# Función para procesar la cámara y realizar el reconocimiento
def process_Camara():
    known_names, known_faces_encodings = load_encodings_from_file()

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
        save_encodings_to_file(known_names, known_faces_encodings)
        print("Datos guardados en archivo para evitar cálculos repetidos.")
    else:
        print("Los datos ya fueron cargados desde el archivo.")

    global camara, saveVideo
    # Verificamos si la cámara ya está abierta
    if camara is None or not camara.isOpened():
        print("Reasignando la cámara...")
        camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        widht = int(camara.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camara.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # nameVideo = str(dt.datetime.now().strftime("%A %d-%b-%Y %H-%M-%S %p")) + ".avi"
        # nameVideo = dirRecord + '/' + nameVideo
        # saveVideo = cv2.VideoWriter(nameVideo, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'), 24.0, (widht, height))
    else:
        print("Ya esta asignada")
    while True:
        ret, frame = camara.read()

        if not ret:
            break

        small_Frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_Frame, model="hog")

        if face_locations:
            face_frame_encodings = face_recognition.face_encodings(small_Frame, known_face_locations=face_locations)
            for (face_location, face_encoding) in zip(face_locations, face_frame_encodings):
                global results, text
                results = face_recognition.compare_faces(known_faces_encodings, face_encoding)

                text = "Desconocido"
                textJob="Desconocido"
                textHours="Desconocido"
                color = (50, 50, 255)

                if True in results:
                    match_index = results.index(True)
                    text = str(known_names[match_index])
                    if text != "Desconocido":
                        print(text)
                        fullName = text.split(" ")
                        Name, Ap1, Ap2 = fullName
                        sql_Values= SearchDataPerson(connection,Name, Ap1, Ap2)

                        if sql_Values is not None:
                            NameIn, Ap1In, Ap2IN, Job, StartHour, EndHour = sql_Values
                            text= f"{Name} {Ap1} {Ap2}"
                            textJob=  f"Puesto: {Job}"
                            textHours = f"Horario: {StartHour}:00 a {EndHour}:00"
                            InsertInLog(connection, NameIn, Ap1In, Ap2IN, Job, StartHour, EndHour)
                            color = (255, 0, 0)
                else:
                    NameIn = Ap1In = Ap2IN = Job = StartHour = EndHour = "DESCONOCIDO"
                    InsertInLog(connection, NameIn, Ap1In, Ap2IN, Job, StartHour, EndHour)

                top, right, bottom, left = [coord * 4 for coord in face_location]
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
                cv2.putText(frame, textJob, (left, bottom + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1) 
                cv2.putText(frame, textHours, (left, bottom + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)


        # saveVideo.write(frame)
        suc, encode = cv2.imencode('.jpg', frame)
        frame = encode.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("z"):
            camara.release()
            cv2.destroyAllWindows()
            break

    camara.release()
    cv2.destroyAllWindows()