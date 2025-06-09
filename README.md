# IRIS (Intelligent Response and Information System) - Advanced AI Assistant

## Project Overview
IRIS (Intelligent Response and Information System) is an advanced AI assistant that combines multiple AI capabilities including natural language processing, speech recognition, text-to-speech conversion, and real-time web search functionality.

## Project Structure
```
├── Backend/
│   ├── Automation.py         # Core automation functionality
│   ├── Chatbot.py           # AI chatbot implementation using Groq
│   ├── ImageGeneration.py   # AI image generation capabilities
│   ├── Model.py             # Core AI model implementations
│   ├── RealtimeSearchEngine.py # Real-time web search functionality
│   ├── SpeechToText.py      # Speech recognition implementation
│   ├── TextToSpeech.py      # Text-to-speech conversion
│   ├── TestToSpeech.py      # Testing utilities for speech features
│   ├── setup_chrome.py      # Chrome browser automation setup
│   └── requirements.txt     # Python dependencies
├── Frontend/                # Frontend application files
├── Data/                    # Data storage directory
└── .venv/                   # Python virtual environment
```

## Backend Features

### 1. AI Chatbot (Chatbot.py)
- Powered by Groq's Llama3-70b-8192 model
- Real-time conversation capabilities
- Persistent chat history storage
- Context-aware responses
- Multi-language support with English responses
- Real-time date and time awareness

### 2. Speech Processing
- **Speech-to-Text (SpeechToText.py)**
  - Real-time speech recognition
  - Multi-language support
  - High-accuracy transcription

- **Text-to-Speech (TextToSpeech.py)**
  - Natural-sounding voice synthesis
  - Multiple voice options
  - Real-time conversion

### 3. Web Automation (Automation.py)
- Browser automation capabilities
- Web scraping functionality
- Real-time web search integration
- Chrome browser integration

### 4. Image Generation (ImageGeneration.py)
- AI-powered image generation
- Custom image creation based on text prompts
- Image manipulation capabilities

### 5. Real-time Search (RealtimeSearchEngine.py)
- Live web search functionality
- Search result processing
- Information extraction

## Dependencies
Key Python packages used in the project:
- cohere (>=4.37)
- python-dotenv (>=1.0.0)
- rich (>=13.7.0)
- groq (>=0.4.2)
- googlesearch-python (>=1.2.3)
- selenium (>=4.18.1)
- webdriver-manager (>=4.0.1)
- mtranslate (>=1.8.0)

## Setup Instructions
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r Backend/requirements.txt
   ```

4. Set up environment variables in `.env`:
   ```
   Username=your_username
   Assistantname=IRIS
   GroqAPIKey=your_groq_api_key
   ```

## Usage
The backend services can be used independently or integrated with the frontend application. Each module provides specific functionality that can be imported and used in other Python applications.

## Security
- API keys and sensitive information are stored in environment variables
- Secure communication protocols for API interactions
- Data persistence with proper file handling

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
