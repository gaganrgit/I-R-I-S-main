import sys
import os

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Get the parent directory of Frontend
sys.path.append(project_root)  # Add project root to Python path
sys.path.append(current_dir)  # Add Frontend directory to Python path

# Create necessary directories
os.makedirs(os.path.join(current_dir, "Files"), exist_ok=True)
os.makedirs(os.path.join(project_root, "Data"), exist_ok=True)
os.makedirs(os.path.join(project_root, "Backend", "Data"), exist_ok=True)

from Graphics.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognizer
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import time

# Load environment variables from Frontend/.env
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "IRIS")
GroqAPIKey = env_vars.get("GroqAPIKey", "your_actual_groq_api_key")

DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome home, sir. I am J.A.R.V.I.S., your AI assistant. How may I assist you today?"""

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ShowDefaultChatIfNoChats():
    try:
        os.makedirs('Data', exist_ok=True)

        try:
            with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
                content = file.read().strip()
                if not content or content == "[]":
                    default_chat = [
                        {"role": "user", "content": f"Hello {Assistantname}, How are you?"},
                        {"role": "assistant", "content": f"Welcome {Username}. I am doing well. How may I help you?"}
                    ]
                    with open(r'Data\ChatLog.json', "w", encoding='utf-8') as f:
                        json.dump(default_chat, f, indent=4)

                    with open(os.path.join(TempDirPath, 'Database.data'), 'w', encoding="utf-8") as file:
                        file.write("")
                    with open(os.path.join(TempDirPath, 'Responses.data'), 'w', encoding='utf-8') as file:
                        file.write(DefaultMessage)
        except (json.JSONDecodeError, FileNotFoundError):
            default_chat = [
                {"role": "user", "content": f"Hello {Assistantname}, How are you?"},
                {"role": "assistant", "content": f"Welcome {Username}. I am doing well. How may I help you?"}
            ]
            with open(r'Data\ChatLog.json', "w", encoding='utf-8') as f:
                json.dump(default_chat, f, indent=4)

            with open(os.path.join(TempDirPath, 'Database.data'), 'w', encoding="utf-8") as file:
                file.write("")
            with open(os.path.join(TempDirPath, 'Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")


def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(os.path.join(TempDirPath, 'Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    with open(os.path.join(TempDirPath, 'Database.data'), "r", encoding='utf-8') as File:
        Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = "\n".join(lines)

        with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as File:
            File.write(result)


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Initializing speech recognition...")
    recognizer = SpeechRecognizer()

    if not recognizer.driver:
        SetAssistantStatus("Failed to initialize speech recognition. Please check your microphone.")
        time.sleep(2)
        SetAssistantStatus("Available ... ")
        return False

    SetAssistantStatus("Listening ... ")
    Query = recognizer.recognize()

    if not Query:
        SetAssistantStatus("No speech detected...")
        time.sleep(2)
        SetAssistantStatus("Available ... ")
        return False

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ... ")

    try:
        Decision = FirstLayerDMM(Query)

        print("")
        print(f"Decision : {Decision}")
        print("")

        for queries in Decision:
            if "generate image of" in queries:
                subject = queries.replace("generate image of", "").strip()
                ImageGenerationQuery = subject
                ImageExecution = True
                break

        if ImageExecution:
            SetAssistantStatus("Generating image...")
            ShowTextToScreen(f"{Assistantname} : I'll generate an image of {ImageGenerationQuery} for you.")

            files_dir = os.path.join(current_dir, "Files")
            os.makedirs(files_dir, exist_ok=True)

            data_file = os.path.join(files_dir, "ImageGeneration.data")
            with open(data_file, "w", encoding='utf-8') as file:
                file.write(f"{ImageGenerationQuery}, True")

            try:
                image_script = os.path.join(project_root, "Backend", "ImageGeneration.py")
                p1 = subprocess.Popen(['python', image_script],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      stdin=subprocess.PIPE, shell=False)
                subprocesses.append(p1)
                SetAssistantStatus("Processing image request...")
                return True
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")
                ShowTextToScreen(f"{Assistantname} : Sorry, I encountered an error while generating the image.")
                SetAssistantStatus("Error in image generation...")
                return False

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Mearged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )

        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in Functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if (G and R) or R:
            SetAssistantStatus("Searching ... ")
            Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ... ")
            if not TextToSpeech(Answer):
                print("Error in text-to-speech")
            return True

        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking ... ")
                    QueryFinal = Queries.replace("general ", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    if not TextToSpeech(Answer):
                        print("Error in text-to-speech")
                    return True

                elif "realtime" in Queries:
                    SetAssistantStatus("Searching ... ")
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    if not TextToSpeech(Answer):
                        print("Error in text-to-speech")
                    return True

                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    if not TextToSpeech(Answer):
                        print("Error in text-to-speech")
                    SetAssistantStatus("Answering ... ")
                    os._exit(1)

    except Exception as e:
        print(f"Error in MainExecution: {e}")
        SetAssistantStatus("Error occurred...")
        time.sleep(2)
        SetAssistantStatus("Available ... ")
        return False


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ... " in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ... ")


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
