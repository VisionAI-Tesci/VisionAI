import cv2, dlib, imutils,keyboard, os

dataPath = "app/Personal_CCAI2"

def Face_Capture(newPerson):
    personPath = dataPath +'/'+ newPerson
    countImages = 0

    if not os.path.exists(personPath):
        os.makedirs(personPath)
        print(f"Carpeta {personPath} creada.")
    else: 
        print("Ya existe la carpeta.")

    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

    face_detector = dlib.get_frontal_face_detector()

    cap.set(5, 20.0) #fps
    cap.set(3, 640) #Ancho
    cap.set(4, 480) #Alto
    # cap.set(10, 20) #Brillo
    while True:
        ret, frame = cap.read()

        if ret == False:
            break

        frame = imutils.resize(frame, width=600)
        auxFrame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        coordinates_bboxes = face_detector(gray, 1)
        # print("coordinates_bboxes:", coordinates_bboxes)

        for c in coordinates_bboxes:
            x_ini, y_ini, x_fin, y_fin = c.left(), c.top(), c.right(), c.bottom()
            rostro = auxFrame[y_ini:y_fin, x_ini:x_fin]
            rostro = cv2.resize(rostro,(150,150),interpolation=cv2.INTER_CUBIC)
            cv2.rectangle(frame, (x_ini, y_ini), (x_fin, y_fin), (0, 255, 0), 2)

            if keyboard.is_pressed("f"):
                cv2.imwrite(personPath + f"/rostro {countImages}.jpg", rostro)
                countImages +=1
                print(f"imagen {countImages} creada.")

        suc, encode = cv2.imencode('.jpg', frame)
        frame = encode.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    cap.release()
    cv2.destroyAllWindows()
