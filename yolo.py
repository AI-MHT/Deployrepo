from ultralytics import YOLO
import os
import shutil
from flask import jsonify

input_folder = 'images'
output_plus_4 = 'resultat/plus_4_etages'
output_3 = 'resultat/3_etages'
output_2= 'resultat/2_etages'
output_1 = 'resultat/1_etage'
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