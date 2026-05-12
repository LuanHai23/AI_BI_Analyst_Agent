import shutil
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import UploadFile

# thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parents[3]
# đây là nơi lưu trữ các file user upload lên
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
# tạo folder uploads nếu không chưa có folder
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class DatasetService:
    # Lưu file upload vào thư mục uploads
    def save_upload_file(self, file: UploadFiled) -> Path:
        # Chỉ lấy phần tên file như .cxv .txt hay .xlsx
        file_extension = Path(file.filename).suffix.lower()

        # Checkk thử file có hợp lệ không
        if file_extension not in [".csv", ".xlsx", ".xls"]:
            raise ValueError["Only CSV and Excel files are supported."]
        
        # Tạo tên file unique để tránh trùng tên file sau mỗi lần update
        unique_file = f"{uuid4()}{file_extension}"

        # Tạo đường dẫn khi lưu file
        file_path = UPLOAD_DIR / unique_file
        
        # Mở file dưới dạng binary write
        with file_path.open("wb") as buffer:
            # Copy nội dung file upload vào file đích
            shutil.copyfileobj(file.file, buffer)

        # Trả về đường dẫn file đã lưu
        return file_path
    
    # Hàm này dùng để đọc dataset bằng pandas
    def load_dateset(self, file_path: Path) -> pd.DataFrame:
        # Lấy phần đuôi file để biết đọc bằng read_csv hay read_excel
        file_extension = file_path.suffix.lower()

        # Nếu là csv thì dùng pd.read_csv
        if file_extension == ".csv":
            return pd.read_csv(file_path)
        
        # Nếu là excel thì dùng pd.read_excel
        if file_extension == [".xlsx",".xls"]:
            return pd.read_excel(file_path)
        
        # Nếu không đúng định dạng thì báo lỗi
        raise ValueError("Unsupported file format")
    
    # Hàm này dùng để tạo ra một thông tin tổng quan về dataset
    def get_info_dataset(self, df: pd.DataFrame) -> dict:
        # Chuyển dtype của từng cột sang string để JSON serialize được
        dtypes = {column: str(dtype) for column, dtype in df.dtypes.items()}

        preview_df = df.head(5).fillna("")
        