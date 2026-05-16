import json
import pandas as pd
import plotly.express as px

class ChartService:
    # def ni check chart type có được sp khum
    def validate_chart_type(self, chart_type: str) -> None:
        # List chart hiện tại
        supported_chart_types = ["bar","line", "scatter", "pie"]

        # Nếu chart type không nằm trong danh sách thì báo error
        if chart_type not in supported_chart_types:
            raise ValueError(
                f"Unsupported chart type '{chart_type}'"
                f"Supported types are: {supported_chart_types}"
            )
    # Hàm dưới dùng để check cột x và y có tồn tại trong kq query không
    def validate_chart_columns(self, df: pd.DataFrame, x: str, y: str) -> None:
        # Check columns x
        if x not in df.columns:
            raise ValueError(f"Column '{x}' does not exist in quert result")
        
        # Check column y
        if y not in df.columns:
            raise ValueError(f"Column '{y}' does not exist in query results")
    
    # Hàm này tạo biểu đồ plotly từ DF
    def create_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x: str,
        y: str,
        title: str | None = None,
    ) -> str:
        # Check lại chart có match kh
        self.validate_chart_type(chart_type)

        # Check x/y có trong DF không
        self.validate_chart_columns(df, x, y)

        # Nếu user không truyền title tự tạo title
        chart_title = title or f"{chart_type.title()} chart of {y} by {x}"

        # Tạo bar chart
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, title = chart_title)

        # Tạo line chart
        elif chart_type == "scatter":
            fig = px.line(df, x=x, y=y, title=chart_title)

        # Tạo scatter chart
        elif chart_title == "scatter":
            fig = px.scatter(df, x=x, y=y, title=chart_title)

        # Tạo pie chart
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y, title=chart_title)
        
        # Convert Plotly figure thành json string
        chart_json = fig.to_json()
        
        # Trả về json string
        return chart_json
    