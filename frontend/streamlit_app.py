import json
import os
import pandas as pd
import plotly.io as pio
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# Lấy URL của FastAPI backend từ biến môi trường
API_BASE_URL = os.getenv("API_BASE_URL")

st.set_page_config(
    page_title = "AI Data Analyst Agent",
    page_icon = "📊",
    layout = "wide"
)

# Title của app
st.title("AI Data Analyst Agent")

st.write(
    "Upload dataset, ask business questions, run SQL, and generate charts using AI."
)

# Khởi tạo session để lưu dataset_id giuawx các lần user tương tác
# Streamlit chạy lại script mỗi lần bấm nút
if "dataset_id" not in st.session_state:
    st.session_state.dataset_id = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "dataset_columns" not in st.session_state:
    st.session_state.dataset_columns = []

# Sidebar dùng để upload và hiển thị thông tin của data
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV or Excel file",
    type =["csv", "xlsx", "xls"],
)

# Khi user bấm nút upload
if st.sidebar.button("Upload Dataset"):
    # Kiểm tra user đã chọn file chưa
    if uploaded_file is None:
        st.sidebar.error("Please choose a file first")
    else:
        # Gửi file lên FastAPI endpoint /datasets/upload
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type,
            )
        }

        try:
            # Gọi API upload dataset
            response = requests.post(
                f"{API_BASE_URL}/datasets/upload",
                files = files,
                timeout=120
            )

            # Nếu API trả lỗi thì raise exception
            response.raise_for_status()

            # Parse JSON response từ backend
            data = response.json()

            # Lưu dataset vào session_state để dùng cho các tab khác
            st.session_state.dataset_id = data["dataset_id"]
            st.session_state.uploaded_filename = data["filename"]
            st.session_state.dataset_columns = data["columns"]

            # Thông báo upload thành công
            st.sidebar.success("Upload successful")

            # Hiển thị dataset để debug/test
            st.sidebar.write("Dataset ID:")
            st.sidebar.code(st.session_state.dataset_id)
        
        except requests.exceptions.RequestException as e:
            # Hiện lỗi khi calls API fail
            st.sidebar.error(f"Upload failed: {e}")

st.sidebar.header("Current Dataset")

if st.session_state.dataset_id:
    st.sidebar.success(f"Loaded: {st.session_state.uploaded_filename}")
    st.sidebar.code(st.session_state.dataset_id)
else:
    st.sidebar.warning("No dataset uploaded yet")

tab_profile, tab_ask, tab_sql, tab_chart, tab_logs, tab_evaluation = st.tabs(
    [
        "📌 Profile / EDA",
        "🤖 Ask AI",
        "🧠 SQL Query",
        "📈 Chart",
        "📝 Logs",
        "📊 Evaluation"
    ]
)
with tab_profile:
    st.header("📌 Dataset Profile / EDA")

    # Chỉ cho dùng tab này khi đã upload dataset
    if not st.session_state.dataset_id:
        st.info("Please upload a dataset first.")
    else:
        # Khi user bấm nút Generate Profile
        if st.button("Generate Profile"):
            try:
                # Gọi API profile dataset
                response = requests.get(
                    f"{API_BASE_URL}/datasets/{st.session_state.dataset_id}/profile",
                    timeout=120,
                )

                # Nếu backend trả lỗi thì raise exception
                response.raise_for_status()

                # Parse JSON response
                profile = response.json()

                # Hiển thị thông tin tổng quan
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Rows", profile["row_count"])

                with col2:
                    st.metric("Columns", profile["column_count"])

                with col3:
                    st.metric("Duplicate Rows", profile["duplicate_rows"])

                # Hiển thị danh sách cột và dtype
                st.subheader("Columns and Data Types")
                dtype_df = pd.DataFrame(
                    {
                        "column": list(profile["dtypes"].keys()),
                        "dtype": list(profile["dtypes"].values()),
                    }
                )
                st.dataframe(dtype_df, use_container_width=True)

                # Hiển thị missing values
                st.subheader("Missing Values")
                missing_df = pd.DataFrame(
                    {
                        "column": list(profile["missing_values"].keys()),
                        "missing_count": list(profile["missing_values"].values()),
                        "missing_percentage": list(
                            profile["missing_percentage"].values()
                        ),
                    }
                )
                st.dataframe(missing_df, use_container_width=True)

                # Hiển thị numeric summary
                st.subheader("Numeric Summary")
                if profile["numeric_summary"]:
                    numeric_df = pd.DataFrame(profile["numeric_summary"]).T
                    st.dataframe(numeric_df, use_container_width=True)
                else:
                    st.info("No numeric columns found.")

                # Hiển thị categorical summary
                st.subheader("Categorical Summary")
                if profile["categorical_summary"]:
                    st.json(profile["categorical_summary"])
                else:
                    st.info("No categorical columns found.")

            except requests.exceptions.RequestException as e:
            # Hiển thị lỗi chung từ requests
                st.error(f"Failed to generate profile: {e}")

            # Hiển thị lỗi chi tiết từ backend
                if e.response is not None:
                    st.error(e.response.text)

# Tab 2 này dùng để hỏi AI
with tab_ask:
    st.header("Asi AI about your dataset")
    
    if not st.session_state.dataset_id:
        st.info("Please upload a dataset first")
    else:
        # Ô nhập câu hỏi
        question = st.text_area(
            "Ask a question",
            placeholder="Ví dụ: Top 10 sản phẩm có số lượng bán nhiều nhất là gì?",
        )

        # Khi user bấm Ask
        if st.button("Ask AI"):
            if not question.strip():
                st.warning("Please enter a question")
            else:
                try:
                    # Body gửi lên API /ask
                    payload = {
                        "question": question,
                    }

                    # Gọi API ask dataset
                    response = requests.post(
                        f"{API_BASE_URL}/datasets/{st.session_state.dataset_id}/ask",
                        json = payload,
                        timeout=180,
                    )

                    # Nếu lỗi thì raise exception
                    response.raise_for_status()

                    # Parse JSON response
                    result = response.json()

                    # Hiển thị câu trả lời
                    st.subheader("Answer")
                    st.write(result["answer"])

                    # Hiển thị SQL do LLM tạo ra
                    st.subheader("Generated SQL")
                    st.code(result["generated_sql"], language="sql")

                    # Hiển thị kết quả query dưới dạng bảng
                    st.subheader("Query Results")
                    st.dataframe(
                        pd.DataFrame(result["results"]),
                        use_container_width=True,
                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"AI ask failed: {e}")

# Tab 3 dùng để SQL query
with tab_sql:
    st.header("SQL Query")

    if not st.session_state.dataset_id:
        st.info("Please upload a dataset first")
    else:
        # Ô để nhập SQL
        sql = st.text_area(
            "Write SQL query",
            value = "SELECT * FROM dataset LIMIT 10",
            height = 150,
        )

        # Khi user bấm run SQL
        if st.button("Run SQL"):
            if not sql.strip():
                st.warning("Please enter SQL")
            else:
                try:
                    # Body gửi lên API /query
                    payload = {
                        "sql": sql,
                    }

                    # Gọi API query
                    response = requests.post(
                        f"{API_BASE_URL}/datasets/{st.session_state.dataset_id}/query",
                        json = payload,
                        timeout=180,
                    )

                    # Nếu lỗi thì raise exception
                    response.raise_for_status()

                    # Parse JSON response
                    result = response.json()

                    # Hiển thị số dòng kết quả
                    st.write(f"Rows returned: {result['row_count']}")

                    # Hiển thị bảng kết quả
                    st.dataframe(
                        pd.DataFrame(result["results"]),
                        use_container_width = True,
                    )
                except requests.exceptions.RequestException as e:
                # Hiển thị lỗi chung từ requests
                    st.error(f"SQL query failed: {e}")

                # Nếu backend có trả response body thì hiển thị ra để debug
                    if e.response is not None:
                        st.error(e.response.text)

# Tab 4: Chart 
with tab_chart:
    st.header("📈Generate Chart")

    if not st.session_state.dataset_id:
        st.info("Please upload a dataset first")
    else:
        # SQL lấy dữ liệu cho chart
        chart_sql = st.text_area(
            "SQL for chart data",
            value=(
                "SELECT product_id, SUM(quantity) AS total_quantity"
                "FROM dataset"
                "GROUP BY product_id"
                "ORDER BY total_quantity DESC"
                "LIMIT 10"
            ),
            height=150
        )

        # Chọn loại biểu đồ
        chart_type = st.selectbox(
            "Chart type",
            ["bar", "line", "scatter", "pie"],
        )

        # Nhập tên cột x
        x_col = st.text_input(
            "X column",
            value = "product_id",
        )

        # Nhập tên cột y
        y_col = st.text_input(
            "Y column",
            value = "total_quantity"
        )

        # Nhập title
        chart_title = st.text_input(
            "Chart title",
            value = "Top 10 sản phẩm bán nhiều nhất",
        )

        # khi user bấm Generated Chart
        if st.button("Generate Chart"):
            try:
                payload = {
                    "sql": chart_sql,
                    "chart_type": chart_type,
                    "x": x_col,
                    "y": y_col,
                    "title": chart_title,
                }

                # Call API
                response = requests.post(
                    f"{API_BASE_URL}/datasets/{st.session_state.dataset_id}/chart",
                    json = payload,
                    timeout=180,
                )

                # Nếu lỗi thì raise exception
                response.raise_for_status()

                # Parse JSON response
                result = response.json()

                # Convert chart_json string về plotly
                fig = pio.from_json(result["chart_json"])

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Chart Data")
                st.dataframe(
                    pd.DataFrame(result["data"]),
                    use_container_width=True,
                )
            except requests.exceptions.RequestException as e:
            # Hiển thị lỗi chung từ requests
                st.error(f"Chart generation failed: {e}")

            # Hiển thị lỗi chi tiết từ backend
                if e.response is not None:
                    st.error(e.response.text)

# Tab 5: Logs
with tab_logs:
    st.header("📝 Agent Logs")

    # Số lượng log muốn lấy
    limit = st.number_input(
        "Number of logs",
        min_value = 1,
        max_value = 500,
        value = 50,
    )
        # Khi user bấm load logs
    if st.button("Load logs"):
        try:
        # Gọi API lấy logs
            response = requests.get(
                f"{API_BASE_URL}/logs/agent",
                params={"limit": limit},
                timeout=60,
            )

            # Nếu backend trả lỗi thì raise exception
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Lấy list logs
            logs = data["logs"]

            # Nếu chưa có logs thì thông báo
            if not logs:
                st.info("No logs found")
            else:
                # Hiển thị logs dưới dạng bảng
                logs_df = pd.DataFrame(logs)
                st.dataframe(logs_df, use_container_width=True)
        
        except requests.exceptions.RequestException as e:
            # Hiển thị lỗi chung từ requests
            st.error(f"Failed to load logs: {e}")

            if e.response is not None:
                st.error(e.response.text)