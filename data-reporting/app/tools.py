# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import json
import pandas as pd
import matplotlib.pyplot as plt
from google.adk.tools import ToolContext
from google.genai import types

def clean_missing_values(raw_data_json: str) -> dict:
    """Cleans a raw dataset represented as a JSON string, handling missing and null values.

    This tool is perfect for taking dirty, raw data (CSV/JSON representation), filling in 
    missing numbers with column medians, setting missing text fields to 'Unknown', and 
    returning a pristine, structured dataset.

    Args:
        raw_data_json: A JSON string representing list of records (e.g. '[{"col1": 1, "col2": null}]').

    Returns:
        A dictionary with keys 'status' and 'cleaned_data' (list of cleaned records).
    """
    try:
        data = json.loads(raw_data_json)
        df = pd.DataFrame(data)
        
        # Numeric columns: impute nulls with median
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
                
        # Non-numeric columns: fill with 'Unknown'
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns
        for col in non_numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna("Unknown")
                
        cleaned_records = df.to_dict(orient='records')
        return {
            "status": "success",
            "cleaned_data": cleaned_records
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def generate_and_save_chart(
    data_json: str, 
    chart_title: str, 
    x_column: str, 
    y_column: str, 
    chart_type: str = "bar",
    tool_context: ToolContext = None
) -> dict:
    """Generates a professional data visualization chart using matplotlib and saves it as an ADK session artifact.

    Args:
        data_json: A JSON string containing a list of objects/records to plot.
        chart_title: The title of the generated chart.
        x_column: Name of the column to place on the X-axis.
        y_column: Name of the column to place on the Y-axis.
        chart_type: Type of chart to generate ('bar', 'line', or 'pie'). Defaults to 'bar'.

    Returns:
        A dictionary containing the status of the operation and the name of the saved artifact.
    """
    try:
        # Load and prepare data
        records = json.loads(data_json)
        df = pd.DataFrame(records)
        
        # Verify columns exist
        if x_column not in df.columns or y_column not in df.columns:
            return {
                "status": "error",
                "message": f"Columns {x_column} or {y_column} not found in the dataset. Available columns: {list(df.columns)}"
            }
            
        # Clear previous plots
        plt.clf()
        plt.figure(figsize=(6, 4))
        
        # Plot data
        if chart_type == "line":
            plt.plot(df[x_column], df[y_column], marker='o', color='#1a73e8', linewidth=2)
        elif chart_type == "pie":
            plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%', colors=['#1a73e8', '#34a853', '#fbbc05', '#ea4335', '#4285f4'])
        else: # default to bar
            plt.bar(df[x_column], df[y_column], color='#1a73e8')
            
        plt.title(chart_title, fontsize=11, fontweight='bold', pad=10)
        plt.xlabel(x_column, fontsize=9)
        plt.ylabel(y_column, fontsize=9)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        
        # Save plot to an in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_bytes = buf.read()
        buf.close()
        plt.close()
        
        # Save as an ADK artifact
        if tool_context is not None:
            part = types.Part(inline_data=types.Blob(mime_type="image/png", data=img_bytes))
            version = await tool_context.save_artifact("chart.png", part)
            return {
                "status": "success",
                "message": f"Successfully generated chart '{chart_title}' and saved as session artifact 'chart.png' (version {version}).",
                "artifact_name": "chart.png",
                "version": version
            }
        else:
            # Fallback for testing without ToolContext
            with open("chart.png", "wb") as f:
                f.write(img_bytes)
            return {
                "status": "success",
                "message": "Successfully generated chart and saved locally as 'chart.png' (no ToolContext was active).",
                "artifact_name": "chart.png"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate chart: {str(e)}"
        }
