from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
# Lớp client để tương tác với Groq API
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
    
    def generate_sql(self, question: str, dataset_schema: dict) -> str:
        # Promt system định nghĩa vai trò của LLM 
        # Ở đây chỉ ép buộc sinh ra SQL chứ không giải thích lan man
        system_prompt = """
            You are an expert data analyst.
            Your task is to generate a valid DuckDB SQL query based on the user's question and dataset schema.

            Rules:
            - Use only the table name: dataset
            - Use only columns that exist in the schema
            - If a column name has spaces or special characters, wrap it in double quotes
            - Return only SQL, no markdown, no explanation
            - Do not use DELETE, UPDATE, INSERT, DROP, ALTER, CREATE
            - Prefer LIMIT 20 for large result queries

            Business interpretation rules:
            - If the user asks about "số lượng sản phẩm" or "total quantity", and a column named quantity exists, use SUM(quantity).
            - If the user asks about "số loại sản phẩm", "sản phẩm khác nhau", or "unique products", use COUNT(DISTINCT product_id) if product_id exists.
            - If the user asks about revenue and unit_price + quantity exist, calculate revenue as quantity * unit_price.
            - If discount_amount exists and the user asks about net revenue, calculate quantity * unit_price - discount_amount.
        """
        # Chuyển schema dataset thành text để LLM hiểu cột và kiểu dữ liệu
        schema_text = "\n".join(
            [
                f"- {column}: {dtype}"
                for column, dtype in dataset_schema["dtypes"].items()
            ]
        )
        # Prompt user chứa schema và câu hỏi
        user_prompt = f"""
            Dataset schema:
            {schema_text}
            User question:
            {question}

            Generate DuckDB SQL:
        """

        # CAll Groq Chat completion
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature = 0.0,
        )

        # Lấy content SQL từ response
        sql = response.choices[0].message.content.strip()

        # Xoá markdown code block nếu LLM có trả về  ```sql ... ```
        sql = sql.replace("```sql", "").replace("```", "").strip()

        # Trả về câu SQL
        return sql
    
    def explain_query_result(
        self,
        question: str,
        sql: str,
        results: list,
    ) -> str:
        # Prompt system yêu cầu LLM chỉ diễn giải dựa trên kết quả thật
        system_prompt = """
            You are an AI Data Analyst.
            Explain the SQL query result clearly and concisely.

            Rules:
            - Answer in VietNamese
            - Base your answer only on the provided query results
            - Do not make up numbers
            - If the result is empty, say that no matching data was found
        """

        user_prompt = f"""
            User question:
            {question}

            SQL query:
            {sql}

            Query results:
            {results}

            Please explain the result:
        """

        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt
                },
            ],
            temperature=0.2,
        )
        # Trả về câu trl cuối cùng
        return response.choices[0].message.content.strip()