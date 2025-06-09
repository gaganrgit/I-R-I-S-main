import os
import sys
import subprocess
import logging
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_chrome_installation():
    """Check if Chrome is installed and get its version."""
    try:
        if sys.platform == "win32":
            # Windows-specific command to get Chrome version
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        else:
            # For other platforms, try to get Chrome version from command line
            if sys.platform == "darwin":  # macOS
                cmd = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --version"
            else:  # Linux
                cmd = "google-chrome --version"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
    except Exception as e:
        logger.error(f"Error checking Chrome version: {e}")
        return None

def setup_chromedriver():
    """Set up ChromeDriver with proper version matching."""
    try:
        # Get Chrome version
        chrome_version = check_chrome_installation()
        if not chrome_version:
            logger.error("Chrome is not installed or version could not be determined")
            return False

        logger.info(f"Detected Chrome version: {chrome_version}")

        # Force a clean installation of ChromeDriver
        driver_manager = ChromeDriverManager()
        driver_path = driver_manager.install()
        
        # Fix the driver path to point to the actual executable
        if sys.platform == "win32":
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, "chromedriver.exe")
        
        if not os.path.exists(driver_path):
            logger.error(f"ChromeDriver not found at {driver_path}")
            return False

        logger.info(f"ChromeDriver installed at: {driver_path}")

        # Test the driver
        service = Service(driver_path)
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.quit()
        
        logger.info("ChromeDriver setup successful")
        return True

    except Exception as e:
        logger.error(f"Error setting up ChromeDriver: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Chrome and ChromeDriver...")
    if setup_chromedriver():
        print("Setup completed successfully!")
    else:
        print("Setup failed. Please check the error messages above.") 