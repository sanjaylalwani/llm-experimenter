import sys
import os
import time
from typing import List, Dict, Optional, Iterator
from dotenv import load_dotenv
from groq import Groq
import groq

class CLS_Groq_Client:
    def __init__(self):
        load_dotenv()
        
        # Validate API key exists
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=api_key)
        print("Groq client initialized with API key")
        
        # Test connection on initialization
        try:
            # Simple test to validate API key
            self.client.models.list()
            print("Groq client initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to validate Groq API key: {e}")

    def generate_text_response(self, 
                             selected_model: str,
                             chat_history: List[Dict],
                             temperature: float = 0.7,
                             max_completion_tokens: int = 1024,
                             top_p: float = 0.9,
                             presence_penalty: float = 0.0,
                             frequency_penalty: float = 0.0,
                             stream: bool = False,
                             stop: Optional[List[str]] = None,
                             timeout: int = 30) -> Optional[str]:
        """
        Generate text response with comprehensive error handling and validation.
        
        Args:
            selected_model: Groq model name (e.g., 'gemma2-9b-it', 'llama3-8b-8192')
            chat_history: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            max_completion_tokens: Maximum tokens to generate (1-32768 depending on model)
            top_p: Nucleus sampling parameter (0.0-1.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            stream: Whether to stream the response
            stop: List of stop sequences
            timeout: Request timeout in seconds
            
        Returns:
            Generated text or None if failed
        """
        
        # Input validation
        if not selected_model or not isinstance(selected_model, str):
            print("Error: Invalid model name provided")
            return None
            
        if not chat_history or not isinstance(chat_history, list):
            print("Error: Invalid chat history provided")
            return None
            
        # Validate chat history format
        for i, msg in enumerate(chat_history):
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                print(f"Error: Invalid message format at index {i}. Expected dict with 'role' and 'content'")
                return None
            if msg['role'] not in ['system', 'user', 'assistant']:
                print(f"Error: Invalid role '{msg['role']}' at index {i}. Must be 'system', 'user', or 'assistant'")
                return None
        
        # Parameter validation
        if not (0.0 <= temperature <= 2.0):
            print(f"Error: Temperature must be between 0.0 and 2.0, got {temperature}")
            return None
            
        if not (1 <= max_completion_tokens <= 32768):  # Groq's typical max context
            print(f"Error: max_completion_tokens must be between 1 and 32768, got {max_completion_tokens}")
            return None
            
        if not (0.0 <= top_p <= 1.0):
            print(f"Error: top_p must be between 0.0 and 1.0, got {top_p}")
            return None
            
        if not (-2.0 <= presence_penalty <= 2.0):
            print(f"Error: presence_penalty must be between -2.0 and 2.0, got {presence_penalty}")
            return None
            
        if not (-2.0 <= frequency_penalty <= 2.0):
            print(f"Error: frequency_penalty must be between -2.0 and 2.0, got {frequency_penalty}")
            return None
        
        if stop is not None and not isinstance(stop, list):
            print("Error: stop must be a list of strings or None")
            return None
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=chat_history,
                temperature=temperature,
                max_tokens=max_completion_tokens,  # Groq uses max_tokens, not max_completion_tokens
                top_p=top_p,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stream=stream,
                stop=stop,
                timeout=timeout
            )
            print(response)
            
            elapsed_time = time.time() - start_time
            
            # Log response time if it's slow
            if elapsed_time > 10:
                print(f"Warning: Response took {elapsed_time:.2f} seconds")
            
            # Handle streaming vs non-streaming responses
            if stream:
                return self._handle_streaming_response(response)
            else:
                # Check if response has content
                if not response.choices or not response.choices[0].message.content:
                    print("Error: Empty response received from Groq")
                    return None
                    
                return response.choices[0].message.content
                
        except groq.AuthenticationError as e:
            print(f"Error: Invalid API key or authentication failed: {e}")
            return None
            
        except groq.RateLimitError as e:
            print(f"Error: Rate limit exceeded: {e}")
            print("Please wait before making another request or check your usage limits")
            return None
            
        except groq.APIConnectionError as e:
            elapsed_time = time.time() - start_time
            print(f"Error: Failed to connect to Groq API: {e}")
            print(f"Request duration: {elapsed_time:.2f} seconds")
            return None
            
        except groq.APITimeoutError as e:
            elapsed_time = time.time() - start_time
            print(f"Error: Request timed out after {elapsed_time:.2f} seconds: {e}")
            return None
            
        except groq.BadRequestError as e:
            print(f"Error: Invalid request parameters: {e}")
            # Check for specific bad request issues
            error_msg = str(e).lower()
            if "model" in error_msg:
                print(f"Hint: Model '{selected_model}' may not exist or be accessible")
            elif "token" in error_msg:
                print("Hint: Try reducing max_tokens or chat history length")
            elif "context" in error_msg:
                print("Hint: Chat history may be too long for the model's context window")
            return None
            
        except groq.InternalServerError as e:
            print(f"Error: Groq server error: {e}")
            print("Please try again later")
            return None
            
        except groq.PermissionDeniedError as e:
            print(f"Error: Permission denied: {e}")
            print("Check if your API key has access to the requested model")
            return None
            
        except groq.UnprocessableEntityError as e:
            print(f"Error: Unprocessable request: {e}")
            return None
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"Unexpected error generating response: {e}")
            print(f"Request duration: {elapsed_time:.2f} seconds")
            print(f"Error type: {type(e).__name__}")
            return None
    
    def _handle_streaming_response(self, response: Iterator) -> Optional[str]:
        """
        Handle streaming response from Groq.
        
        Args:
            response: Streaming response iterator
            
        Returns:
            Complete response text or None if failed
        """
        try:
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)
            
            print()  # New line after streaming
            return full_response if full_response else None
            
        except Exception as e:
            print(f"\nError during streaming: {e}")
            return None
    
    def generate_streaming_response(self, 
                                  selected_model: str,
                                  chat_history: List[Dict],
                                  temperature: float = 0.7,
                                  max_completion_tokens: int = 1024,
                                  top_p: float = 0.9,
                                  presence_penalty: float = 0.0,
                                  frequency_penalty: float = 0.0,
                                  stop: Optional[List[str]] = None,
                                  timeout: int = 30) -> Optional[str]:
        """
        Generate streaming text response (convenience method).
        
        Returns:
            Complete response text or None if failed
        """
        return self.generate_text_response(
            selected_model=selected_model,
            chat_history=chat_history,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stream=True,
            stop=stop,
            timeout=timeout
        )
    
    def get_available_models(self) -> Optional[List[str]]:
        """
        Get list of available models from Groq.
        
        Returns:
            List of model names or None if failed
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching available models: {e}")
            return None
    
    def validate_model(self, model_name: str) -> bool:
        """
        Validate if a model exists and is accessible.
        
        Args:
            model_name: Name of the model to validate
            
        Returns:
            True if model is valid, False otherwise
        """
        try:
            available_models = self.get_available_models()
            if available_models:
                return model_name in available_models
            else:
                # Fallback: try to make a simple request
                test_response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                return True
        except Exception as e:
            print(f"Model '{model_name}' not found or inaccessible: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, List[str]]:
        """
        Get information about commonly available Groq models.
        
        Returns:
            Dictionary with model categories and their names
        """
        return {
            "llama_models": [
                "llama3-8b-8192",
                "llama3-70b-8192",
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama-3.2-1b-preview",
                "llama-3.2-3b-preview"
            ],
            "gemma_models": [
                "gemma2-9b-it",
                "gemma-7b-it"
            ],
            "mixtral_models": [
                "mixtral-8x7b-32768"
            ]
        }