from flask import Flask, request, jsonify, render_template
import os
import time
import shutil
import pytesseract
import exifread
import csv
from geopy.geocoders import Nominatim
from PIL import Image
import requests
from io import BytesIO
from ultralytics import YOLO
from math import radians, sin, cos, sqrt, atan2
import yagmail
from datetime import datetime
import os
from PIL import Image
app = Flask(__name__)

# Import the functions from createjson.py
# from createjson import read_csv, calculate_stats, write_json


# # Define your create_json function
# def create_json(csv_file_path_json, json_file_path_json):
#     data = read_csv(csv_file_path_json)
#     stats = calculate_stats(data)
#     write_json(stats, json_file_path_json)

# Define a function to perform OCR on the image
def ocr_image(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img)
        return text.lower()

# Define a function to check if specific words are present in the OCR result
def check_words_in_image(image_path, words):
    ocr_text = ocr_image(image_path)
    for word in words:
        if word.lower() in ocr_text:
            return True
    return False

# Function to convert coordinates from degrees, minutes, seconds to decimal
def convert_to_decimal(coord, ref):
    degrees = coord[0].num / coord[0].den
    minutes = coord[1].num / coord[1].den / 60
    seconds = coord[2].num / coord[2].den / 3600
    decimal_degrees = degrees + minutes + seconds
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees

# Function to get city and neighborhood from GPS coordinates
def get_city_and_neighborhood(latitude, longitude):
    geolocator = Nominatim(user_agent="city_extractor")
    location = geolocator.reverse((latitude, longitude), language='en')
    address = location.raw['address']
    city = address.get('city', '')
    if not city:
        city = address.get('town', '')
    if not city:
        city = address.get('village', '')
    if not city:
        city = address.get('county', '')
    neighborhood = address.get('suburb', '')
    if not neighborhood:
        neighborhood = address.get('quarter', '')
    return city, neighborhood

# Function to get image information such as latitude, longitude, city, and neighborhood
def get_image_info(image_path, folder_name):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        image_info = {'image_path': image_path, 'Number of floor': folder_name}  # Include image_path in the dictionary
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            latitude = tags['GPS GPSLatitude'].values
            longitude = tags['GPS GPSLongitude'].values
            altitude = None
            if 'GPS GPSAltitude' in tags:
                altitude = tags['GPS GPSAltitude'].values[0].num / tags['GPS GPSAltitude'].values[0].den
            dimensions = None
            if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
                dimensions = (tags['EXIF ExifImageWidth'].values, tags['EXIF ExifImageLength'].values)
            orientation = None
            if 'Image Orientation' in tags:
                orientation = tags['Image Orientation'].printable
            latitude = convert_to_decimal(latitude, tags['GPS GPSLatitudeRef'].values)
            longitude = convert_to_decimal(longitude, tags['GPS GPSLongitudeRef'].values)
            city, neighborhood = get_city_and_neighborhood(latitude, longitude)
            taken_date = None
            if 'EXIF DateTimeOriginal' in tags:
                taken_date = str(tags['EXIF DateTimeOriginal'])
            image_info.update({'latitude': latitude, 'longitude': longitude, 'altitude': altitude, 'dimensions': dimensions, 'orientation': orientation, 'city': city, 'neighborhood': neighborhood, 'taken_date': taken_date})
        return image_info

# Function to load data from b2b.csv file
def load_b2b_data(b2b_file_path):
    b2b_data = []
    with open(b2b_file_path, 'r', newline='') as b2b_file:
        reader = csv.reader(b2b_file, delimiter=';')
        next(reader)
        for row in reader:
            b2b_data.append(row)
    return b2b_data

# Function to calculate distance between two GPS coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
    radius_earth = 6371000
    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad
    a = sin(d_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius_earth * c
    return distance

def send_email():
    sender_email = 'workoutaiman@gmail.com'
    sender_password = 'mxjl imza srho djmn'
    receiver_email = 'workoutaiman@hotmail.com'
    current_date = datetime.now().strftime("%d_%m_%Y")

    yag = yagmail.SMTP(sender_email, sender_password)
    
    file_path = f'Rapport.pdf'
    subject = f"CSV File - {current_date}"
    body = "Veuillez trouver le fichier CSV ci-joint et vous devez le vérifier"

    yag.send(
        to=receiver_email,
        subject=subject,
        contents=body,
        attachments=file_path,
    )
def create_latex_from_images(image_folder, Rapport_tex, rapport):
    # LaTeX document structure
    header = r'''
    \documentclass[a4paper,12pt]{article}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{graphicx}
    \usepackage{geometry}
    \usepackage{float}
    \geometry{a4paper, margin=1in}
    \begin{document}
    \title{Rapport}
    \author{}
    \date{}
    \maketitle
    \noindent
    ''' + rapport + r'''
    \newpage
    '''

    footer = r'''
    \end{document}
    '''

    body = ''

    # Get list of images
    images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    image_count = 0

    for image_file in images:
        image_path = os.path.join(image_folder, image_file)
        with Image.open(image_path) as img:
            # Reduce resolution to 100 dpi
            img = img.resize((img.width // 5, img.height // 5))

            img_width, img_height = img.size

            # Convert pixels to inches (assuming 100 dpi)
            img_width_in = img_width / 100
            img_height_in = img_height / 100

            # Determine the scaling factor to fit the image within a half-page width
            max_width_in = 3.0  # Half of the 6-inch width for A4 with 1-inch margins
            scale = max_width_in / img_width_in

            if image_count % 2 == 0:
                body += r'\begin{figure}[H]\centering' + '\n'

            body += r'\includegraphics[width=%.2f\textwidth]{%s}' % (scale, image_path.replace('\\', '/'))

            if image_count % 2 == 1:
                body += r'\end{figure}' + '\n'
                body += r'\hfill'  # Add horizontal space between images
                body += r'\hspace{4px}'  # Add additional 4px of space

            image_count += 1

            if image_count % 8 == 0:
                body += r'\newpage' + '\n'

    # Close any unclosed figure environments
    if image_count % 2 != 0:
        body += r'\end{figure}' + '\n'

    # Combine header, body, and footer
    latex_content = header + body + footer

    # Write LaTeX content to .tex file
    with open(Rapport_tex, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    # Compile the .tex file to a PDF only
    os.system(f'pdflatex {Rapport_tex}')

# Define the folder containing images and the Rapport .tex file
image_folder = 'latex/images'
Rapport_tex = 'latex/Rapport.tex'
rapport = r'''
Ces images ne présentent aucune information utile. Veuillez les vérifier et, la prochaine fois, prenez des images qui respectent les règles suivantes :
\begin{itemize}
    \item Les bâtiments doivent être clairement visibles sur l'image.
    \item Pas de reflets.
    \item Pas d'image floue.
    \item Positionnement correct de l'image (par exemple, centré sur le bâtiment).
    \item L'image ne doit pas contenir d'obstructions (par exemple, ombres, reflets).
\end{itemize}
Si vous trouvez un problème, merci de contacter Mr Youssef MDEGHRI ALAOUI :
\begin{itemize}
    \item Email : youssef.mdeghrialaoui@orange.com
    \item Numéro de téléphone : +212600000000
\end{itemize}
'''

# Define the paths for CSV files
input_folder = 'images'
output_construction = 'resultat/construction'
output_plus_4 = 'resultat/plus_4_etages'
output_3 = 'resultat/3_etages'
output_2= 'resultat/2_etages'
output_1 = 'resultat/1_etage'
resultat_csv_path = 'resultat/image_info.csv'
b2b_csv_path = 'modeles/b2b.csv'
updated_csv_path = 'resultat/resultatfinal.csv'
csv_file_path_json='resultat/resultatfinal.csv'
json_file_path_json='../../../../orange/orange/src/Data/output1.json'
# Route to execute all functionalities
@app.route('/execute_all', methods=['POST'])
def execute_all():
    # YOLO inference
    yolo_inference()
    
    # Save image info
    save_image_info()
    
    # Update CSV
    update_csv()
    create_latex_from_images(input_folder, Rapport_tex, rapport)
    send_email()
    time.sleep(5)
    remove_contents(input_folder)
    
    return jsonify({'message': 'All functionalities executed successfully'})
def remove_contents(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    
    # Iterate over all the files and directories in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            # Remove file or directory
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
# Route to process images
def process_images():
    words_to_check = [
        "appart", "dh", "villa", "000", "magasin", "immob", "archi",
        "resid", "dence", "imme", "00", "oo", "architecture", "construction",
        "immobiliere", "immo", "bilie", "constru", "archi", "REGION"]

    os.makedirs(output_construction, exist_ok=True)
    detected_images = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            if check_words_in_image(image_path, words_to_check):
                shutil.move(image_path, os.path.join(output_construction, filename))
                detected_images.append(filename)

    return jsonify({'message': 'Images processed successfully', 'detected_images': detected_images})

# Route to perform inference using YOLO model
def yolo_inference():

    model_path = "modeles/plus_4_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)  # Create the output_plus_4
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.01)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_plus_4, filename)
                    shutil.move(input_path, output_final_path)  # Save the inferred image to output_plus_4
                    processed_images.append(filename)


    model_path = "modeles/3_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)  # Create the output_plus_4
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_3, filename)
                    shutil.move(input_path, output_final_path)  # Save the inferred image to output_plus_4
                    processed_images.append(filename)

    model_path = "modeles/2_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)  # Create the output_plus_4
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_2, filename)
                    shutil.move(input_path, output_final_path)  # Save the inferred image to output_plus_4
                    processed_images.append(filename)
    
    model_path = "modeles/1_etage.pt"
    os.makedirs(output_plus_4, exist_ok=True)  # Create the output_plus_4
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_1, filename)
                    shutil.move(input_path, output_final_path)  # Save the inferred image to output_plus_4
                    processed_images.append(filename)

    return jsonify({'message': 'YOLO inference completed', 'processed_images': processed_images})

# Route to save image information to CSV
def save_image_info():
    base_path = os.path.join(os.getcwd(), 'resultat')  # Assuming the folders are located in the current working directory
    image_info_list = []

    for root, dirs, files in os.walk(base_path):
        folder_name = os.path.basename(root)
        for filename in files:
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(root, filename)
                info = get_image_info(image_path, folder_name)
                if info:
                    image_info_list.append(info)

    # Save data to CSV
    csv_file_path = os.path.join(os.getcwd(), 'resultat/image_info.csv')
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['image_path', 'latitude', 'longitude', 'altitude', 'orientation', 'dimensions', 'Number of floor', 'taken_date', 'city', 'neighborhood']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for info in image_info_list:
            writer.writerow(info)

    return jsonify({'message': 'Image information saved to CSV', 'csv_file_path': csv_file_path})

def update_csv():
    b2b_data = load_b2b_data(b2b_csv_path)
    updated_rows = []

    with open(resultat_csv_path, 'r', newline='') as resultat_file:
        reader = csv.reader(resultat_file)
        header = next(reader)
        header.append('Nearby Activities')
        updated_rows.append(header)
        for row in reader:
            try:
                latitude = float(row[1])
                longitude = float(row[2])
                nearby_activities = []
                for b2b, ville, address, lat, lon in b2b_data:
                    if lat and lon:
                        try:
                            distance = calculate_distance(latitude, longitude, float(lat), float(lon))
                            if distance <= 2000:
                                nearby_activities.append(b2b)
                        except ValueError:
                            pass
                activities_str = ', '.join(nearby_activities)
                row.append(activities_str)
                updated_rows.append(row)
            except ValueError:
                pass

    with open(updated_csv_path, 'w', newline='') as updated_file:
        writer = csv.writer(updated_file)
        writer.writerows(updated_rows)

    return jsonify({'message': 'PDF file updated successfully'})
# Define the folder where images will be saved
UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Endpoint to upload images
@app.route('/uploadimages', methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST':
        # Check if the post request has the files part
        if 'images' not in request.files:
            return jsonify({'message': 'No images part in the request'}), 400

        files = request.files.getlist('images')

        uploaded_files = []
        for file in files:
            if file.filename == '':
                continue
            if file:
                # Save the file to the upload folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                uploaded_files.append(file.filename)

        return jsonify({'message': 'Images uploaded successfully', 'files': uploaded_files})

    return render_template('upload.html')



if __name__ == '__main__':
    app.run(debug=True)
