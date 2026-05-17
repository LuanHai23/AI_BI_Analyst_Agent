import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
import requests
load_dotenv()

# URL của FastAPI backend
API_BASE_URL = os.getenv("API_BASE_URL")

# Đường dẫn tới file questions.json
QUESTIONS_FILE = Path(__file__).parent / "questions.json"

# Đường dẫn lưu kết quả evaluation
RESULTS_FILE = Path(__file__).parent / "eval_results.csv"

def load_questions():
    # Đọc danh sách câu hỏi từ file JSON
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
    
def check_sql_keywords(generated_sql: str, expected_keywords: list[str]) -> bool:
    # Chuyển sql về thường để check keyword
    generated_sql_lower = generated_sql.lower()
    
    # Kiểm tra tất cả keyword có xuất hiện trong SQL không
    for keyword in expected_keywords:
        if keyword.lower() not in generated_sql_lower:
            return False
    return True

def evaluate_question(dataset_id: str, test_case: dict) -> dict:
    # Lấy câu hỏi từ test case
    question = test_case["question"]

    # Lấy danh sách keyword SQL kỳ vọng
    expected_keywords = test_case.get("expected_sql_keywords", [])

    # Tạo payload gửi lên endpoint /ask
    payload = {
        "question": question,
    }

    # Ghi lại thời điểm bắt đầu để tính latency
    start_time = time.perf_counter()

    try:
        # Call API cuaR be
        response = requests.post(
            f"{API_BASE_URL}/datasets/{dataset_id}/ask",
            json=payload,
            timeout=180,  # timeout sau 30 giây
        )

        # Nếu BE trả lỗi HTTP thì raise exception
        response.raise_for_status()

        # Parse response JSON
        data = response.json()

        # Tính latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Lấy SQL được sinh ra
        generated_sql = data.get("generated_sql", "")

        # Check SQL có chứa các keyword kỳ vọng khum
        keyword_pass = check_sql_keywords(
            generated_sql = generated_sql, 
            expected_keywords = expected_keywords,
        )

        # Trả về kết quả evualation
        return {
            "id": test_case["id"],
            "question": question,
            "status": "success",
            "keyword_pass": keyword_pass,
            "latency_ms": round(latency_ms, 2),
            "generated_sql": generated_sql,
            "row_count": data.get("row_count"),
            "answer": data.get("answer"),
            "error_message": "",
        }
    except Exception as e:
        # Tính latency nếu có lỗi
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Trả về kết quả error
        return {
            "id": test_case["id"],
            "question": question,
            "status": "error",
            "keyword_pass": False,
            "latency_ms": round(latency_ms, 2),
            "generated_sql": "",
            "row_count": None,
            "answer": None,
            "error_message": str(e),
        }
    
def run_evaluation(dataset_id: str) -> None:
    # Đọc danh sách câu hỏi test
    questions = load_questions()

    # List lưu kết quả evaluation
    results = []

    print(f"Running evaluation for dataset: {dataset_id}")
    print(f"Total questions: {len(questions)}")

    print("-" * 50)

    # Duyệt qua từng test case
    for test_case in questions:
        print(f"Running test {test_case['id']}: {test_case['question']}")

        # Evaluate câu hoir
        result = evaluate_question(
            dataset_id = dataset_id,
            test_case = test_case,
        )

        # Thêm kết quả vào list
        results.append(result)

        # In trang thai ra terminal
        print(
            f"Status: {result['status']} | "
            f"Keyword pass: {result['keyword_pass']} | "
            f"Latency: {result['latency_ms']} ms"
        )
        print("-" * 80)

        # Convert result thành DF
        results_df = pd.DataFrame(results)

        # Lưu kết quả ra CSV
        results_df.to_csv(RESULTS_FILE, index=False, encoding="utf-8-sig")

        # Tính summary
        total_tests = len(results)
        success_count = (results_df["status"] == "success").sum()
        keyword_pass_count = results_df["keyword_pass"].sum()
        avg_latency = results_df["keyword_pass"].mean()

        # In summary
        print("\n Evaluation Summary:")
        print("=" * 80)
        print(f"Total tests: {total_tests}")
        print(f"Success count: {success_count}")
        print(f"Success rate: {success_count / total_tests * 100:.2f}%")
        print(f"Keyword pass count: {keyword_pass_count}")
        print(f"Keyword pass rate: {keyword_pass_count / total_tests * 100:.2f}%")
        print(f"Average latency: {avg_latency:.2f} ms")
        print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    # Nhập dataset_id từ terminal
    dataset_id = input("Enter dataset_id: ").strip()

    # Nếu user không nhập dataset_id thì báo lỗi
    if not dataset_id:
        raise ValueError("dataset_id is required.")

    # Chạy evaluation
    run_evaluation(dataset_id)