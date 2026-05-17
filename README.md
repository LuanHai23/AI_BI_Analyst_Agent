# AI Data Analyst Agent

An AI-powered data analysis agent that allows users to upload CSV/Excel datasets, automatically profile data, ask business questions in natural language, generate SQL queries with LLM, execute SQL using DuckDB, visualize results with Plotly charts, and track agent logs/evaluation results.

This project is designed as an end-to-end AI Engineer Intern/Fresher portfolio project, focusing on LLM application development, tool calling, data analysis automation, backend API design, and production-oriented logging/evaluation.

---

## 1. Project Overview

AI Data Analyst Agent helps users analyze tabular datasets without manually writing SQL or Python code.

Users can:

- Upload CSV/Excel datasets.
- View automated EDA/profile reports.
- Ask questions in natural language.
- Let the LLM generate SQL automatically.
- Execute SQL on the dataset using DuckDB.
- Generate interactive charts.
- Track AI agent logs.
- Run evaluation tests on predefined business questions.

Example questions:

```text
Tổng số lượng sản phẩm đã bán là bao nhiêu?
```

```text
Top 10 sản phẩm có doanh thu cao nhất là gì?
```

```text
Mã khuyến mãi nào tạo ra doanh thu thuần cao nhất?
```

---

## 2. Key Features

Dataset Upload
Upload CSV or Excel files through Streamlit UI or FastAPI endpoint.

Supported formats:

```text
.csv
.xlsx
.xls
```

---

After upliad, the backend returns:
- dataset ID
- filename
- row count
- column count
- column names
- data types
- preview records

---

Automated Data Profiling / EDA
The system automatically generates dataset profilling information:
- number of rows and columns
- data types
- missing values
- missing percentage
- duplicate rows
- numeric summary
- categorcal summary

---

Natural Language to SQL
Users can ask business questions in Vietnameses or English.

The LLM receives:
- dataset schema
- user question
- SQL generation rules
Then it generates a valid DuckDB SQL query.
Example:
User question:
``` text
Top 10 sản phẩm có số lượng bán nhiều nhất là gì?
```
Generated SQL:
``` text
SELECT product_id, SUM(quantity) AS total_quantity
FROM dataset
GROUP BY product_id
ORDER BY total_quantity DESC
LIMIT 10;
```

---

SQL Query Execution
The generated SQL is executed using DuckDB on the uploaded dataset.
Users cal also manually write SQL queries through the UI.

---

Chart Generation
The system can generate charts from SQL query results using Plotly.
Supported chart types:
- bar
- line
- scatter
- pie
Example chart query:
``` text
SELECT product_id, SUM(quantity) AS total_quantity
FROM dataset
GROUP BY product_id
ORDER BY total_quantity DESC
LIMIT 10;
```

---

Agent Logging
Each AI question is logged with:
- dataset ID
- user question
- generated SQL
- answer
- row count
- latency
- status
- error message
- created timestamp
Logs are stored in:
```test
logs/agent_logs.csv
```
This helps debug the agent and analyze failure cases

---
Evaluation Pipeline
The project includes an evaluation script to test the agent using predefined business questions.
The evaluation trachs:
- SQL execution success
- generated SQL keywords
- latency
- row count
- answer
- error messages
Evaluation files:
```text
evaluation/questions.json
evaluation/run_eval.py
evaluation/eval_results.csv
```

---

## 3. Tech Stack
__Backend__ 
```text
FastAPI
Pydantic
DuckDB
Pandas
Groq API / LLM API
```
__Frontend__
```text
Streamlit
Plotly
Requests
Pandas
```
__AI / LLM__
``` text
Groq API
Llama 3.3 79B Versatile
Natural Language to SQL
LLM-based result explanation
```
__Data Processing__
```text
Pandas
DuckDB
OpenPyXL
```
__Evaluation and Logging__
```text
CSV logging
Custom evaluation script
Latency tracking
SQL keyword validation
```
---
## 4. System Architecture
```text
User
 ↓
Streamlit UI
 ↓
FastAPI Backend
 ↓
AI Agent Logic
 ├── Dataset Profiling Tool
 ├── SQL Query Tool
 ├── LLM SQL Generator
 ├── LLM Result Explainer
 ├── Chart Generation Tool
 ├── Logging Service
 └── Evaluation Script
 ↓
Storage
 ├── Uploaded datasets
 ├── Agent logs
 └── Evaluation results
```
---
## 5. Project Structure
```text
ai-data-analyst-agent/
│
├── backend/
│   └── app/
│       ├── llm/
│       │   ├── __init__.py
│       │   └── groq_client.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── chat_schema.py
│       │   └── dataset_schema.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── dataset_service.py
│       │   ├── chart_service.py
│       │   └── logging_service.py
│       │
│       ├── __init__.py
│       └── main.py
│
├── frontend/
│   └── streamlit_app.py
│
├── data/
│   └── uploads/
│
├── logs/
│   └── agent_logs.csv
│
├── evaluation/
│   ├── questions.json
│   ├── run_eval.py
│   └── eval_results.csv
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
---
## 6. API Endpoints
__Health Check__
``` http
GET /
```
Check if the backend API is running

---
__Chat with LLM__
```http
POST /chat
```
__Resquest body__:
``` JSON
{
  "message": "Explain what an AI Data Analyst Agent does"
}
```
---
__Upload Dataset__
``` http
POST /datases/upload
```
Upload a CSV or Excel file
Response example:
```JSON
 {
  "dataset_id": "abc-123",
  "filename": "order_items.csv",
  "row_count": 714669,
  "column_count": 7,
  "columns": [
    "order_id",
    "product_id",
    "quantity",
    "unit_price",
    "discount_amount",
    "promo_id",
    "promo_id_2"
  ],
  "dtypes": {
    "order_id": "object",
    "product_id": "object",
    "quantity": "int64",
    "unit_price": "float64"
  },
  "preview": []
}
```
---
__Dataset Profile__
```http
GET /datasets/{dataset_id}/profile
```
Returns automated EDA infomation
---
__SQL Query__
```http
POST /datasets/{dataset_id}/query
```
Request body:
``` JSON
{
  "sql": "SELECT * FROM dataset LIMIT 10"
}
```
---
__Ask AI__
```http
POST /datasets/{dataset_id}/ask
```
Request body:
```JSON
{
  "question": "Top 10 sản phẩm có số lượng bán nhiều nhất là gì?"
}
```
Response example:
```JSON
{
  "dataset_id": "abc-123",
  "question": "Top 10 sản phẩm có số lượng bán nhiều nhất là gì?",
  "generated_sql": "SELECT product_id, SUM(quantity) AS total_quantity FROM dataset GROUP BY product_id ORDER BY total_quantity DESC LIMIT 10",
  "row_count": 10,
  "results": [],
  "answer": "..."
}
```
---
__Generate Chart__
```http
POST /datasets/{dataset_id}/chart
```
Request body:
```JSON
{
  "sql": "SELECT product_id, SUM(quantity) AS total_quantity FROM dataset GROUP BY product_id ORDER BY total_quantity DESC LIMIT 10",
  "chart_type": "bar",
  "x": "product_id",
  "y": "total_quantity",
  "title": "Top 10 sản phẩm bán nhiều nhất"
}
```





