import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def generate_text_response(self, selected_model, chat_history, temperature, max_tokens, top_p, presence_penalty, frequency_penalty):
        try:
            response = self.client.chat.completions.create(
                        model=selected_model,
                        messages=chat_history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        presence_penalty=presence_penalty,
                        frequency_penalty=frequency_penalty
                    )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error generating response"