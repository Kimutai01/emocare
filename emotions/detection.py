# import face_recognition
import cv2
import numpy as np
import requests
from io import BytesIO
from keras.models import load_model
from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
import cv2
import numpy as np
# from flask import Flask, render_template, request, redirect, url_for
from speechbrain.pretrained.interfaces import foreign_class
import soundfile as sf
import pyaudio
import numpy as np
import os
import face_recognition
import mediapipe as mp
def face_recognition_function(frame, image_url='URL_OF_YOUR_IMAGE', name='Unknown'):
    # Load Image from URL and Convert to RGB
    response = requests.get(image_url)
    img_bytes = BytesIO(response.content)
    imgElon = face_recognition.load_image_file(img_bytes)
    imgElon = cv2.cvtColor(imgElon, cv2.COLOR_BGR2RGB)
    faceLocElon = face_recognition.face_locations(imgElon)[0]
    encodeElon = face_recognition.face_encodings(imgElon)[0]

    # resize frame for display
    frame = cv2.resize(frame, (960, 720))

    # Face detection and encoding for the live frame
    faceLocTest = face_recognition.face_locations(frame)
    if faceLocTest:
        encodeTest = face_recognition.face_encodings(frame, faceLocTest)[0]

        # Compare Faces and Find Distance
        results = face_recognition.compare_faces([encodeElon], encodeTest)
        faceDis = face_recognition.face_distance([encodeElon], encodeTest)

        # Draw rectangle and text on the live frame
        top, right, bottom, left = faceLocTest[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)

        # Label the bounding box with the name if confidence is above 0.6
        if results[0] and faceDis[0] < 0.8:
            detected_name = name
            cv2.putText(frame, detected_name, (left, top - 10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 255), 2)
        else:
            detected_name = 'Unknown'
            cv2.putText(frame, detected_name, (left, top - 10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 255), 2)

        return frame, detected_name  # Return the frame and the detected name

    # Return the frame and the default name if no face is detected
    return frame, 'Unknown'

def face_emotion_detection(frame):
    face_classifier = cv2.CascadeClassifier('models/haarcascade_frontalface_default (1).xml')
    classifier = load_model("models/model.h5")
    emotion_labels = ['Angry','Disgust','Fear','Happy','Neutral', 'Sad', 'Surprise']

    # resize frame for display
    # resize frame for display
    frame = cv2.resize(frame, (960,720))

    labels = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray)

    detected_face_emotion = "No Faces"  # Default emotion if no faces are detected

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            prediction = classifier.predict(roi)[0]
            detected_face_emotion = emotion_labels[prediction.argmax()]
            label_position = (x, y)
            cv2.putText(frame, detected_face_emotion, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'No Faces', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame, detected_face_emotion

def is_standing(pose_landmarks):
    if pose_landmarks is None:
        return False  # If no landmarks are detected, assume not standing

    # Assume landmarks for shoulders
    left_shoulder = pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]

    # Check if both shoulders are visible (above certain threshold)
    return left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5

def pose_estimation(frame):
    # initialize mediapipe pose solution
    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils
    pose = mp_pose.Pose()

    # resize frame for display
    frame = cv2.resize(frame, (960, 720))

    # do Pose detection
    results = pose.process(frame)

    # draw the detected pose on the frame
    mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                           mp_draw.DrawingSpec((255, 0, 0), 2, 2),
                           mp_draw.DrawingSpec((255, 0, 255), 2, 2)
                           )

    # Extract and draw pose on plain white image
    h, w, c = frame.shape
    opImg = np.zeros([h, w, c])
    opImg.fill(255)

    # draw extracted pose on black white image
    mp_draw.draw_landmarks(opImg, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                           mp_draw.DrawingSpec((255, 0, 0), 2, 2),
                           mp_draw.DrawingSpec((255, 0, 255), 2, 2)
                           )

    # print all landmarks
    pose_landmarks = results.pose_landmarks
    print(pose_landmarks)

    return frame, pose_landmarks

def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []
    for i in range(0, int(RATE / CHUNK * 5)):  # Record for 5 seconds, adjust as needed
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    return audio_data

