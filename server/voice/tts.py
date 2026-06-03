import os
import warnings
import io

# suppress pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# suppress pkg_resources deprecation warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources is deprecated.*')

import edge_tts
import asyncio
import pygame

# Characters to avoid/remove from input text (markdown special characters)
CHARS_TO_AVOID = ['-', '*', '#', '`', '_', '[', ']', '(', ')', '{', '}', '\\', '|', '~', '^']

def clean_text(text: str) -> str:
    """Remove markdown and special characters from text while preserving readability."""
    for char in CHARS_TO_AVOID:
        text = text.replace(char, '')
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text

async def _generate_audio(text: str, output_file: str, voice: str = "en-GB-RyanNeural"):
    """Calls the Edge-TTS API to generate the hyper-realistic voice."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def speak_to_user(text: str, voice: str = "en-GB-RyanNeural"):
    """generates AI audio and plays it instantly."""
    # Clean the text from markdown and special characters
    text = clean_text(text)
    print(f"Assistant: {text}")
    
    audio_file = "response.mp3"
    
    # generate the audio file asynchronously
    asyncio.run(_generate_audio(text, audio_file, voice))
    
    # play the audio file
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    
    # wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    # clean up the system
    pygame.mixer.music.unload()
    pygame.mixer.quit()
    if os.path.exists(audio_file):
        os.remove(audio_file)


async def _generate_audio_bytes(text: str, voice: str) -> bytes:
    """Generates audio and returns raw MP3 bytes (no file written)."""
    communicate = edge_tts.Communicate(text, voice)
    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])
    buffer.seek(0)
    return buffer.read()

async def synthesize_to_bytes(text: str, voice: str = "en-GB-RyanNeural") -> bytes:
    """Returns MP3 audio bytes for the given text. No playback, no file."""
    # Clean the text from markdown and special characters
    text = clean_text(text)
    return await _generate_audio_bytes(text, voice)

# text = """To develop a comprehensive understanding of data structures and algorithms, consider the following step-by-step plan:
# * Begin by reviewing the fundamentals of programming, including data types, variables, control structures, functions, and object-oriented programming concepts, to ensure a solid foundation for learning data structures and algorithms.
# * Familiarize yourself with basic data structures such as arrays, linked lists, stacks, and queues, and practice implementing them in your preferred programming language."""
# speak_to_user(text)

# text = "i have uploaded all the files to the drive as you said. and its currently 8:50 pm. taking about the weather, its 36°C and cloudy. "
# audio_b64 = synthesize_to_bytes(text)
# print(len(audio_b64), "bytes of audio")


