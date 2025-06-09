# Required Libraries
from AppOpener import close, open as appopen  # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard-related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.
import sys  # Import sys for system-related functionalities.

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the Frontend/.env file
env_path = os.path.join(os.path.dirname(script_dir), "Frontend", ".env")

try:
    # Load environment variables
    env_vars = dotenv_values(env_path)
    GroqAPIKey = env_vars.get("GroqAPIKey")

    # Validate Groq API Key
    if not GroqAPIKey:
        print("[red]Error: GroqAPIKey not found in .env file[/red]")
        print(f"Please ensure GroqAPIKey is set in: {env_path}")
        sys.exit(1)

    # Initialize Groq client
    client = Groq(api_key=GroqAPIKey)

except Exception as e:
    print(f"[red]Error initializing Groq client: {str(e)}[/red]")
    print("Please check your API key and internet connection")
    sys.exit(1)

# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "zCubwf", "hgKElc", "LTKO0 sY7ric", "ZØLcW",
    "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc",
    "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe",
    "kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# List to store chatbot messages
messages = []

# System message to provide context to the chatbot
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.environ.get('Username')}, You're a content writer. You have to write content like letters."
}]

# Function to perform a Google search
def GoogleSearch(Topic):
    try:
        if not Topic or not isinstance(Topic, str) or not Topic.strip():
            print("[red]Error: Empty or invalid search query[/red]")
            return False
            
        Topic = Topic.strip()
        print(f"[yellow]Performing Google search for: {Topic}[/yellow]")
        
        # Use pywhatkit's search function to perform a Google search
        search(Topic)
        print(f"[green]Successfully searched for {Topic}[/green]")
        return True
        
    except Exception as e:
        print(f"[red]Error during Google search: {str(e)}[/red]")
        try:
            # Fallback method: directly open Google with the search query
            search_query = Topic.replace(" ", "+")
            webopen(f"https://www.google.com/search?q={search_query}")
            print(f"[yellow]Opened Google search for {Topic} (fallback method)[/yellow]")
            return True
        except Exception as fallback_error:
            print(f"[red]Fallback method also failed: {str(fallback_error)}[/red]")
            return False

# Function to generate content using AI and save it to a file
def Content(Topic):
    def OpenNotepad(File):
        try:
            default_text_editor = 'notepad.exe'  # Default text editor.
            # Make sure the file path is valid
            if os.path.exists(File):
                subprocess.Popen([default_text_editor, File])  # Open the file in Notepad.
                return True
            else:
                print(f"[red]Error: File does not exist: {File}[/red]")
                return False
        except Exception as e:
            print(f"[red]Error opening notepad: {str(e)}[/red]")
            return False

    def ContentWriterAI(prompt):
        try:
            messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Specify the AI model.
                messages=SystemChatBot + messages,  # Include system instructions and chat history.
                max_tokens=2048,  # Limit the maximum tokens in the response.
                temperature=0.7,  # Adjust response randomness.
                top_p=1,  # Use nucleus sampling for response diversity.
                stream=True,  # Enable streaming response.
                stop=None  # Allow the model to determine stopping conditions.
            )

            Answer = ""  # Initialize an empty string for the response.
            # Process streamed response chunks.
            for chunk in completion:
                if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                    Answer += chunk.choices[0].delta.content  # Append the content to the answer.

            Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
            messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages.
            return Answer

        except Exception as e:
            print(f"[red]Error generating content: {str(e)}[/red]")
            return f"I apologize, but I encountered an error while generating content: {str(e)}"

    try:
        # Clean the topic string to use as a filename
        Topic = Topic if not Topic.startswith("content ") else Topic.replace("content ", "", 1)
        
        # Ensure topic is not empty
        if not Topic.strip():
            print("[red]Error: Empty topic provided[/red]")
            return False
        
        # Generate content
        ContentByAI = ContentWriterAI(Topic)  

        # Create Data directory if it doesn't exist
        data_dir = os.path.join(script_dir, "Data")
        os.makedirs(data_dir, exist_ok=True)

        # Create a safe filename from the topic
        safe_filename = ''.join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in Topic.lower())
        safe_filename = safe_filename.replace(' ', '_')
        
        # Save the generated content to a text file
        file_path = os.path.join(data_dir, f"{safe_filename}.txt")
        
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(ContentByAI)
                print(f"[green]Content saved to: {file_path}[/green]")
        except Exception as e:
            print(f"[red]Error saving content to file: {str(e)}[/red]")
            return False

        # Open the file in Notepad
        return OpenNotepad(file_path)

    except Exception as e:
        print(f"[red]Error in Content function: {str(e)}[/red]")
        return False  # Indicate failure.


# Function to play a video on YouTube
def PlayYoutube(query):
    try:
        print(f"[yellow]Searching for '{query}' on YouTube...[/yellow]")
        
        # Clean up the query if needed
        query = query.replace("play ", "").strip()
        if query.endswith(" on youtube") or query.endswith(" in youtube"):
            query = query.replace(" on youtube", "").replace(" in youtube", "").strip()
            
        if not query:
            print("[red]Error: Empty query for YouTube search[/red]")
            return False
            
        # Use pywhatkit's playonyt function to play the video
        playonyt(query)
        print(f"[green]Playing '{query}' on YouTube[/green]")
        return True
        
    except Exception as e:
        print(f"[red]Error playing YouTube video: {str(e)}[/red]")
        try:
            # Fallback method: Open YouTube with a search query
            search_query = query.replace(" ", "+")
            youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
            webopen(youtube_search_url)
            print(f"[yellow]Opened YouTube search for '{query}'[/yellow]")
            return True
        except Exception as fallback_error:
            print(f"[red]Fallback method also failed: {str(fallback_error)}[/red]")
            return False


# Function to open an application or a relevant webpage
def OpenApp(app, sess=requests.session()):
    try:
        # Special handling for common websites and services
        if app.lower() in ["youtube", "google", "facebook", "instagram", "twitter", "gmail", "amazon"]:
            web_urls = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "facebook": "https://www.facebook.com",
                "instagram": "https://www.instagram.com",
                "twitter": "https://twitter.com",
                "gmail": "https://mail.google.com",
                "amazon": "https://www.amazon.com"
            }
            webopen(web_urls[app.lower()])
            print(f"[green]Opened {app} in web browser[/green]")
            return True
            
        # Try to open as a desktop application
        print(f"[yellow]Attempting to open {app} as a desktop application...[/yellow]")
        appopen(app, match_closest=True, output=True, throw_error=True)  # Attempt to open the app.
        print(f"[green]Successfully opened {app}[/green]")
        return True
    except Exception as app_error:
        print(f"[yellow]Could not open as desktop app: {str(app_error)}[/yellow]")
        print(f"[yellow]Attempting to find {app} on the web...[/yellow]")
        
        try:
            # Nested function to extract links from HTML content
            def extract_links(html):
                if html is None:
                    return []
                soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content.
                links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevant links.
                return [link.get('href') for link in links if link.get('href')]  # Return the links, filtering None

            def search_google(query):
                try:
                    url = f"https://www.google.com/search?q={query}"  # Construct the Google search URL.
                    headers = {"User-Agent": useragent}  # Use the predefined user-agent.
                    response = sess.get(url, headers=headers)  # Perform the GET request.
                    if response.status_code == 200:
                        return response.text  # Return the HTML content.
                    else:
                        print(f"[red]Failed to retrieve search results: Status code {response.status_code}[/red]")
                        return None
                except Exception as e:
                    print(f"[red]Error during Google search: {str(e)}[/red]")
                    return None

            html = search_google(app)  # Perform the Google search.
            
            if html:
                links = extract_links(html)
                if links and len(links) > 0:
                    link = links[0]  # Extract the first link from the search results.
                    webopen(link)  # Open the link in a web browser.
                    print(f"[green]Opened {app} web page: {link}[/green]")
                    return True
                else:
                    print(f"[red]No links found for {app}[/red]")
                    # Fallback to a direct search
                    webopen(f"https://www.google.com/search?q={app}")
                    print(f"[yellow]Opened Google search for {app}[/yellow]")
                    return True
            else:
                # If all else fails, just open a Google search for the app
                webopen(f"https://www.google.com/search?q={app}")
                print(f"[yellow]Opened Google search for {app}[/yellow]")
                return True
                
        except Exception as web_error:
            print(f"[red]Error opening {app} on the web: {str(web_error)}[/red]")
            return False


# Function to close an application
def CloseApp(app):
    try:
        app_name = app.lower().strip()
        
        # Skip certain apps like chrome that might be risky to close
        if app_name in ["chrome", "browser", "microsoft edge", "edge", "firefox"]:
            print(f"[yellow]Skipping closing {app_name} as it may disrupt your browsing[/yellow]")
            return False
            
        # Try to close the app
        print(f"[yellow]Attempting to close {app_name}...[/yellow]")
        close(app_name, match_closest=True, output=True, throw_error=True)
        print(f"[green]CLOSING {app_name.upper()}[/green]")
        return True
        
    except Exception as e:
        print(f"[red]Error closing {app}: {str(e)}[/red]")
        
        # If AppOpener fails, try using taskkill as a fallback for Windows
        if sys.platform == 'win32':
            try:
                # Get a simplified app name without spaces for process matching
                simple_app = app_name.split()[0] if ' ' in app_name else app_name
                # Try to kill the process with taskkill
                result = subprocess.run(['taskkill', '/F', '/IM', f"{simple_app}*"], 
                                      shell=True, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                
                if result.returncode == 0:
                    print(f"[green]Successfully closed {app_name} using taskkill[/green]")
                    return True
                else:
                    print(f"[red]Failed to close {app_name} using taskkill: {result.stderr.decode()}[/red]")
            except Exception as fallback_error:
                print(f"[red]Fallback method also failed: {str(fallback_error)}[/red]")
        
        return False


# Function to execute system-level commands
def System(command):
    # Convert command to lowercase for easier matching
    command = command.lower().strip()
    print(f"[yellow]Executing system command: {command}[/yellow]")
    
    # Audio controls
    if command in ["mute", "mute audio", "mute sound"]:
        keyboard.press_and_release("volume mute")
        print("[green]System muted[/green]")
        return True
        
    elif command in ["unmute", "unmute audio", "unmute sound"]:
        keyboard.press_and_release("volume mute")
        print("[green]System unmuted[/green]")
        return True
        
    elif command in ["volume up", "increase volume", "louder"]:
        # Press multiple times for more noticeable change
        for _ in range(5):
            keyboard.press_and_release("volume up")
        print("[green]Volume increased[/green]")
        return True
        
    elif command in ["volume down", "decrease volume", "quieter"]:
        # Press multiple times for more noticeable change
        for _ in range(5):
            keyboard.press_and_release("volume down")
        print("[green]Volume decreased[/green]")
        return True
    
    # Media controls
    elif command in ["play", "pause", "play pause", "toggle playback"]:
        keyboard.press_and_release("play/pause media")
        print("[green]Media play/pause toggled[/green]")
        return True
        
    elif command in ["next", "next track", "skip"]:
        keyboard.press_and_release("next track")
        print("[green]Skipped to next track[/green]")
        return True
        
    elif command in ["previous", "previous track", "back"]:
        keyboard.press_and_release("previous track")
        print("[green]Returned to previous track[/green]")
        return True
    
    # Screen controls
    elif command in ["lock", "lock screen", "lock computer"]:
        if sys.platform == 'win32':
            os.system("rundll32.exe user32.dll,LockWorkStation")
            print("[green]Screen locked[/green]")
            return True
        else:
            print("[red]Lock screen command not supported on this platform[/red]")
            return False
    
    # Power controls (limited for safety)
    elif command in ["sleep", "sleep mode", "put computer to sleep"]:
        if sys.platform == 'win32':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            print("[green]Putting system to sleep[/green]")
            return True
        else:
            print("[red]Sleep command not supported on this platform[/red]")
            return False
    
    # Brightness controls
    elif command in ["brightness up", "increase brightness"]:
        if sys.platform == 'win32':
            try:
                # Simulate brightness up key if available
                keyboard.press_and_release("brightness up")
                print("[green]Brightness increased[/green]")
                return True
            except:
                print("[red]Brightness control not available[/red]")
                return False
        else:
            print("[red]Brightness control not supported on this platform[/red]")
            return False
            
    elif command in ["brightness down", "decrease brightness"]:
        if sys.platform == 'win32':
            try:
                # Simulate brightness down key if available
                keyboard.press_and_release("brightness down")
                print("[green]Brightness decreased[/green]")
                return True
            except:
                print("[red]Brightness control not available[/red]")
                return False
        else:
            print("[red]Brightness control not supported on this platform[/red]")
            return False
    
    # Unknown command
    else:
        print(f"[red]Unknown system command: {command}[/red]")
        return False

# Asynchronous function to translate and execute commands
async def TranslateAndExecute(commands: list[str]):
    if not commands or len(commands) == 0:
        print("[red]No commands to execute[/red]")
        return
        
    print(f"[blue]Received commands: {commands}[/blue]")
    funcs = []  # List to store asynchronous tasks.
    command_types = []  # Keep track of command types for reporting

    for command in commands:
        if not command or not isinstance(command, str):
            print(f"[red]Invalid command: {command}[/red]")
            continue
            
        command = command.strip().lower()
        command_type = None
        
        if command.startswith("open "):  # Handle "open" commands
            if "open it" in command or "open file" == command:
                print("[yellow]Skipping ambiguous command: {command}[/yellow]")
                continue
            else:
                app_name = command.replace("open ", "", 1).strip()
                if app_name:
                    fun = asyncio.to_thread(OpenApp, app_name)
                    funcs.append(fun)
                    command_type = f"open_{app_name}"

        elif command.startswith("general "):  # Placeholder for general commands
            # These are handled by the main code, not here
            pass

        elif command.startswith("realtime "):  # Placeholder for real-time commands
            # These are handled by the main code, not here
            pass

        elif command.startswith("close "):  # Handle "close" commands
            app_name = command.replace("close ", "", 1).strip()
            if app_name:
                fun = asyncio.to_thread(CloseApp, app_name)
                funcs.append(fun)
                command_type = f"close_{app_name}"

        elif command.startswith("play "):  # Handle "play" commands
            query = command.replace("play ", "", 1).strip()
            if query:
                fun = asyncio.to_thread(PlayYoutube, query)
                funcs.append(fun)
                command_type = f"play_{query}"

        elif command.startswith("content "):  # Handle "content" commands
            topic = command.strip()  # Keep "content" prefix for the Content function
            if len(topic) > 8:  # Make sure there's something after "content "
                fun = asyncio.to_thread(Content, topic)
                funcs.append(fun)
                command_type = f"content_{topic.replace('content ', '', 1)}"

        elif command.startswith("google search "):  # Handle Google search commands
            query = command.replace("google search ", "", 1).strip()
            if query:
                fun = asyncio.to_thread(GoogleSearch, query)
                funcs.append(fun)
                command_type = f"google_search_{query}"

        elif command.startswith("youtube search "):  # Handle YouTube search commands
            query = command.replace("youtube search ", "", 1).strip()
            if query:
                fun = asyncio.to_thread(PlayYoutube, query)
                funcs.append(fun)
                command_type = f"youtube_search_{query}"

        elif command.startswith("system "):  # Handle system commands
            action = command.replace("system ", "", 1).strip()
            if action:
                fun = asyncio.to_thread(System, action)
                funcs.append(fun)
                command_type = f"system_{action}"

        else:
            print(f"[red]No function found for: {command}[/red]")
            
        if command_type:
            command_types.append(command_type)

    # If we have functions to execute, run them concurrently
    if funcs:
        try:
            results = await asyncio.gather(*funcs, return_exceptions=True)
            
            # Process and yield results
            for i, result in enumerate(results):
                command_info = command_types[i] if i < len(command_types) else "unknown"
                
                if isinstance(result, Exception):
                    print(f"[red]Error executing {command_info}: {str(result)}[/red]")
                    yield False
                else:
                    print(f"[green]Successfully executed {command_info}[/green]")
                    yield result
        except Exception as e:
            print(f"[red]Error during command execution: {str(e)}[/red]")
            yield False
    else:
        print("[yellow]No actionable commands to execute[/yellow]")
        yield True  # Still return success if no commands were actionable

# Asynchronous function to automate command execution
async def Automation(commands: list[str]):
    success = True
    try:
        async for result in TranslateAndExecute(commands):
            if result is False:
                success = False
        return success
    except Exception as e:
        print(f"[red]Error in Automation: {str(e)}[/red]")
        return False

