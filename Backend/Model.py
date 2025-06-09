import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich Library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables.
import os  # Import os for path handling

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the Frontend/.env file
env_path = os.path.join(os.path.dirname(script_dir), "Frontend", ".env")
env_vars = dotenv_values(env_path)

# Retrieve API key:
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API Key.
CO = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image of", "system", "content", "google search",
    "youtube search", "reminder"
]

# Initialize an empty list to store user messages.
messages = []

ChatHistory = [
    {"role": "User", "message": "generate the images of tony stark"},
    {"role": "Chatbot", "message": "generate image of tony stark"},
    {"role": "User", "message": "can you create a picture of a sunset"},
    {"role": "Chatbot", "message": "generate image of a sunset"},
    {"role": "User", "message": "make me an image of tony stark"},
    {"role": "Chatbot", "message": "generate image of tony stark"},
    {"role": "User", "message": "draw a picture of spiderman"},
    {"role": "Chatbot", "message": "generate image of spiderman"},
    {"role": "User", "message": "show me tony stark"},
    {"role": "Chatbot", "message": "generate image of tony stark"},
    {"role": "User", "message": "generate images on tony stark"},
    {"role": "Chatbot", "message": "generate image of tony stark"}
]

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write an application and open it in notepad'.
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general (query)' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up-to-date information like:
   - If the query is 'who was akbar?' respond with 'general who was akbar?'
   - If the query is 'how can I study more effectively?' respond with 'general how can I study more effectively?'
   - If the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?'
   - If the query is 'Thanks, I really liked it.' respond with 'general thanks, I really liked it.'
   - If the query is 'what is python programming language?' respond with 'general what is python programming language?'
   
-> Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like:
   - 'who is he?' -> 'general who is he?'
   - 'what's his net worth?' -> 'general what's his net worth?'
   - 'tell me more about him.' -> 'general tell me more about him.'
   
-> Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc. like:
   - 'what's the time?' -> 'general what's the time?'

-> Respond with 'realtime (query)' if a query cannot be answered by an LLM model (because they don't have real-time data) and requires up-to-date information like:
   - 'who is Indian prime minister' -> 'realtime who is Indian prime minister'
   - 'tell me about Facebook's recent update.' -> 'realtime tell me about Facebook's recent update.'
   - 'tell me news about coronavirus.' -> 'realtime tell me news about coronavirus.'

-> Respond with 'realtime (query)' if the query is asking about any individual or thing like:
   - 'who is Akshay Kumar' -> 'realtime who is Akshay Kumar'
   - 'what is today's news?' -> 'realtime what is today's news?'
   - 'what is today's headline?' -> 'realtime what is today's headline?'

-> Respond with 'open (application name or website name)' if a query is asking to open any application or website like:
   - 'open Facebook' -> 'open Facebook'
   - 'open Telegram' -> 'open Telegram'
   - For multiple apps, respond like: 'open 1st Facebook, open 2nd Telegram'

-> Respond with 'close (application name)' if a query is asking to close any application like:
   - 'close Notepad' -> 'close Notepad'
   - 'close Facebook' -> 'close Facebook'
   - For multiple apps, respond like: 'close 1st Notepad, close 2nd Facebook'

-> Respond with 'play (song name)' if a query is asking to play any song like:
   - 'play Afsanay by Ys' -> 'play Afsanay by Ys'
   - 'play Let Her Go' -> 'play Let Her Go'
   - For multiple songs, respond like: 'play 1st Afsanay by Ys, play 2nd Let Her Go'

-> Respond with 'generate image (image prompt)' if a query is requesting to generate an image like:
   - 'generate image of a lion' -> 'generate image of a lion'
   - 'generate image of a cat' -> 'generate image of a cat'
   - For multiple images, respond like: 'generate image 1st lion, generate image 2nd cat'

-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like:
   - 'set a reminder at 9:00pm on 25th June for my business meeting.' -> 'reminder 9:00pm 25th June business meeting'

-> Respond with 'system (task name)' if a query is asking to perform system tasks like mute, unmute, volume up, volume down, etc.:
   - For multiple tasks, respond like: 'system 1st mute, system 2nd volume up'

-> Respond with 'content (topic)' if a query is asking to write any type of content (applications, codes, emails, etc.) about a specific topic:
   - For multiple content types, respond like: 'content 1st resignation letter, content 2nd leave application'

-> Respond with 'google search (topic)' if a query is asking to search a specific topic on Google:
   - For multiple searches, respond like: 'google search 1st topic, google search 2nd topic'

-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on YouTube:
   - For multiple searches, respond like: 'youtube search 1st topic, youtube search 2nd topic'

*** If the query is asking to perform multiple tasks like 'open Facebook, Telegram and close WhatsApp' respond with: 'open Facebook, open Telegram, close WhatsApp' ***

*** If the user is saying goodbye or wants to end the conversation like 'bye Jarvis.' respond with: 'exit' ***

*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***

*** If there is no decision, if the output is empty ( [] ), or if the query is unanswerable, respond with 'realtime (query)' ***
"""

def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "content": f"{prompt}"})
    
    stream = CO.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.1,  # Very low temperature for consistent responses
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )
    
    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text
    
    response = response.replace("\n", "")
    response = response.split(". ")
    response = [i.strip() for i in response]
    
    # First check for image generation commands
    for task in response:
        task_lower = task.lower()
        if any(word in task_lower for word in ["image", "picture", "draw", "show me"]):
            # Extract the subject
            if "of" in task_lower:
                subject = task_lower.split("of", 1)[1].strip()
            else:
                words = task_lower.split()
                if "show me" in task_lower:
                    subject = " ".join(words[2:]).strip()
                else:
                    subject = " ".join(words[2:]).strip()
            
            # Remove any prefixes like "general" or "realtime"
            subject = subject.replace("general", "").replace("realtime", "").strip()
            return [f"generate image of {subject}"]
    
    # Only process other commands if no image command was found
    temp = []
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    
    if "(query)" in temp:
        return FirstLayerDMM(prompt=prompt)
    
    return temp

# Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input.
    while True:
        print(FirstLayerDMM(input(">>> ")))
        