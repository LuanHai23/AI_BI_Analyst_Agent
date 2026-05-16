from fastapi import FastAPI, HTTPException, UploadFile, File

from llm.groq_client import LLMclient
from schemas.chat_schema import ChatRequest, ChatResponse
from schemas.dataset_schema import (
    DatasetUploadResponse,
    DatasetProfileResponse,
    DatasetQueryRequest,
    DatasetQueryResponse,
    DatasetAskRequest,
    DatasetAskResponse,
    DatasetChartRequest,
    DatasetChartResponse
)
from services.dataset_service import DatasetService
from services.chart_service import ChartService

app = FastAPI(
    title = "AI Data Analyst Agent API",
    description = "Backend API for AI-powered data analysis agent",
    version = "0.1.0",
)

llm_client = LLMclient()
chart_service = ChartService()

dataset_service = DatasetService()
@app.get("/debug/dataset-service")
def debug_dataset_service():
    return {
        "methods": dir(dataset_service)
    }
# Endpoint để kiểm tra xem BE có đang chạy hay không
@app.get("/")
def root():
    return {
        "message": "AI Data Analyst Agent API is running",
        "docs": "/docs",
    }

# Endpoint để chat với LLMs
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Gửi message của user sang LLM
        response = llm_client.chat(request.message)
        return ChatResponse(response=response)
        # Trả response về client
    except Exception as e:
        # Nếu lỗi thì trả HTTP 500
        raise HTTPException(status_code=500, detail=str())

# Endpoint upload dataset CSV/Excel
@app.post("/datasets/upload", response_model = DatasetUploadResponse)
def upload_dataset(file: UploadFile = File(...)):
    try:
        # Xử lý file đã upload
        dataset_info = dataset_service.process_uploaded_dataset(file)

        # Trả thông tin của dataset về client
        return DatasetUploadResponse(**dataset_info)
    
    except ValueError as e:
        # Lỗi do user upload sai định dạng file
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Lỗi từ server
        raise HTTPException(status_code= 500, detail=str(e))
    
@app.get("/datasets/{dataset_id}/profile", response_model = DatasetProfileResponse)
def profile_dataset(dataset_id: str):
    try:
        # Gọi DataService để tạo profile cho dataset theo ds_id
        profile = dataset_service.profile_dataset(dataset_id)

        # Convert dictionary thành response schema Pydantic
        return DatasetProfileResponse(**profile)
    
    except FileNotFoundError as e:
        # Trả lỗi 404 nếu không tìm thấy dataset_id trong data/uploads
        raise HTTPException(status_code = 404, detail=str(e))
    
    except Exception as e:
        # Trả về 500 nếu bị lỗi server
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/datasets/{dataset_id}/query", response_model=DatasetQueryResponse)
def query_dataset(dataset_id: str, request: DatasetQueryRequest):
    try:
        # Gọi service để chạy SQL trên dataset bằng DuckDB
        query_result = dataset_service.query_dataset(
             dataset_id=dataset_id,
             sql=request.sql,
        )
        # Trả kq về cho client
        return DatasetQueryResponse(**query_result)
    
    except FileNotFoundError as e:
        # Trả về lỗi 404 nếu không tìm thấy dataset
        raise HTTPException(status=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

@app.post("/datasets/{dataset_id}/ask", response_model = DatasetAskResponse)
def ask_dataset(dataset_id: str, request: DatasetAskRequest):
    try:
        # Lấy schema của dataset để đưa cho LLM biết có cột mô
        dataset_schema = dataset_service.get_dataset_schema(dataset_id)

        # Gửi schema  + question cho LLM để tạo SQL
        generated_sql = llm_client.generate_sql(
            question = request.question,
            dataset_schema=dataset_schema
        )

        # Chạy SQL do LLM sinh ra bằng DuckDB
        query_results = dataset_service.query_dataset(
            dataset_id= dataset_id,
            sql = generated_sql,
        )

        # Gọi LLM lần 2 đẻ diễn giải kết quả quểy thành results tự nhiên
        answer = llm_client.explain_query_result(
            question = request.question,
            sql = generated_sql,
            results = query_results["results"],
        )

        # Trả về câu hỏi, SQL, kết quả và answer
        return DatasetAskResponse(
            dataset_id=dataset_id,
            question=request.question,
            generated_sql=generated_sql,
            row_count=query_results["row_count"],
            results=query_results["results"],
            answer= answer,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code = 404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/datasets/{dataset_id}/chart", response_model=DatasetChartResponse)
def create_dataset_chart(dataset_id: str, request: DatasetChartRequest):
    try:
        # Chạy SQL để lấy dữ liệu cho chart
        result_df = dataset_service.query_dataset_as_dataframe(
            dataset_id = dataset_id,
            sql = request.sql,
        )

        # Tạo chart JSON bằng plotly
        chart_json = chart_service.create_chart(
            df=result_df,
            chart_type = request.chart_type,
            x=request.x,
            y= request.y,
            title = request.title,
        )

        # Thay Nan bằng None để trả JSON sạch hơn
        clean_df = result_df.where(result_df.notnull(), None)

        # Trả về response về client
        return DatasetChartResponse(
            dataset_id=dataset_id,
            sql = request.sql,
            chart_type = request.chart_type,
            chart_json = chart_json,
            data = clean_df.to_dict(orient="records"),
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code = 404, detail = str(e))
    
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))