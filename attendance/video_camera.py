import cv2
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime
import os
from .models import Employee
from .excel_util import create_attendance_file_if_not_exists

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.current_attendees = set()  # Track current attendees
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
        processed_frame = self.process_frame(image)

        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()

    def process_frame(self, frame):
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                self.current_attendees.add(name)
                self.mark_attendance(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame

    def mark_attendance(self, name):
        date_str = datetime.now().strftime('%Y-%m-%d')
        attendance_file_path = os.path.join('attendance_files', f'attendance_{date_str}.xlsx')
        if not os.path.exists(attendance_file_path):
            create_attendance_file_if_not_exists()

        df = pd.read_excel(attendance_file_path)

        employee = Employee.objects.get(name=name)
        emp_id = employee.emp_id
        arrival_time = datetime.now().strftime('%H:%M:%S')

        if emp_id not in df['Employee ID'].values:
            new_row = {'Employee ID': emp_id, 'Name': name, 'Attendance': 'Present', 'Arrival Time': arrival_time}
            df = df.append(new_row, ignore_index=True)
        else:
            df.loc[df['Employee ID'] == emp_id, 'Attendance'] = 'Present'
            df.loc[df['Employee ID'] == emp_id, 'Arrival Time'] = arrival_time

        df.to_excel(attendance_file_path, index=False)

    def get_current_attendees(self):
        return list(self.current_attendees)
