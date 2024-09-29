from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tensorflow as tf  # or use PyTorch depending on your model
import numpy as np

from keras.src.saving import load_model
from keras.api.preprocessing import image

MODEL_NAME = [
    "Baseline",
    "VGG",
    "Inception",
    "ResNet",
]
MODEL_PATH = [
    "food101/models/baseline_model_22_class.keras",
    "food101/models/vgg_model_22_class.keras",
    "food101/models/inception_model_22_class.keras",
    "food101/models/resnet_model_22_class.keras",
]
FOOD_LIST = [
    "Apple Pie",
    "Baby Back Ribs",
    "Bibimbap",
    "Caesar Salad",
    "Cheesecake",
    "Chicken Curry",
    "Chicken Wings",
    "Club Sandwich",
    "Donuts",
    "Dumplings",
    "French Fries",
    "Hot Dog",
    "Hamburger",
    "Frozen Yogurt",
    "Pizza",
    "Ramen",
    "Steak",
    "Ice Cream",
    "Waffles",
    "Spring Rolls",
    "Sushi",
    "Fish and Chips",
]


@csrf_exempt
def classify(request):
    if request.method == "POST" and request.FILES.get("file"):
        print("Received POST request")
        file = request.FILES["file"]
        print("File received")

        # Save the file temporarily
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_path = f"uploads/{file_name}"
        print(f"File saved at {file_path}")

        try:
            # Load and preprocess the image
            img = image.load_img(file_path, target_size=(299, 299))
            print("Image loaded")
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0
            print("Image preprocessed")

            # Run predictions on all models
            predictions = []
            for i, model_path in enumerate(MODEL_PATH):
                print(f"Running prediction with model {MODEL_NAME[i]}")
                # Load model
                model = load_model(model_path)
                # Make predictions
                prediction = model.predict(img_array)
                first_predicted_index = np.argmax(prediction)
                first_predicted_percentage = float(prediction[0][first_predicted_index])
                first_predicted_label = FOOD_LIST[first_predicted_index]
                prediction[0][first_predicted_index] = -1
                second_predicted_index = np.argmax(prediction)
                second_predicted_percentage = float(
                    prediction[0][second_predicted_index]
                )
                second_predicted_label = FOOD_LIST[second_predicted_index]
                print(
                    f"Complete prediction with model {MODEL_NAME[i]}: {first_predicted_label} with prob {first_predicted_percentage},  {second_predicted_label} with prob {second_predicted_percentage}"
                )
                predictions.append(
                    {
                        "model": MODEL_NAME[i],
                        "first_predicted_class": first_predicted_label,
                        "second_predicted_class": second_predicted_label,
                        "first_predicted_prob": first_predicted_percentage,
                        "second_predicted_prob": second_predicted_percentage,
                    }
                )

            print("Image prediction completed")
            return JsonResponse({"predictions": predictions}, status=200)

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                print("File deleted")

    return JsonResponse({"error": "Invalid request"}, status=400)
