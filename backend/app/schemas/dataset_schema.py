from pydantic import BaseModel
from typing import List, Dict, Any

#Schema này dùng để định nghĩa response trả về sau khi mình upload dataset thành công
class DatasetUploadResponse(BaseModel):
    # ID tạm thời của dataset, sử dụng tên file đã lưu
    dataset_id: str
    # Tên file gốc mà người dùng upload
    filename: str
    # Số dòng của dataset
    row_count: int
    # Số cột của dataset
    column_count: int
    # Danh sách tên các cột
    columns: List[str]
    # Kiểu dữ liệu của từng cột
    dtypes: Dict[str, str]
    # 5 dòng đầu tiên để check dữ liệu
    preview: List[Dict[str, Any]]

class DatasetProfileResponse(BaseModel):
    # ID của dataset cần profile
    dataset_id: str

    # Số dòng trong dataset
    row_count: int

    # Số cột trong dataset
    column_count: int

    # Danh sách tên các cột
    columns: List[str]

    # Kiểu dữ liệu của từng cột
    dtypes: Dict[str, str]

    # Số lượng missing values của từng cột
    missing_values: Dict[str, int]

    # Phần trăm missing values của từng cột
    missing_percentage: Dict[str, float]

    # Số dòng bị duplicate
    duplicate_rows: int

    # Thống kê mô tả cho các cột numeric
    numeric_summary: Dict[str, Dict[str, Any]]

    # Thống kê mô tả cho các cột categorical/text
    categorical_summary: Dict[str, Dict[str, Any]]
class DatasetQueryRequest(BaseModel):
    # Câu SQL user gửi lên để query dataset
    sql: str

class DatasetQueryResponse(BaseModel):
    # ID cuar dataset được query
    dataset_id: str

    # Câu SQL đã chạy
    sql: str
    
    # Số dòng kết quả trả về
    row_count: int

    # Danh sách tên cột trong kết quả
    columns: List[str]

    # Kết quả query dạng list dict
    results: List[Dict[str, Any]]
    
class DatasetAskRequest(BaseModel):
    # Câu hỏi đến từ user: " Doanh thu theo từng danh mục là bao nhiêu"
    question: str

# Schema response cho API hỏi dataset bằng NLP
class DatasetAskResponse(BaseModel):
    # ID của dataset
    dataset_id: str

    # Câu hỏi gốc của user
    question: str

    # SQL do LLM tạo
    generated_sql:str

    # Số dòng query
    row_count: int

    # Kết quả query dưới dạng list dictionary
    results: List[Dict[str, Any]]

    # Câu trả lời tự nhiên do LLM diễn giải từ kq thật
    answer: str

class DatasetChartRequest(BaseModel):
    # Câu SQL dùng để lấy dữ liệu cho biểu đồ
    sql: str

    # Loại biểu đồ: bar, line, scatter, pie
    chart_type: str

    # Cột dùng làm trục X hoặc label
    x: str

    # Cột dùng làm trục Y hoặc value
    y: str

    # Tiêu đề biểu đồ, optional
    title: str | None = None

# Schema response cho API tạo chart
class DatasetChartResponse(BaseModel):
    # Id dataset được dùng
    dataset_id :str

    # Câu sql đã chạy
    sql: str

    # Loại biểu đồ đã tạo
    chart_type: str

    # Chart dạng JSON string để frontend render lại bằng plotly
    chart_json: str

    # Dữ liệu query dùng để tạo chart
    data: List[Dict[str, Any]]