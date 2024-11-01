import face_recognition, cv2, os, keyboard, pickle
import datetime as dt

dataPath = "app/Personal_CCAI2"
personalCCAIList = os.listdir(dataPath)
#Crear carpeta de grabaciones y inicializar videowritter()
monthYear = dt.datetime.now().strftime("%B-%Y")
if not os.path.exists(f"app/Grabaciones/{monthYear}"):
    os.makedirs("app/Grabaciones/"+ monthYear)
    print("Carpeta de grabaciones ",monthYear, " creada.")

dirRecord = f"app/Grabaciones/{monthYear}"

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
    camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #Obtener info de la camara
    widht = int(camara.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camara.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #Crear nombre y codificación del video
    nameVideo = str(dt.datetime.now().strftime("%A %d-%b-%Y %H-%M-%S %p")) + ".avi"
    nameVideo = dirRecord + '/' + nameVideo
    saveVideo = cv2.VideoWriter(nameVideo, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'), 24.0, (widht, height))

    while True:
        ret, frame = camara.read()

        if not ret:
            break

        small_Frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
        face_locations = face_recognition.face_locations(small_Frame, model="hog")

        if face_locations:
            face_frame_encodings = face_recognition.face_encodings(small_Frame, known_face_locations=face_locations)
            for (face_location, face_encoding) in zip(face_locations, face_frame_encodings):
                results = face_recognition.compare_faces(known_faces_encodings, face_encoding)

                text = "Desconocido"
                color = (50, 50, 255)

                if True in results:
                    match_index = results.index(True)
                    text = known_names[match_index]
                    color = (125, 220, 0)

                top, right, bottom, left = [coord * 2 for coord in face_location]
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, text, (left, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        saveVideo.write(frame)
        suc, encode = cv2.imencode('.jpg', frame)
        frame = encode.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("z"):
            break
    saveVideo.release()
    camara.release()
    cv2.destroyAllWindows()