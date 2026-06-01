from pathlib import Path
from faster_whisper import WhisperModel
import sounddevice as sd
import speech_recognition as sr
import asyncio
import numpy as np

 
current_dir = Path(__file__).parent

# 'base' is significantly faster than 'small' on CPU
# Switch back to 'small' if accuracy feels insufficient
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    download_root=current_dir / "models" / "faster-whisper"
)

def record_audio(duration=5, samplerate=16000, silence_threshold=0.01, silence_duration=3):
    """
    Record audio and stop early if silence lasts more than silence_duration seconds.
    
    Args:
        duration: Maximum recording time in seconds
        samplerate: Sample rate in Hz
        silence_threshold: Audio level below this is considered silence
        silence_duration: Seconds of silence before stopping (default 3)
    """
    print("🎙️ Recording...")
    
    chunk_size = int(samplerate * 0.1)  # 100ms chunks for responsiveness
    silence_chunks = int(silence_duration / 0.1)  # How many silent chunks = stop
    consecutive_silent = 0
    audio_chunks = []
    
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='float32', blocksize=chunk_size)
    stream.start()
    
    try:
        max_chunks = int(duration / 0.1)  # Maximum number of chunks
        chunks_recorded = 0
        
        # while chunks_recorded < max_chunks:
        while True: # recording infinitely until silence is detected
            # stream.read returns a tuple (data, overflow)
            data, overflow = stream.read(chunk_size)
            audio_chunks.append(data)
            chunks_recorded += 1
            
            # Check if this chunk is silent
            rms = np.sqrt(np.mean(data ** 2))
            
            if rms < silence_threshold:
                consecutive_silent += 1
                if consecutive_silent >= silence_chunks:
                    print(f"⏹️ Silence detected for {silence_duration}s, stopping recording")
                    break
            else:
                consecutive_silent = 0
    
    finally:
        stream.stop()
        stream.close()
    
    audio = np.concatenate(audio_chunks)
    return audio.flatten()

def transcribe(audio_array):
    initial_prompt = 'adis'
    segments, info = model.transcribe(audio_array,language='en', vad_filter = True, initial_prompt=initial_prompt,  beam_size=1)  # beam_size=1 is fastest
    text = " ".join([seg.text for seg in segments])
    return text.strip()

def listen_to_user():
    audio = record_audio()
    print(f'audio type: {audio.dtype}, audio shape: {audio.shape}')
    result = transcribe(audio)
    return result


# USING SR-PYTHON MODULE:
def listen_to_user2():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0  
    recognizer.non_speaking_duration = 0.5

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            print("\nListening... Speak now!")
            audio_data = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio_data)
                return text

            except sr.UnknownValueError:
                print("\nSorry, I could not understand the audio.")

            except sr.RequestError as e:
                print(f"\nCould not request results from Google service; {e}")

        except sr.WaitTimeoutError:
            print("\nNo speech detected. Please try again.")
        except KeyboardInterrupt:
            print("\nListening stopped by user.")
        return None




