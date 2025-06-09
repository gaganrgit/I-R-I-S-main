import edge_tts
import asyncio
from dotenv import dotenv_values
import os
import subprocess
import logging
import pygame
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(script_dir), "Frontend", ".env")

# Ensure Frontend/Files directory exists
files_dir = os.path.join(os.path.dirname(script_dir), "Frontend", "Files")
os.makedirs(files_dir, exist_ok=True)

try:
    env_vars = dotenv_values(env_path)
    AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")
    # Get speech rate from .env or use default
    SpeechRate = env_vars.get("SpeechRate", "+0%")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    AssistantVoice = "en-CA-LiamNeural"
    SpeechRate = "+0%"  # Default speech rate (normal)

class TTSEngine:
    def __init__(self):
        self.initialized = False
        self.current_file = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing audio: {e}")

    def cleanup(self):
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass
            finally:
                self.initialized = False

    async def generate_audio(self, text, rate=None):
        try:
            speech_file = os.path.join(files_dir, "Speech.mp3")
            
            # Remove existing file if it exists
            if os.path.exists(speech_file):
                try:
                    os.remove(speech_file)
                except:
                    pass

            # Standard approach - no rate modification
            if not rate or rate == "+0%":
                communicate = edge_tts.Communicate(text, AssistantVoice)
                await communicate.save(speech_file)
            else:
                # Use the standard approach with simple text
                communicate = edge_tts.Communicate(text, AssistantVoice)
                await communicate.save(speech_file)
                # Note: We're ignoring the rate parameter for now, but using the standard API
                # This ensures compatibility while we figure out how to properly implement rate control
                
            self.current_file = speech_file
            return True
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return False

    def play_audio(self):
        try:
            if not self.initialized:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                self.initialized = True

            if self.current_file and os.path.exists(self.current_file):
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                return True
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            # Fallback to Windows Media Player if pygame fails
            try:
                subprocess.run(['start', 'wmplayer', self.current_file], shell=True)
                return True
            except Exception as e:
                logger.error(f"Error with fallback playback: {e}")
        finally:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        return False

def TextToSpeech(text, rate=None):
    try:
        if not text or not isinstance(text, str):
            logger.error("Invalid text input")
            return False
        
        # For now, we'll ignore the rate parameter
        # This ensures compatibility until we can properly implement rate control
        engine = TTSEngine()
        try:
            if asyncio.run(engine.generate_audio(text)):
                return engine.play_audio()
            return False
        finally:
            engine.cleanup()
    except Exception as e:
        logger.error(f"Error in TextToSpeech: {e}")
        return False

if __name__ == "__main__":
    # Test the TTS functionality
    test_text = "Hello, this is a test of the text to speech system."
    print(f"Testing TTS with voice: {AssistantVoice}")
    success = TextToSpeech(test_text)
    print(f"TTS test {'successful' if success else 'failed'}") 