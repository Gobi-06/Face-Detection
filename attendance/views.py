from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from .models import Employee
from .face_recognition_util import VideoCamera, recognize_faces, mark_absent_for_latecomers
import datetime

camera = VideoCamera()

def home(request):
    now = datetime.datetime.now()
    context = {
        'current_date': now.strftime("%Y-%m-%d"),
        'current_time': now.strftime("%H:%M:%S")
    }
    return render(request, 'home.html', context)

def upload_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        emp_id = request.POST.get('emp_id')
        phone_no = request.POST.get('phone_no')
        image = request.FILES.get('image')
        
        if name and emp_id and phone_no and image:
            employee = Employee(name=name, emp_id=emp_id, phone_no=phone_no, image=image)
            employee.save()
            return redirect('upload_employee')
        else:
            return HttpResponse("All fields are required, including the image.")
    return render(request, 'upload_employee.html')

def start_attendance(request):
    return render(request, 'video_stream.html')

def stop_attendance(request):
    return redirect('home')

def mark_latecomers(request):
    mark_absent_for_latecomers()
    return HttpResponse("Marked absentees who arrived after 12:00 PM.")

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(camera),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def video_stream(request):
    # Fetch the current attendees list and pass it to the template
    attendees = camera.get_current_attendees()
    return render(request, 'video_stream.html', {'current_attendees': attendees})

def get_current_attendees(request):
    attendees = camera.get_current_attendees()
    return JsonResponse({'attendees': attendees})