from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import logging
import time

# Suppress all unnecessary logging
logging.basicConfig(level=logging.ERROR)
for logger_name in ['selenium', 'urllib3', 'WDM']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)
os.environ['WDM_LOG'] = 'off'
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, "Frontend", ".env")

# Load environment variables
env_vars = dotenv_values(env_path)
InputLanguage = env_vars.get("InputLanguage", "en-US")

# Create necessary directories
data_dir = os.path.join(script_dir, "Data")
os.makedirs(data_dir, exist_ok=True)

class SpeechRecognizer:
    def __init__(self):
        self.driver = None
        self.html_path = os.path.join(data_dir, "voice.html")
        self._write_html_file()
        self._setup_driver()
        
    def _write_html_file(self):
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Speech Recognition</title>
    <script>
        let recognition = null;
        let isRecognizing = false;
        
        function startRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
            
            recognition = new webkitSpeechRecognition();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onresult = function(event) {{
                document.getElementById('output').textContent = event.results[0][0].transcript;
                isRecognizing = false;
            }};
            
            recognition.onend = function() {{
                if (isRecognizing) {{
                    setTimeout(startRecognition, 100);
                }}
            }};
            
            recognition.onerror = function(event) {{
                if (event.error === 'no-speech') {{
                    if (isRecognizing) {{
                        setTimeout(startRecognition, 100);
                    }}
                }}
            }};
            
            isRecognizing = true;
            recognition.start();
        }}
        
        window.onload = function() {{
            startRecognition();
        }};
        
        window.onbeforeunload = function() {{
            if (recognition) {{
                recognition.stop();
            }}
        }};
    </script>
</head>
<body>
    <div id="output"></div>
</body>
</html>
"""
        with open(self.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--use-fake-device-for-media-stream")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.notifications": 2
        })
        
        try:
            # Get the ChromeDriver path and fix it to point to the actual executable
            driver_path = ChromeDriverManager().install()
            if os.name == 'nt':  # Windows
                driver_dir = os.path.dirname(driver_path)
                driver_path = os.path.join(driver_dir, "chromedriver.exe")
            
            if not os.path.exists(driver_path):
                logging.error(f"ChromeDriver not found at {driver_path}")
                return False
                
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.get(f"file:///{os.path.abspath(self.html_path)}")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "output"))
            )
            return True
        except Exception as e:
            logging.error(f"Driver setup error: {e}")
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None

    def recognize(self, timeout=10):
        if not self.driver:
            if not self._setup_driver():
                return ""
        
        try:
            start_time = time.time()
            last_text = ""
            
            while (time.time() - start_time) < timeout:
                try:
                    element = self.driver.find_element(By.ID, "output")
                    current_text = element.text.strip()
                    
                    if current_text and current_text != last_text:
                        return current_text.capitalize()
                    
                    last_text = current_text
                    time.sleep(0.1)
                    
                except Exception:
                    continue
            
            return ""
            
        except Exception as e:
            logging.error(f"Recognition error: {e}")
            return ""
        finally:
            self.cleanup()

if __name__ == "__main__":
    print("Speech Recognition Started. Speak into your microphone...")
    print("Press Ctrl+C to exit")
    
    recognizer = SpeechRecognizer()
    
    try:
        while True:
            text = recognizer.recognize()
            if text:
                print(f"Recognized: {text}")
    except KeyboardInterrupt:
        print("\nSpeech Recognition stopped by user")
    finally:
        recognizer.cleanup()
