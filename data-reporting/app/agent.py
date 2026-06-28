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

import os
import google.auth
from google.adk.agents import Agent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

# Import custom tools
from app.tools import clean_missing_values, generate_and_save_chart

# Load / fallback GCP credentials
try:
    _, project_id = google.auth.default()
except Exception:
    project_id = "csilvariverademo"

# Set model execution environment (Vertex AI, Global region)
os.environ["GOOGLE_CLOUD_PROJECT"] = "csilvariverademo"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Configure BigQuery Location to US (requested by user)
bq_location = "US"

# Instantiate global shared model configuration
root_model = Gemini(
    model="gemini-3.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# Factory function to build the data cleaner sub-agent
def create_data_cleaner() -> Agent:
    return Agent(
        name="data_cleaner_agent",
        model=root_model,
        instruction=(
            "You are a meticulous Data Cleansing Specialist. Your job is to ingest raw data (either as JSON or raw input), "
            "standardize the layout, and use the 'clean_missing_values' tool to cleanly handle any nulls, NaNs, "
            "or empty values. Impute numeric nulls with the column medians and string/text nulls with 'Unknown'. "
            "You must pass the resulting cleaned data directly to the session state under the 'cleaned_data' key so "
            "that the next agent can analyze it. Always explain briefly how you cleaned the data."
        ),
        description="Ingests raw CSV/JSON data and handles missing values to produce a clean dataset.",
        tools=[clean_missing_values],
        output_key="cleaned_data",
    )

# Factory function to build the data analyzer sub-agent
def create_data_analyzer() -> Agent:
    # Set up BigQuery Toolset with US region and csilvariverademo project ID
    bq_config = BigQueryToolConfig(
        compute_project_id="csilvariverademo",
        location=bq_location,
        write_mode=WriteMode.BLOCKED, # Safe read-only mode for analysis
        max_query_result_rows=100
    )
    bq_tools = BigQueryToolset(bigquery_tool_config=bq_config)

    return Agent(
        name="data_analyzer_agent",
        model=root_model,
        instruction=(
            "You are a brilliant Data Analyst. Your job is to perform statistical analysis and identify trends on the cleaned data. "
            "First, read the cleaned data from the state using '{cleaned_data}' or utilize your BigQuery tools to query "
            "the `csilvariverademo.sample.duplicate_invoice` table if you need additional metrics, context, or schemas. "
            "Your output must be a highly informative, structured summary that outlines the main findings, including: "
            "1. Core descriptive statistics (total records, sum/mean of Invoice Amounts, highest/lowest amounts). "
            "2. Identified trends (such as top spending companies, frequent vendors, or peak dates). "
            "Save your analysis and findings to the state under the 'analysis_results' key. Be thorough and analytical."
        ),
        description="Performs statistical analysis, computes descriptive metrics, and identifies trends.",
        tools=[bq_tools],
        output_key="analysis_results",
    )

# Factory function to build the chart generator sub-agent (possessing custom visual representation skill)
def create_chart_generator() -> Agent:
    return Agent(
        name="chart_generator_agent",
        model=root_model,
        instruction=(
            "You are a skilled Visualization and Reporting Specialist. Your job is to create visual representations "
            "of the trends identified by the analyst. Ingest the statistical analysis findings from state '{analysis_results}' "
            "and call the 'generate_and_save_chart' tool to plot a gorgeous visualization (like invoice amounts by Vendor_id, "
            "Company_Code, or Date). Always save the generated chart as an ADK session-scoped artifact 'chart.png'. "
            "Finally, assemble and output a beautiful, premium markdown report summarizing the entire data reporting pipeline: "
            "1. Summary of Cleansing steps (from the cleaner agent). "
            "2. Summary of Insights and Trends (from the analyzer agent). "
            "3. The generated visualization, embedded directly into your response as a link to the session-scoped artifact 'chart.png'. "
            "Do not use placeholders; output a fully detailed and gorgeous markdown report."
        ),
        description="Creates visual representations (charts) of findings and outputs the final report.",
        tools=[generate_and_save_chart],
        output_key="final_report",
    )

# Define the root agent as a SequentialAgent coordinating the 3 sub-agents
root_agent = SequentialAgent(
    name="DataReportingAgent",
    sub_agents=[
        create_data_cleaner(),
        create_data_analyzer(),
        create_chart_generator(),
    ],
    description="Processes raw data through cleaning, analysis, visualization, and final report generation."
)

# Set up the App container
app = App(
    root_agent=root_agent,
    name="app",
)
