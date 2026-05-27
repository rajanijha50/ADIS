import speech_recognition as sr

def listen_to_user() -> str:
    """Listens to the microphone and returns transcribed text using Whisper."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\nListening... (Speak now!)")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        recognizer.dynamic_energy_threshold = True  
        recognizer.pause_threshold = 2.0 

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=None)
            
            print("Processing with OpenAI Whisper...")
            text = recognizer.recognize_whisper(
                audio, 
                model="small.en", 
                load_options={"download_root": "./models"}
            )
            
            print(f"You said: {text}")
            return text.lower().strip()
            
        except sr.UnknownValueError:
            print("Whisper could not understand the audio.")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""