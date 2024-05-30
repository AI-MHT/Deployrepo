from ultralytics import YOLO
import os
import shutil
from flask import jsonify
import pytesseract
from PIL import Image
import csv

input_folder = 'images'
output_construction = 'resultat/construction'
output_plus_4 = 'resultat/plus_4_etages'
output_3 = 'resultat/3_etages'
output_2= 'resultat/2_etages'
output_1 = 'resultat/1_etage'
updated_csv_path = 'resultat/dataset.csv'

def load_existing_paths(csv_file):
    existing_paths = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_paths.add(row['image_path'])
    return existing_paths

# Function to perform OCR on the image
def ocr_image(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img)
        return text.lower()

# Function to check if specific words are present in the OCR result
def check_words_in_image(image_path, words):
    ocr_text = ocr_image(image_path)
    for word in words:
        if word.lower() in ocr_text:
            return True
    return False

# Route to process images
def process_images():
    words_to_check = [
        "appart", "dh", "villa", "000", "magasin", "immob", "archi",
        "resid", "dence", "imme", "00", "oo", "architecture", "construction",
        "immobiliere", "immo", "bilie", "constru", "archi", "REGION"]

    os.makedirs(output_construction, exist_ok=True)
    detected_images = []

    existing_paths = load_existing_paths(updated_csv_path)

    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            if image_path in existing_paths:
                os.remove(image_path)  # Delete the image if it's already processed
                print(f"Duplicate image {filename} found and deleted.")
            else:
                if check_words_in_image(image_path, words_to_check):
                    shutil.move(image_path, os.path.join(output_construction, filename))
                    detected_images.append(filename)

    return jsonify({'message': 'Images processed successfully', 'detected_images': detected_images})

# Route to perform inference using YOLO model
def yolo_inference():

    model_path = "modeles/plus_4_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.01)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_plus_4, filename)
                    shutil.move(input_path, output_final_path)
                    processed_images.append(filename)


    model_path = "modeles/3_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_3, filename)
                    shutil.move(input_path, output_final_path)
                    processed_images.append(filename)

    model_path = "modeles/2_etages.pt"
    os.makedirs(output_plus_4, exist_ok=True)
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_2, filename)
                    shutil.move(input_path, output_final_path)
                    processed_images.append(filename)
    
    model_path = "modeles/1_etage.pt"
    os.makedirs(output_plus_4, exist_ok=True)
    model = YOLO(model_path)
    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            results = model(input_path, conf=0.14)
            for result in results:
                if len(result) > 0:
                    output_final_path = os.path.join(output_1, filename)
                    shutil.move(input_path, output_final_path)
                    processed_images.append(filename)

    return jsonify({'message': 'YOLO inference completed', 'processed_images': processed_images})