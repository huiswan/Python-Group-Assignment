import numpy as np
import cv2

from tensorflow.keras.models import load_model

class OCR :
    def __init__(self, model_path="./digit_recognition_model.h5"):
        self.model = load_model(model_path)

    def get_model(self) :
        return self.model

    def get_predection(self, boxes, result_threshold=0.7):
        result = []
        for image in boxes:
            # Prepare the image from individual boxes
            img = np.asarray(image)
            img = img[4:img.shape[0] - 4, 4:img.shape[1] -4]
            img = cv2.resize(img, (28, 28))
            img = img / 255
            img = img.reshape(1, 28, 28, 1)

            predictions = self.model.predict(img)
            classIndex = np.argmax(predictions, axis=1)
            probabilityValue = np.amax(predictions)

            # Only if the predicted value has a probability
            # greater than result_threshold, we consider it
            if probabilityValue >= result_threshold:
                result.append(classIndex[0])
            else:
                result.append(0)
        return result
