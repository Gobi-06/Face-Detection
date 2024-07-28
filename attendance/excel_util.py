import os
import pandas as pd
import datetime

def create_attendance_file_if_not_exists():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    attendance_file_path = os.path.join('attendance_files', f'attendance_{date_str}.xlsx')

    if not os.path.exists(attendance_file_path):
        df = pd.DataFrame(columns=['Employee ID', 'Name', 'Attendance', 'Arrival Time'])
        os.makedirs(os.path.dirname(attendance_file_path), exist_ok=True)
        df.to_excel(attendance_file_path, index=False)

def mark_absent_for_latecomers():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    attendance_file_path = os.path.join('attendance_files', f'attendance_{date_str}.xlsx')
    cutoff_time_full = datetime.datetime.strptime(f"{date_str} 10:00:00", "%Y-%m-%d %H:%M:%S")
    cutoff_time_half = datetime.datetime.strptime(f"{date_str} 11:00:00", "%Y-%m-%d %H:%M:%S")
    cutoff_time_absent = datetime.datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")

    if not os.path.exists(attendance_file_path):
        return

    df = pd.read_excel(attendance_file_path)

    for index, row in df.iterrows():
        if row['Attendance'] == 'Absent':
            employee_id = row['Employee ID']
            arrival_time = get_employee_arrival_time(employee_id)
            if arrival_time > cutoff_time_absent:
                df.at[index, 'Attendance'] = 'Absent'
            elif arrival_time > cutoff_time_half:
                df.at[index, 'Attendance'] = 'Half'
            elif arrival_time > cutoff_time_full:
                df.at[index, 'Attendance'] = 'Full'
            else:
                df.at[index, 'Attendance'] = 'Full'

    df.to_excel(attendance_file_path, index=False)

def get_employee_arrival_time(emp_id):
    return datetime.datetime.now()
