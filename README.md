# Door Lock Security with Facial Recognition

This is an IoT-based door security system that uses facial recognition to grant or deny access. The system integrates a NodeMCU module, ultrasonic sensor, and PIR sensor to detect presence and a USB camera with facial recognition software to identify authorized users.

## Group Members

- Deepshika Chand (221011250)  
- Sowmya M (2210110591)  
- Ansh Sharma (220110167)

## Components

- NodeMCU ESP8266  
- Ultrasonic Sensor  
- PIR Motion Sensor  
- USB Camera  
- Raspberry Pi (or PC with Python support)

## Functionality

- Activates the NodeMCU via serial when motion is detected  
- Uses camera to capture face  
- Matches captured image against registered users using facial recognition  
- Grants or denies access accordingly

## Setup Instructions

### Arduino

1. Open 'ultrasonicAndPir.ino' in the Arduino IDE  
2. Connect your NodeMCU via USB  
3. Upload the sketch to the board  
4. This activates the sensor detection mechanism

### Python (Geany or any terminal)

#### 1. Register a new face


```
bash
python3 RegisterFace.py
```

This will capture images of a new user's face and add them to the training dataset.

2. Run the main face recognition system
```
python3 Main.py
```

## This script:

- Loads trained encodings

- Opens the USB camera feed

- Detects and recognizes faces

- Sends signal to unlock if match is found

## Notes
- Make sure your camera is connected properly before running the Python scripts.

- Ensure face images are clear and well-lit during registration for accurate recognition.

### License
This project is for educational use only.

