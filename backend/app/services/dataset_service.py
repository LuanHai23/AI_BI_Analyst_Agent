import shutil
from pathlib import Path
from uuid import uuid4
import duckdb
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
    def save_upload_file(self, file: UploadFile) -> Path:
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
    def load_dataset(self, file_path: Path) -> pd.DataFrame:
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
    
    # Dùng để tìm file dataset theo dataset_id
    def get_dataset_path(self, dataset_id: str) -> Path:
        # Tìm tất cả file trong thư mục uploads có tên bắt đầu bằng dataset_id
        # Ví dụ dataset_id = abd thì có thể match cho .csv hoặc .xlsx
        matched_files = list(UPLOAD_DIR.glob(f"{dataset_id}.*"))

        if not matched_files:
            raise FileNotFoundError(f"Dataset with id '{dataset_id}' not found.")
        
        # Trả về file đầu tiên tìm được
        return matched_files[0]
    
    # Hàm này dùng để tạo ra một thông tin tổng quan về dataset
    def get_dataset_summary(self, df: pd.DataFrame) -> dict:
        # Chuyển dtype của từng cột sang string để JSON serialize được
        dtypes = {column: str(dtype) for column, dtype in df.dtypes.items()}

        preview_df = df.head(5).fillna("")

        # Trả về  dictionary chứa metadata của dataset
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "dtypes": dtypes,
            "preview": preview_df.to_dict(orient="records"),
        }
    
    # Hàm tổng hợp để lưu file, đọc file, tạo summary
    def process_uploaded_dataset(self, file: UploadFile) -> dict:
        # Lưu file vào data/uploads/
        file_path = self.save_upload_file(file)

        # Đọc dataset bằng pd (pandas)
        df = self.load_dataset(file_path)

        # Tạo summary từ DF
        summary = self.get_dataset_summary(df)

        # Thêm dataset_id để dùng khi cần thiết
        summary["dataset_id"] = file_path.stem

        # Theem file name gốc của user
        summary["filename"] = file.filename

        return summary
    
    def get_numeric_summary(self, df: pd.DataFrame) -> dict:
        # Lấy ra các cột có dữ liệu số
        numeric_df = df.select_dtypes(include=["number"])

        # Nếu dataset không có cột numeric thì trả về dict rỗng
        if numeric_df.empty:
            return {}
        
        # Describe() tạo các chỉ số count, mean, std, min, 25%, 50%, 75%, max
        summary_df = numeric_df.describe().T

        # Chuyển các giá trị NaN thành None để json trả về không error
        summary_df = summary_df.where(pd.notnull(summary_df), None)

        # Convert DF summary thành dict
        return summary_df.to_dict(orient="index")
    
    def get_categorical_summary(self, df: pd.DataFrame) -> dict:
        categorical_df = df.select_dtypes(include=["object", "category", "bool"])

        # Không có cột category thì trả về dict rỗng
        if categorical_df.empty:
            return {}
        
        # Dict dùng để chứa kết quả thống kê cho từng cột
        result = {}

        for column in categorical_df.columns:
            # Lấy series của cột hiện tại
            series = categorical_df[column]

            # Tính số lượng giá trị khác nhau và bỏ qua missing value
            unique_count = int(series.nunique(dropna=True))

            # Lấy top 5 giá trị xuất hiện nhiều nhất
            top_values = series.value_counts(dropna=True).head(5).to_dict()

            # Ép key và value để về dạng JSON
            top_values = {str(key): int(value) for key, value in top_values.items()}

            # Lưu summary của cột vào resultl
            result[column] = {
                "unique_count": unique_count,
                "top_values": top_values,
            }
        return result
    
    # hàm ni dùng để tạo profule EDA tổng quan về cho dataset
    def profile_dataset(self, dataset_id: str) -> dict:
        # Tìm đường dẫn file theo dataset
        file_path = self.get_dataset_path(dataset_id)

        # Đọc file thành DF
        df = self.load_dataset(file_path)

        # Tính số lượng missing values từng cột
        missing_values = df.isnull().sum().to_dict()

        # Ép value từ numpy int sang int thường để JSON serialize được nò
        missing_values = {column: int(value) for column, value in missing_values.items()}

        # Tính % missing cho từng cột
        missing_percentage = (df.isnull().mean() * 100).round(2).to_dict()

        # Ép value sang float thường để JSON serialize được nữa
        missing_percentage = {
            column: float(value) for column, value in missing_percentage.items()
        }

        # Chuyển dtype từng cột sang string
        dtypes = {column: str(dtype) for column, dtype in df.dtypes.items()}

        # Tạo 1 profile tổng quan
        profile = {
            "dataset_id": dataset_id,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "dtypes": dtypes,
            "missing_values": missing_values,
            "missing_percentage": missing_percentage,
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_summary": self.get_numeric_summary(df),
            "categorical_summary": self.get_categorical_summary(df),
        }

        return profile
    
    # 
    def query_dataset(self, dataset_id: str, sql: str) -> dict:
        # Chạy SQL và lấy kq dưới dạng DF
        result_df = self.query_dataset_as_dataframe(dataset_id, sql)

        # Thay NaN bằng json response không lỗi
        result_df = result_df.where(pd.notnull(result_df), None)

        # Trả về kết quả query
        return {
            "dataset_id": dataset_id,
            "sql": sql,
            "row_count": len(result_df),
            "columns": result_df.columns.tolist(),
            "results": result_df.to_dict(orient="records"),
        }
    # Hàm này lấy schema đơn giản của dataset để gửi LLM và tạo ra sql
    def get_dataset_schema(self, dataset_id: str) -> dict:
        # Tìm đường dẫn file theo dataset_id
        file_path = self.get_dataset_path(dataset_id)

        # Đọc file
        df = self.load_dataset(file_path)

        # Chuyển dtype từng cột sang string để LLM đọc được
        dtypes = {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

        # Trả về schema đơn giản
        return {
            "dataset_id": dataset_id,
            "columns": df.columns.to_list(),
            "dtypes": dtypes,
        }
    
    def validate_sql(self, sql: str) -> None:
        # Chuyển SQL về chữ thường để check keyword
        lowered_sql = sql.lower()

        # Danh sasch keyword
        blocked_keywords = [
            "delete",
            "update",
            "insert",
            "drop",
            "alter",
            "create",
            "truncate",
            "attach",
            "copy"
        ]

        # Nếu SQL chứa keyword như trên thì báo lỗi
        for keyword in blocked_keywords:
            if keyword in lowered_sql:
                raise ValueError(f"SQL contains blocked keyword {keyword}")
            
    # Hàm này để chạy SQL và trả về kq dưới dạng DF
    def query_dataset_as_dataframe(self, dataset_id: str, sql: str) -> pd.DataFrame:
        # Check SQL trước khi chạy
        self.validate_sql(sql)

        # Tìm đường dẫn file theo ds_id
        file_path = self.get_dataset_path(dataset_id)

        # Đọc file csv excel thành DF
        df = self.load_dataset(file_path)

        # Tạo connect Duckdb in-memory
        connection = duckdb.connect(database = ":memory:")

        try:
            # Sign up df thành tên dataset
            connection.register("dataset", df)

            # Chạy SQL và lấy kq thành DF
            result_df = connection.execute(sql).fetchdf()

            # Trả về DF kết quả
            return result_df
        finally:
            # Đóng kết nối
            connection.close()

