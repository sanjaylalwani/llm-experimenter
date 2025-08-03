import os
import time
from typing import List, Dict, Optional, Iterator
from dotenv import load_dotenv
from google import genai
from google.genai import types

class CLS_Gemini_Client:
    def __init__(self):
        load_dotenv()
        
        # Validate API key exists
        api_key = os.getenv("GOOGLE_LLM_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_LLM_API_KEY not found in environment variables")
            
        self.client = genai.Client(api_key=api_key)
        print("Google Gemini client initialized with API key")

        # Test connection on initialization
        try:
            # Simple test to validate API key
            self.client.models.list()
            print("Google Gemini client initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to validate Google Gemini API key: {e}")

    def generate_text_response(self, selected_model: str,
                                chat_history: List[Dict],
                                temperature: float = 0.7,
                                max_tokens: int = 1000,) -> Optional[str]:
        """
        Generate text response using Google's Gemini API.

        Args:
            selected_model: Model name to use
            chat_history: List of message dictionaries
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        prompt = "\n".join([msg["content"] for msg in chat_history])
        print(f"Generating response using model: {selected_model} with prompt: {prompt}")
        response = self.client.models.generate_content(
                model=selected_model, 
                contents=[prompt],
                config=types.GenerateContentConfig(
                                temperature=temperature,         # Increase randomness for a more creative story
                                max_output_tokens=max_tokens,   # Limit the story's length to a reasonable size
                            ),
        )
        return response.text