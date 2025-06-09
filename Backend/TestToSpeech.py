import pygame  # Import pygame library for handling audio playback
import random  # Import random for generating random choices
import asyncio  # Import asyncio for asynchronous operations
import edge_tts  # Import edge tts for text-to-speech functionality
import os  # Import os for file path handling
from dotenv import dotenv_values  # Import dotenv for reading environment variables from a .env file
import logging  # Import logging for error handling

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the .env file in the Frontend directory
env_path = os.path.join(os.path.dirname(script_dir), "Frontend", ".env")
env_vars = dotenv_values(env_path)

# Get the AssistantVoice from environment variables with a default value
AssistantVoice = env_vars.get("AssistantVoice", "en-US-ChristopherNeural")

class TTSEngine:
    def __init__(self):
        self.initialized = False
        self.current_file = None
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.initialized = True

    def cleanup(self):
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass
            finally:
                self.initialized = False

    async def generate_audio(self, text):
        try:
            # Ensure the Data directory exists
            data_dir = os.path.join(script_dir, "Data")
            os.makedirs(data_dir, exist_ok=True)

            # Define the output file path
            file_path = os.path.join(data_dir, "speech.mp3")

            # Remove existing file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)

            # Create the communicate object with proper voice configuration
            communicate = edge_tts.Communicate(
                text=text,
                voice=AssistantVoice,
                pitch='+5Hz',
                rate='+13%'
            )

            await communicate.save(file_path)
            self.current_file = file_path
            return True
        except Exception as e:
            logging.error(f"Error generating audio: {e}")
            return False

    def play_audio(self, callback=None):
        try:
            if not self.initialized:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                self.initialized = True

            if self.current_file and os.path.exists(self.current_file):
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    if callback and callback() is False:
                        break
                    pygame.time.Clock().tick(10)

                return True
        except Exception as e:
            logging.error(f"Error playing audio: {e}")
        finally:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        return False

def TextToSpeech(text, callback=lambda r=None: True):
    engine = TTSEngine()
    try:
        # Split text into sentences
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        
        if len(sentences) > 4 and len(text) > 250:
            # For long text, speak first two sentences and add a note
            short_text = ". ".join(sentences[:2]) + ". "
            note = random.choice([
                "The rest of the text is now on the chat screen, sir.",
                "You can find the complete text on the chat screen, sir.",
                "Please check the chat screen for the full message, sir.",
                "The remaining information is displayed on your screen, sir."
            ])
            asyncio.run(engine.generate_audio(short_text + note))
        else:
            # For shorter text, speak everything
            asyncio.run(engine.generate_audio(text))

        # Play the generated audio
        return engine.play_audio(callback)

    except Exception as e:
        logging.error(f"Error in TextToSpeech: {e}")
        return False
    finally:
        engine.cleanup()

if __name__ == "__main__":
    print("Text-to-Speech Test")
    print("Enter 'exit' to quit")
    print("Assistant Voice:", AssistantVoice)
    
    while True:
        try:
            text = input("\nEnter text to speak: ").strip()
            if text.lower() == 'exit':
                break
            if text:
                TextToSpeech(text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logging.error(f"Error: {e}")
