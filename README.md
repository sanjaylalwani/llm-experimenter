# LLM Experimenter

LLM Experimenter is a powerful Streamlit-based application that allows you to experiment with various Language Learning Models (LLMs) from different providers including OpenAI, Anthropic, Google (Gemini), and Llama/Groq. The application provides a unified interface to interact with these models and compare their responses.

## Features

- 🤖 Support for multiple LLM providers:
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Google (Gemini models)
  - Llama/Groq
- 💬 Interactive chat interface
- 📊 Customizable model parameters
- 📝 Chat history tracking
- 🗄️ MongoDB integration for conversation storage
- 👤 User-specific configurations
- ⚙️ Advanced parameter controls (temperature, max tokens, etc.)

## Prerequisites

- Python 3.11 or higher
- MongoDB (local or cloud instance)
- API keys for the LLM providers you want to use

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sanjaylalwani/llm-experimenter.git
   cd llm-experimenter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r src/requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_API_KEY=your_google_api_key
   GROQ_API_KEY=your_groq_api_key
   MONGODB_URI=your_mongodb_connection_string
   ```

## Configuration

The application uses YAML configuration files located in `src/configurations/`:
- `models.yml`: Define available models for each provider
- `settings.py`: Default settings and configuration

## Running the Application

1. Make sure your virtual environment is activated

2. Run the Streamlit application:
   ```bash
   cd src
   streamlit run app/main.py
   ```

3. Open your web browser and navigate to `http://localhost:8501`

## Usage

1. Login using your name or email in the sidebar
2. Select an LLM model from the dropdown menu
3. (Optional) Adjust advanced parameters like temperature and max tokens
4. Start chatting with the model
5. View your chat history in the expandable section below

## Features in Detail

### Model Selection
- Choose from various models across different providers
- Each provider's models are clearly labeled with the provider name

### Advanced Parameters
- Temperature: Control response randomness (0.0 - 1.0)
- Max Tokens: Set maximum response length
- Top-p: Control response diversity
- Presence/Frequency Penalties: Adjust response creativity

### Chat History
- All conversations are saved automatically
- View previous interactions with timestamp and model information
- MongoDB integration ensures persistent storage

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- Thanks to all LLM providers for their APIs
- Built with Streamlit
- MongoDB for data storage