import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class VisualizationEngine:
    @staticmethod
    def _get_best_columns(df: pd.DataFrame):
        """Auto-detect best x (categorical) and y (numeric) columns."""
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        x = categorical_cols[0] if categorical_cols else (numeric_cols[0] if numeric_cols else None)
        y = numeric_cols[0] if numeric_cols else None
        return x, y

    @staticmethod
    def generate_chart(df: pd.DataFrame, chart_type: str, x_col: str = None, y_col: str = None, title: str = "") -> go.Figure:
        """
        Dynamically generates a Plotly chart based on inputs.
        Auto-detects best columns if x_col/y_col are None or invalid.
        """
        # Validate columns exist in df
        valid_cols = df.columns.tolist()
        if x_col not in valid_cols:
            x_col = None
        if y_col not in valid_cols:
            y_col = None

        # Auto-detect fallback columns
        auto_x, auto_y = VisualizationEngine._get_best_columns(df)
        if x_col is None:
            x_col = auto_x
        if y_col is None:
            y_col = auto_y

        # Handle degenerate states
        if x_col is None and y_col is None:
            raise ValueError("Dataset has no plottable columns.")

        chart_type = (chart_type or "bar").lower()

        try:
            if chart_type == 'bar':
                if df[x_col].dtype == object or pd.api.types.is_categorical_dtype(df[x_col]):
                    agg_df = df.groupby(x_col)[y_col].mean().reset_index()
                    fig = px.bar(agg_df, x=x_col, y=y_col, title=title, color=x_col)
                else:
                    fig = px.bar(df, x=x_col, y=y_col, title=title)
            elif chart_type == 'scatter':
                fig = px.scatter(df, x=x_col, y=y_col, title=title, trendline="ols" if len(df) > 5 else None)
            elif chart_type == 'line':
                fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
            elif chart_type == 'pie':
                agg_df = df.groupby(x_col)[y_col].sum().reset_index()
                fig = px.pie(agg_df, names=x_col, values=y_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=y_col or x_col, title=title, nbins=20)
            elif chart_type == 'box':
                fig = px.box(df, x=x_col, y=y_col, title=title, color=x_col)
            else:
                # Fallback to bar
                agg_df = df.groupby(x_col)[y_col].mean().reset_index() if df[x_col].dtype == object else df
                fig = px.bar(agg_df, x=x_col, y=y_col, title=f"Bar Chart: {title}")

        except Exception as e:
            # Last resort fallback: simple numeric histogram
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            else:
                raise ValueError(f"Cannot generate chart: {str(e)}")
            
        fig.update_layout(
            template="plotly_dark",
            margin=dict(t=60, b=30, l=30, r=30),
            title_font_size=16
        )
        return fig

    @staticmethod
    def generate_overview_charts(df: pd.DataFrame) -> list:
        """Generates a set of auto-selected overview charts for the dataset."""
        charts = []
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(include='object').columns.tolist()

        # Histogram for each numeric column (max 3)
        for col in numeric_cols[:3]:
            fig = px.histogram(df, x=col, title=f"Distribution of {col}", nbins=20, template="plotly_dark")
            charts.append((f"Histogram: {col}", fig))

        # Bar chart for categorical columns (max 2)
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols[:2]:
                agg = df.groupby(cat_col)[numeric_cols[0]].mean().reset_index()
                fig = px.bar(agg, x=cat_col, y=numeric_cols[0], color=cat_col,
                             title=f"Avg {numeric_cols[0]} by {cat_col}", template="plotly_dark")
                charts.append((f"Bar: {cat_col} vs {numeric_cols[0]}", fig))

        return charts
