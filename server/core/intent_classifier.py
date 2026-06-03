import os
import re
import string
import pickle
import joblib
import warnings
from pathlib import Path

# Suppress sklearn version mismatch warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*Trying to unpickle estimator.*')


def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # convert to lowercase
    text = text.lower()
    # remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # remove special characters and punctuation, keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # strip leading and trailing whitespace
    text = text.strip()
    return text


def classify_intent(input_text: str) -> dict:
    try:
        # preprocessing
        cleaned_text = preprocess_text(input_text)
        
        if not cleaned_text:
            return {
                'intent': None,
                'confidence': 0.0,
                'success': False,
                'error': 'Input text is empty after preprocessing'
            }
        

        current_dir = Path(__file__).parent
        
        intent_classifier_path = current_dir / 'models' / 'intent_classifier.pkl'
        label_encoder_path = current_dir / 'models' / 'label_encoder.pkl'
        
        
        if not intent_classifier_path.exists():
            raise FileNotFoundError(f"Intent classifier model not found at {intent_classifier_path}")
        if not label_encoder_path.exists():
            raise FileNotFoundError(f"Label encoder not found at {label_encoder_path}")
        
        # load dthe pipeline and encoder
        model_pipeline = joblib.load(str(intent_classifier_path))
        label_encoder = joblib.load(str(label_encoder_path))
        
        # make prediction
        prediction = model_pipeline.predict([cleaned_text])
        
        # get prediction probabilities for confidence score
        if hasattr(model_pipeline, 'predict_proba'):
            probabilities = model_pipeline.predict_proba([cleaned_text])
            confidence = float(max(probabilities[0]))
        else:
            confidence = 1.0
        
        # decode the prediction to get the intent label
        predicted_label_index = prediction[0]
        intent = label_encoder.inverse_transform([predicted_label_index])[0]
        
        return {
            'intent': intent,
            'confidence': confidence,
            'success': True
        }
        
    except FileNotFoundError as e:
        return {
            'intent': None,
            'confidence': 0.0,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'intent': None,
            'confidence': 0.0,
            'success': False,
            'error': f'Classification error: {str(e)}'
        }



# if __name__ == "__main__":
#     while True:
#         user_input = input("Enter a message to classify intent (or 'exit' to quit): ")
#         if user_input.lower() == 'exit':
#             break
#         result = classify_intent(user_input)
#         print(f"Intent: {result['intent']}, Confidence: {result['confidence']:.2f}, Success: {result['success']}")
#         if not result['success']:
#             print(f"Error: {result.get('error', 'Unknown error')}")
#    
