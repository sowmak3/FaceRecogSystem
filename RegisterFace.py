import cv2
import face_recognition
import os
import json
import numpy as np

# === CONFIGURATION ===
FACE_DB_FILE = "face_db.json"
FACE_FOLDER = "registered_faces"
os.makedirs(FACE_FOLDER, exist_ok=True)

# === CAMERA INDEX AUTO-DETECTION ===
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

# === LOAD / SAVE DB ===
def load_face_db():
    if os.path.exists(FACE_DB_FILE):
        with open(FACE_DB_FILE, "r") as f:
            db = json.load(f)
            for k in db:
                db[k]["encoding"] = np.array(db[k]["encoding"])
            return db
    return {}

def save_face_db(face_db):
    serializable_db = {
        k: {
            "name": v["name"],
            "encoding": v["encoding"].tolist()
        } for k, v in face_db.items()
    }
    with open(FACE_DB_FILE, "w") as f:
        json.dump(serializable_db, f, indent=2)

# === REGISTER FACE ===
def register_face():
    name = input("Enter the person's name to register: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        return

    face_db = load_face_db()

    if any(entry["name"].lower() == name.lower() for entry in face_db.values()):
        print("⚠️ A person with this name is already registered.")
        return

    print(" Capturing image... Please look at the camera.")
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Camera not accessible.")
        return

    cv2.waitKey(1000)  # Camera warm-up
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(" Failed to capture image.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame)

    if len(encodings) != 1:
        print("Exactly one face must be visible.")
        return

    encoding = encodings[0]  # Fixed index error here

    person_id = f"id_{len(face_db) + 1}"
    face_db[person_id] = {
        "name": name,
        "encoding": encoding
    }

    save_face_db(face_db)
    cv2.imwrite(os.path.join(FACE_FOLDER, f"{name}.jpg"), frame)

    print(f" {name} registered successfully.")

# === DELETE FACE ===
def delete_face():
    name = input("Enter the person's name to delete: ").strip()
    face_db = load_face_db()

    found = False
    keys_to_delete = [key for key, val in face_db.items() if val["name"].lower() == name.lower()]

    for key in keys_to_delete:
        found = True
        del face_db[key]

    if found:
        save_face_db(face_db)
        image_path = os.path.join(FACE_FOLDER, f"{name}.jpg")
        if os.path.exists(image_path):
            os.remove(image_path)
        print(f" {name} deleted successfully.")
    else:
        print(" Name not found in database.")

# === VIEW FACES ===
def view_faces():
    face_db = load_face_db()
    if not face_db:
        print("ℹ️ No faces registered yet.")
        return

    print("\n Registered Faces:")
    for entry in face_db.values():
        print(f" - {entry['name']}")
    print()

# === MAIN MENU ===
def main():
    while True:
        print("\n=== FACE DATABASE MANAGER ===")
        print("1. Register a new face")
        print("2. Delete a face")
        print("3. View all registered faces")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_face()
        elif choice == "2":
            delete_face()
        elif choice == "3":
            view_faces()
        elif choice == "4":
            print(" Exiting. Bye!")
            break
        else:
            print(" Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
