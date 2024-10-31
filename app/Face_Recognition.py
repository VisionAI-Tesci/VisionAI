import face_recognition, cv2, os, keyboard
import datetime as dt

class Face_Recognition_CCAI:
    def process_Camara():
        dataPath = "app/Personal_CCAI"
        personalCCAIList = os.listdir(dataPath)

        camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        camara.set(5, 24.0) # fps
        camara.set(3, 640) # Ancho
        camara.set(4, 480) # Alto

        monthYear = dt.datetime.now().strftime("%B-%Y")
        if not os.path.exists(f"app/Grabaciones/{monthYear}"):
            os.makedirs("app/Grabaciones/"+ monthYear)
            print("Carpeta de grabaciones ",monthYear, " creada.")
        dirRecord = f"app/Grabaciones/{monthYear}"

        #Crear nombre y codificación del video
        nameVideo = str(dt.datetime.now().strftime("%A %d-%b-%Y %H-%M-%S %p")) + ".avi"
        nameVideo = dirRecord + '/' + nameVideo
        saveVideo = cv2.VideoWriter(nameVideo, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'), 24.0, (640, 480))
        
        # Cargar imágenes y nombres en listas
        known_faces_encodings = []
        known_names = []

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
                print(image_path)

        while True:
            ret, frame = camara.read()
            if not ret:
                break
            # frame = cv2.flip(frame, 1) #Para cámara de laptop
            
            # Detectar rostros en el cuadro actual
            small_Frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
            
            face_locations = face_recognition.face_locations(small_Frame, model="hog")

            # Solo calcular las codificaciones si se detectan rostros
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
                        # print(text)
                    top, right, bottom, left = [coord * 2 for coord in face_location]
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, text, (left, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            saveVideo.write(frame)
            # frame = cv2.resize(frame,(480,480),interpolation= cv2.INTER_CUBIC)
            suc, encode = cv2.imencode('.jpg', frame)
            frame = encode.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("z"):
                break
        saveVideo.release()
        camara.release()
        cv2.destroyAllWindows()
        print("Camara cerrada")