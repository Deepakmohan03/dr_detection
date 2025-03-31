import os
import shutil
import numpy as np
import PIL
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model("retina_weights.hdf5")

# Labels for classification
labels = {
    0: 'Mild Diabetic Retinopathy',
    1: 'Moderate Diabetic Retinopathy',
    2: 'No Diabetic Retinopathy',
    3: 'Proliferate Diabetic Retinopathy',
    4: 'Severe Diabetic Retinopathy'
}

# Define paths
INPUT_FOLDER = r"C:\Users\Deepak\Desktop\Diabetic-Retinopathy-Detector-using-Ensemble-Learning-main\dataset\image"  # Folder containing images to be classified
OUTPUT_FOLDER = r"C:\Users\Deepak\Desktop\Diabetic-Retinopathy-Detector-using-Ensemble-Learning-main\dataset\prediction"  # Folder where sorted images will be stored

# Ensure output directories exist without changing filenames
for label in labels.values():
    os.makedirs(os.path.join(OUTPUT_FOLDER, label), exist_ok=True)

# Function to classify and move images without renaming
def classify_and_sort_images():
    for filename in os.listdir(INPUT_FOLDER):
        file_path = os.path.join(INPUT_FOLDER, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        try:
            # Preprocess the image
            img = PIL.Image.open(file_path).convert("RGB").resize((256, 256))
            img = np.asarray(img, dtype=np.float32) / 255.0
            img = img.reshape(1, 256, 256, 3)
            
            # Make prediction
            prediction = model.predict(img)
            predicted_label = labels[np.argmax(prediction)]
            
            # Move file to corresponding folder without renaming
            dest_folder = os.path.join(OUTPUT_FOLDER, predicted_label)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_folder, filename))
            print(f"Moved {filename} -> {predicted_label}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    classify_and_sort_images()
    print("Sorting complete!")
