import os
import sys
import time
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

class CLS_Anthropic_Client:
    def __init__(self):
        load_dotenv()
        print(os.getenv("ANTHROPIC_API_KEY"))
        self.client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

    def generate_text_response(self, selected_model: str,                                 
                            chat_history: List[Dict],                                 
                            temperature: float = 0.7,                                 
                            max_tokens: int = 1000,                                 
                            top_p: float = 0.9,  
                            timeout: int = 30) -> Optional[str]:
        """
        Generate text response with comprehensive error handling and validation.
        
        Args:
            selected_model: Model name to use
            chat_history: List of message dictionaries
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter (0.0-1.0)
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
            
        # Parameter validation
        if not (0.0 <= temperature <= 2.0):
            print(f"Error: Temperature must be between 0.0 and 2.0, got {temperature}")
            return None
            
        if not (1 <= max_tokens <= 4096):  # Adjust based on your model's limits
            print(f"Error: max_tokens must be between 1 and 4096, got {max_tokens}")
            return None
            
        if not (0.0 <= top_p <= 1.0):
            print(f"Error: top_p must be between 0.0 and 1.0, got {top_p}")
            return None
            
        
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=selected_model,
                messages=chat_history,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                timeout=timeout
            )
            
            elapsed_time = time.time() - start_time
            
            # Log response time if it's slow
            if elapsed_time > 10:
                print(f"Warning: Response took {elapsed_time:.2f} seconds")
            
            return response.content[0].text if response.content else None
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = str(e).lower()
            
            # Specific error handling
            if "invalid_api_key" in error_msg or "unauthorized" in error_msg:
                print("Error: Invalid API key or unauthorized access")
                
            elif "insufficient_quota" in error_msg or "quota" in error_msg:
                print("Error: API quota exceeded or insufficient balance")
                
            elif "rate_limit" in error_msg:
                print("Error: Rate limit exceeded. Please wait before making another request")
                
            elif "timeout" in error_msg or elapsed_time > timeout:
                print(f"Error: Request timed out after {elapsed_time:.2f} seconds")
                
            elif "model_not_found" in error_msg or "invalid_model" in error_msg:
                print(f"Error: Model '{selected_model}' not found or invalid")
                
            elif "context_length_exceeded" in error_msg or "too_many_tokens" in error_msg:
                print(f"Error: Token limit exceeded. Try reducing max_tokens or chat history length")
                
            elif "invalid_request" in error_msg:
                print("Error: Invalid request parameters")
                
            elif "server_error" in error_msg or "internal_error" in error_msg:
                print("Error: Server error occurred. Please try again later")
                
            elif "network" in error_msg or "connection" in error_msg:
                print("Error: Network connection issue")
                
            else:
                print(f"Error generating text response: {e}")
                print(f"Request duration: {elapsed_time:.2f} seconds")
            
            return None