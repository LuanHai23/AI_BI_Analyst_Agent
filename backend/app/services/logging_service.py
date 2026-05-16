import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from services.dataset_service import UPLOAD_DIR


# BASE_DIR trỏ về thư mục gốc project: ai-data-analyst-agent/
BASE_DIR = Path(__file__).resolve().parents[3]

# Thư mục logs nằm ở project root
LOG_DIR = BASE_DIR / "logs"

# File CSV lưu logs
LOG_FILE = LOG_DIR / "agent_logs.csv"

# Tạo folder logs nếu chưa có
LOG_DIR.mkdir(parents=True, exist_ok=True)

class LoggingService:
    # Các cột trong file CSV
    FIELDNAMES = [
        "created_at",
        "dataset_id",
        "question",
        "generated_sql",
        "answer",
        "row_count",
        "latency_ms",
        "status",
        "error_message",
    ]

    def __init__(self):
        # Đảm bảo file log tồn tại khi service được tạo
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self) -> None:
        # Nếu file chưa tồn tại thì tạo mới và ghi header
        if not LOG_FILE.exists():
            with LOG_FILE.open(mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def log_agent_run(
        self,
        dataset_id: str,
        question: str,
        generated_sql: Optional[str],
        answer: Optional[str],
        row_count: Optional[int],
        latency_ms: float,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        # Tạo một dòng log mới
        log_row = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "dataset_id": dataset_id,
            "question": question,
            "generated_sql": generated_sql or "",
            "answer": answer or "",
            "row_count": row_count if row_count is not None else "",
            "latency_ms": round(latency_ms, 2),
            "status": status,
            "error_message": error_message or "",
        }

        # Debug xem log đang được ghi vào file nào
        print(f"Writing log to: {LOG_FILE}")
        print(f"Log row: {log_row}")

        # Append dòng log vào CSV
        with LOG_FILE.open(mode="a", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writerow(log_row)

    def read_logs(self, limit: int = 50) -> list[dict]:
        # Nếu file chưa tồn tại thì tạo file trước
        self._ensure_log_file_exists()

        # Đọc toàn bộ logs từ CSV
        with LOG_FILE.open(mode="r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Trả về logs mới nhất trước
        return rows[-limit:][::-1]