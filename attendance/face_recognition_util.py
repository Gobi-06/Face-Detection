import os
import cv2
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime
from .models import Employee

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.current_attendees = set()
        self.load_known_faces()

    def __del__(self):
        self.video.release()

    def load_known_faces(self):
        employees = Employee.objects.all()
        for employee in employees:
            image_path = employee.image.path
            if os.path.exists(image_path):
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    self.known_face_encodings.append(encoding[0])
                    self.known_face_names.append(employee.name)

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None

        # Process the image frame
        processed_frame = process_frame(image, self.known_face_encodings, self.known_face_names, self.current_attendees)

        # Mark attendance in the Excel file
        recognize_faces(self.current_attendees)

        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()

    def get_current_attendees(self):
        return list(self.current_attendees)  # Return current attendees as a list

def process_frame(frame, known_face_encodings, known_face_names, current_attendees):
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face found in the frame to see if it's someone we know
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # If a match was found in known_face_encodings, use the first one
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            current_attendees.add(name)  # Add to current attendees set

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    return frame

def recognize_faces(attendees):
    # Logic for recognizing faces and marking attendance
    date_str = datetime.now().strftime('%Y-%m-%d')
    try:
        df = pd.read_excel(f'attendance_files/attendance_{date_str}.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Employee ID', 'Name', 'Status', 'Time'])

    # Create a new DataFrame for current attendees
    new_entries = pd.DataFrame(columns=['Employee ID', 'Name', 'Status', 'Time'])

    # Mark attendance for current attendees
    for name in attendees:
        # Handle case where multiple employees have the same name
        employees = Employee.objects.filter(name=name)
        for emp in employees:
            if emp.name in df['Name'].values:
                df.loc[df['Name'] == emp.name, 'Status'] = 'Present'
                df.loc[df['Name'] == emp.name, 'Time'] = datetime.now().strftime('%H:%M:%S')
            else:
                new_entry = {
                    'Employee ID': emp.emp_id,
                    'Name': emp.name,
                    'Status': 'Present',
                    'Time': datetime.now().strftime('%H:%M:%S')
                }
                new_entries = pd.concat([new_entries, pd.DataFrame([new_entry])], ignore_index=True)

    # Mark all others as absent
    for index, row in df.iterrows():
        if row['Name'] not in attendees:
            df.at[index, 'Status'] = 'Absent'
            df.at[index, 'Time'] = datetime.now().strftime('%H:%M:%S')

    # Combine the existing DataFrame with the new entries
    df = pd.concat([df, new_entries], ignore_index=True)

    df.to_excel(f'attendance_files/attendance_{date_str}.xlsx', index=False)

def mark_absent_for_latecomers():
    date_str = datetime.now().strftime('%Y-%m-%d')
    try:
        df = pd.read_excel(f'attendance_files/attendance_{date_str}.xlsx')
    except FileNotFoundError:
        return

    for index, row in df.iterrows():
        if row['Time'] > '12:00:00' and row['Status'] == 'Present':
            row['Status'] = 'Absent'
            row['Time'] = '12:00:01'  # Example value, adjust as needed

    df.to_excel(f'attendance_files/attendance_{date_str}.xlsx', index=False)
