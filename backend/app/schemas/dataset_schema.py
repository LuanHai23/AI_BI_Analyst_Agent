from pydantic import BaseModel
from tying import List, Dict, Any

#Schema này dùng để định nghĩa response trả về sau khi mình upload dataset thành công
class DatasetUploadResponse(BaseModel):
    # ID tạm thời của dataset, sử dụng tên file đã lưu
    dataset_id: str
    # Tên file gốc mà người dùng upload
    filename: str
    # Số dòng của dataset
    row_count: int
    # Số cột của dataset
    columns_count: int
    # Danh sách tên các cột
    columns: List[str]
    # Kiểu dữ liệu của từng cột
    dtypes: Dict[str, str]
    # 5 dòng đầu tiên để check dữ liệu
    preview: List[Dict[str, Any]]