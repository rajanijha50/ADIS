import edge_tts
import asyncio
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

async def _generate_audio(text: str, output_file: str, voice: str = "en-US-AriaNeural"):
    """Calls the Edge-TTS API to generate the hyper-realistic voice."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def speak_to_user(text: str, voice: str = "en-US-AriaNeural"):
    """Generates AI audio and plays it instantly."""
    print(f"Assistant: {text}")
    
    audio_file = "response.mp3"
    
    # Generate the audio file asynchronously
    asyncio.run(_generate_audio(text, audio_file, voice))
    
    # Play the audio file
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    # Clean up the system
    pygame.mixer.music.unload()
    pygame.mixer.quit()
    if os.path.exists(audio_file):
        os.remove(audio_file)