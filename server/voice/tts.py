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

async def _generate_audio(text: str, output_file: str, voice: str = "en-GB-RyanNeural"):
    """Calls the Edge-TTS API to generate the hyper-realistic voice."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def speak_to_user(text: str, voice: str = "en-GB-RyanNeural"):
    """generates AI audio and plays it instantly."""
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
    return await _generate_audio_bytes(text, voice)

# text = "i have uploaded all the files to the drive as you said. and its currently 8:50 pm. taking about the weather, its 36°C and cloudy. "
# speak_to_user(text)

# text = "i have uploaded all the files to the drive as you said. and its currently 8:50 pm. taking about the weather, its 36°C and cloudy. "
# audio_b64 = synthesize_to_bytes(text)
# print(len(audio_b64), "bytes of audio")
