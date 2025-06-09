from googlesearch import search
from groq import Groq  # Importing the Groq Library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv values to read environment variables from a .env file.
import os  # Import os for path handling

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Get the parent directory

# Load environment variables from the Frontend/.env file
env_path = os.path.join(project_root, "Frontend", ".env")
env_vars = dotenv_values(env_path)

# Create Data directory if it doesn't exist
data_dir = os.path.join(script_dir, "Data")
os.makedirs(data_dir, exist_ok=True)

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Set the GROQ_API_KEY environment variable
os.environ["GROQ_API_KEY"] = GroqAPIKey

# Initialize the Groq client using the environment variable
client = Groq()

# Define the System Instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** IMPORTANT INSTRUCTIONS ***
1. Provide ONLY key points and important information
2. Keep responses brief and focused
3. Use bullet points for multiple pieces of information
4. Avoid unnecessary details or explanations
5. For numerical data or statistics, present only the most recent/relevant numbers
6. If the search results contain outdated information, mention the date
7. Use proper grammar and punctuation"""

# Attempt to load the chat log from a JSON file or create an empty one if it doesn't exist.
chat_log_path = os.path.join(data_dir, "ChatLog.json")
try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chat_log_path, "w") as f:
        dump([], f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=3))
    Answer = ""
    for i in results:
        if i.title and i.description:
            Answer += f"• {i.description.strip()}\n"
    return Answer

# Function to clean up the answer by removing empty lines and search information.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    # Remove any text between [start] and [end] tags
    if '[start]' in modified_answer and '[end]' in modified_answer:
        start_idx = modified_answer.find('[start]')
        end_idx = modified_answer.find('[end]') + len('[end]')
        modified_answer = modified_answer[end_idx:].strip()
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information.
def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = "Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log from the JSON file:
    with open(chat_log_path, "r") as f:
        messages = load(f)

    # Append the user's prompt to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})

    try:
        # Add Google search results to the system chatbot messages.
        search_results = GoogleSearch(prompt)
        SystemChatBot.append({"role": "system", "content": f"Here is the relevant information:\n{search_results}"})

        # Generate a response using the Groq client.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize an empty string for the answer.

        # Concatenate response chunks from the streaming output.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean up the response.
        Answer = Answer.strip().replace("</s>", "")

        # Append the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log back to the JSON file.
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        # Remove the most recent system message from the chatbot conversation.
        SystemChatBot.pop()

        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Remove the system message if it was added
        if len(SystemChatBot) > 3:
            SystemChatBot.pop()
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
