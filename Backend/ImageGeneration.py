import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
from pathlib import Path
import signal
import sys

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nShutting down image generation service gracefully...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Get the directory where the script is located
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Setup paths
data_dir = script_dir / "Data"
env_path = project_root / "Frontend" / ".env"
data_file = project_root / "Frontend" / "Files" / "ImageGeneration.data"

# Create Data directory if it doesn't exist
data_dir.mkdir(exist_ok=True)

def get_api_key() -> str | None:
    """Get the API key from the .env file."""
    try:
        api_key = get_key(env_path, 'HuggingFaceAPIKey')
        if not api_key:
            print(f"Error: HuggingFaceAPIKey not found in {env_path}")
            return None
        print(f"Successfully loaded API key from {env_path}")
        return api_key
    except Exception as e:
        print(f"Error reading API key: {str(e)}")
        return None

# Function to open and display images based on a given prompt
def open_images(prompt):
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores
    
    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in Files:
        image_path = data_dir / jpg_file
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the next image
        except IOError as e:
            print(f"Unable to open {image_path}: {str(e)}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Async function to send a query to the Hugging Face API
async def query(payload, headers):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return None
        return response.content
    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return None

# Async function to generate images based on the given prompt
async def generate_images(prompt: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}"}
    tasks = []
    
    # Create 4 image generation tasks
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload, headers))
        tasks.append(task)
    
    print("Generating images...")
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    success = False
    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                output_path = data_dir / f"{prompt.replace(' ', '_')}{i + 1}.jpg"
                output_path.write_bytes(image_bytes)
                print(f"Saved image {i + 1}")
                success = True
            except Exception as e:
                print(f"Error saving image {i + 1}: {str(e)}")
    
    return success

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    api_key = get_api_key()
    if not api_key:
        return False
    
    try:
        success = asyncio.run(generate_images(prompt, api_key))
        if success:
            open_images(prompt)
        return success
    except Exception as e:
        print(f"Error generating images: {str(e)}")
        return False

# Main loop to monitor for image generation requests
def main():
    print("Image Generation Service Started")
    print(f"Monitoring {data_file} for requests...")
    
    while True:
        try:
            # Check if data file exists
            if not data_file.exists():
                print(f"Data file not found: {data_file}")
                sleep(1)
                continue
                
            # Read the status and prompt from the data file
            with open(data_file, "r") as f:
                data = f.read().strip()
                if not data:
                    data = "None,False"
                prompt, status = [x.strip() for x in data.split(",")]
            
            # If the status indicates an image generation request
            if status.lower() == "true":
                print(f"Generating images for prompt: {prompt}")
                # Update status to processing
                with open(data_file, "w") as f:
                    f.write(f"{prompt},processing")
                
                # Generate images
                success = GenerateImages(prompt=prompt)
                
                # Reset the status in the file after generating images
                with open(data_file, "w") as f:
                    if success:
                        f.write(f"{prompt},completed")
                    else:
                        f.write(f"{prompt},failed")
            else:
                sleep(1)  # Wait for 1 second before checking again
                
        except KeyboardInterrupt:
            print("\nShutting down image generation service...")
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nImage generation service stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
