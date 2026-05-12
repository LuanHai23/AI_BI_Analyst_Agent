from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

class LLMclient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
        # Kiểm tra xem api key đã có chưa
        if not self.api_key:
            raise ValueError("GROQ API KEY is missing. Please set it in your .env file")

        self.client = Groq(api_key=self.api_key)

    def chat(self, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI Data Analyst Agent"
                        "You explain data analysis concepts clearly and avoid making up results"
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content