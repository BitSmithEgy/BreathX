from django.shortcuts import render, get_object_or_404, redirect
from .forms import UploadFileForm
from .models import UploadedImage
import os
import tensorflow as tf
import numpy as np
import cv2
from django.core.mail import send_mail, EmailMessage
import csv
from django.core.files.storage import default_storage

def home(request):
    return render(request, 'UserView/index.html')

def prediction(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            handle_uploaded_file(request.FILES['image'])
            return redirect('result', pk=instance.pk)
    else:
        form = UploadFileForm()

    return render(request, 'UserView/prediction.html', {'form': form})

def handle_uploaded_file(file):
    file_path = os.path.join('media/uploads/', file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def result(request, pk):
    uploaded_image = get_object_or_404(UploadedImage, pk=pk)
    result = perform_image_classification(uploaded_image.image.path)
    return render(request, 'UserView/result.html', {'result': result, 'pk': pk})

def perform_image_classification(image_path):
    model = tf.keras.models.load_model('./model/brathX_model11.h5')
    img = cv2.imread(image_path)

    resize = tf.image.resize(img, (256, 256))
    yhat = model.predict(np.expand_dims(resize/255, 0))

    classes = ["COVID 19", "NORMAL", "Pneumonia Bacterial", "Pneumonia Viral", "TUBERCULOSIS"]
    pred_class = classes[np.argmax(yhat)]

    return f"{pred_class} ({np.round(yhat.max()*100, 2)}%)"

def booking(request, pk, result):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        email = request.POST.get('email')
        diabetes = request.POST.get('diabetes', False)
        blood_pressure = request.POST.get('bloodPressure', False)

        uploaded_image = get_object_or_404(UploadedImage, pk=pk)
        csv_file_path = save_form_data_to_csv(name, age, email, diabetes, blood_pressure)

        subject = 'Booking Information'
        message = 'Please find the booking information attached.'
        recipient_list = ['mo7885425@gmail.com']

        attachments = [
            (os.path.basename(csv_file_path), open(csv_file_path, 'rb').read(), 'text/csv'),
            (os.path.basename(uploaded_image.image.name), open(uploaded_image.image.path, 'rb').read(), 'image/jpeg'),
        ]

        email = EmailMessage(subject, message, to=recipient_list)

        for attachment in attachments:
            email.attach(*attachment)

        email.send()
        return redirect('download', csv_file_path=csv_file_path)

    return render(request, 'UserView/booking.html', {'pk': pk, 'result': result})

def save_form_data_to_csv(name, age, email, diabetes, blood_pressure):
    csv_file_path = f'{name}_booking_info.csv'

    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Age', 'Email', 'Diabetes', 'Blood Pressure']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'Name': name, 'Age': age, 'Email': email, 'Diabetes': diabetes, 'Blood Pressure': blood_pressure})

    return csv_file_path

from django.http import HttpResponse

def download(request, csv_file_path):
    # Create a response with the content type for CSV
    response = HttpResponse(content_type='text/csv')
    
    # Set the Content-Disposition header to prompt download
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(csv_file_path)}"'

    # Open the CSV file and write its content to the response
    with open(csv_file_path, 'rb') as csv_file:
        response.write(csv_file.read())

    return response
