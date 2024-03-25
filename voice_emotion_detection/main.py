from flask import Flask, render_template, request, redirect, url_for
from speechbrain.pretrained.interfaces import foreign_class
import soundfile as sf
import pyaudio
import numpy as np
import os


# Function to record audio
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

# Function to classify emotion using pretrained model
def classify_emotion(audio_data, temp_wav_path):
    sf.write(temp_wav_path, audio_data, 16000)

    classifier = foreign_class(source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP", pymodule_file="custom_interface.py", classname="CustomEncoderWav2vec2Classifier")
    out_prob, score, index, text_lab = classifier.classify_file(temp_wav_path)

    return text_lab


# def classify():
#     # Record audio
#     audio_data = record_audio()

#     # Save audio to a temporary file
#     temp_wav_path = 'temp.wav'
#     with open(temp_wav_path, 'wb') as f:
#         f.write(audio_data)

#     # Classify emotion
#     emotion_label = classify_emotion(audio_data, temp_wav_path)

#     # Return the result
#     return emotion_label

# voice_emotion = classify()
# print(voice_emotion)