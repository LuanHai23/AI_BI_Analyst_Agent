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
Bacnkend 
```text
FastAPI
Pydantic
DuckDB
Pandas
Groq API / LLM API
```
Frontend
```text
Streamlit
Plotly
Requests
Pandas
```
AI / LLM
``` text
Groq API
Llama 3.3 79B Versatile
Natural Language to SQL
LLM-based result explanation
```
Data Processing
```text
Pandas
DuckDB
OpenPyXL
```
Evaluation and Logging
```text
CSV logging
Custom evaluation script
Latency tracking
SQL keyword validation
```
---
## 4. System Architecture




