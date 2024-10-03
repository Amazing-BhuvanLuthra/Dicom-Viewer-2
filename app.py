import os
import pydicom
from flask import Flask, request, render_template, redirect, flash
from PIL import Image
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
IMAGE_FOLDER = 'static/images'

# Ensure the static/images directory exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def save_dicom_as_png(ds, output_path):
    # Assuming the pixel data is in the ds.PixelData and needs to be reshaped
    pixel_array = ds.pixel_array  # Read pixel data
    # Normalize pixel values to [0, 255] for display purposes
    pixel_array = (np.maximum(pixel_array, 0) / pixel_array.max()) * 255.0
    pixel_array = pixel_array.astype(np.uint8)  # Convert to uint8 for image saving

    image = Image.fromarray(pixel_array)
    image.save(output_path)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.dcm'):
        dicom_path = os.path.join(IMAGE_FOLDER, file.filename)
        file.save(dicom_path)

        # Read the DICOM file
        ds = pydicom.dcmread(dicom_path)

        # Extracting metadata
        metadata = {
            'Patient Name': ds.PatientName,
            'Patient ID': ds.PatientID,
            'Modality': ds.Modality,
            'Study Date': ds.StudyDate,
            # Add more metadata fields as needed
        }

        # Define the path for the PNG image
        image_path = os.path.join(IMAGE_FOLDER, file.filename.replace('.dcm', '.png'))

        # Check if the image already exists, if not convert and save it
        if not os.path.exists(image_path):
            save_dicom_as_png(ds, image_path)

        return render_template('view_dicom.html', metadata=metadata, image=image_path)
    
    flash('File type not allowed. Please upload a DICOM file.')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
