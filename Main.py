
import cv2
import face_recognition
import os
import json
import numpy as np
import serial
import time
import subprocess
import RPi.GPIO as GPIO

from twilio.rest import Client
from twilio_config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM,
    TWILIO_TO
)

# === CONFIGURATION ===
GREEN_PIN = 11  # Physical pin 11 for verified LED
FLASK_FEED_URL = "http://192.168.15.219:5000"  # Replace with your actual IP or ngrok URL

# === SETUP GPIO ===
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GREEN_PIN, GPIO.OUT, initial=GPIO.LOW)

# === UART SETUP ===
ser = serial.Serial('/dev/serial0', 115200, timeout=1)
print(" Waiting for motion detection from ESP8266...")

# === FACE DB SETUP ===
FACE_DB_FILE = "face_db.json"
FACE_FOLDER = "registered_faces"
os.makedirs(FACE_FOLDER, exist_ok=True)

# === Auto camera detection ===
def get_working_camera_index(max_index=10):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f" Camera found at index {i}")
                return i
        cap.release()
    print(" No working camera found.")
    return -1

CAMERA_INDEX = get_working_camera_index()
if CAMERA_INDEX == -1:
    raise Exception("No working camera available. Exiting.")

def load_face_db():
    if os.path.exists(FACE_DB_FILE):
        with open(FACE_DB_FILE, "r") as f:
            face_db = json.load(f)
            for k in face_db:
                face_db[k]["encoding"] = np.array(face_db[k]["encoding"])
            return face_db
    return {}

def capture_image():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("ERROR: Could not open the camera.")
        return None
    time.sleep(2)  # Camera warm-up
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

def send_sms_alert():
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Unverified person at the gate.\nHere is the live camera feed: {FLASK_FEED_URL}",
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print(f"SMS sent. SID: {message.sid}")
    except Exception as e:
        print("❌ Failed to send SMS:", e)

def launch_flask_server():
    print("Starting Flask live feed...")
    subprocess.Popen(['python3', 'flask_feed.py'])

def verify_face_once(face_db):
    frame = capture_image()
    if frame is None:
        print("Could not capture image.")
        return False

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame)

    if len(encodings) != 1:
        print("Ensure exactly one face is visible.")
        return False

    unknown_encoding = encodings[0]
    for person_id, data in face_db.items():
        known_encoding = data["encoding"]
        if face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)[0]:
            print(f" Face verified: {data['name']}")
            GPIO.output(GREEN_PIN, GPIO.HIGH)
            time.sleep(5)
            GPIO.output(GREEN_PIN, GPIO.LOW)
            return True

    print(" Face not verified.")
    return False

def main():
    face_db = load_face_db()

    # Wait once for motion
    while True:
        if ser.in_waiting:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            if msg == "1":
                print(" Motion detected! Starting face recognition...")
                break
            elif msg == "0":
                print("No motion.")
            else:
                print("Unknown message:", msg)
        time.sleep(0.1)

    # Run face verification once
    is_verified = verify_face_once(face_db)

    if not is_verified:
        print(" Sending SMS to owner...")
        send_sms_alert()
        time.sleep(2)
        launch_flask_server()

    print(" Process completed. Exiting.")
    ser.reset_input_buffer()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
