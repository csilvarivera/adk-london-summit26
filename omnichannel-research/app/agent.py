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
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Import custom tools
from app.tools import (
    wikipedia_search_tool,
    text_summarizer_tool,
    google_news_api_tool,
    sentiment_analysis_tool,
    arxiv_search_tool,
    pdf_scraper_tool
)

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Configure root Gemini model
root_model = Gemini(
    model="gemini-3.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# Sub-Agent 1: Wikipedia Expert
def create_wikipedia_expert_agent() -> Agent:
    return Agent(
        name="WikipediaFactualResearcher",
        model=root_model,
        instruction=(
            "Search Wikipedia for the given topic using 'wikipedia_search_tool'. "
            "Extract the core historical context, definitions, and major controversies. "
            "Utilize the 'text_summarizer_tool' if the articles are extremely long. "
            "Return a highly structured factual summary and write your outcome to "
            "the session state under 'wikipedia_results'."
        ),
        description="Extracts foundational background context and historical definitions from Wikipedia.",
        tools=[wikipedia_search_tool, text_summarizer_tool],
        output_key="wikipedia_results"
    )

# Sub-Agent 2: News Analyst
def create_news_analyst_agent() -> Agent:
    return Agent(
        name="CurrentEventsResearcher",
        model=root_model,
        instruction=(
            "Search recent news articles from the last 30 days regarding the topic using 'google_news_api_tool'. "
            "Identify the current public sentiment, major headlines, and emerging trends. "
            "Analyze the collective headline sentiment using the 'sentiment_analysis_tool'. "
            "Return your findings and sentiment analysis scores, writing the outcome "
            "to the session state under 'news_results'."
        ),
        description="Sweeps recent headlines and measures public sentiment regarding the topic.",
        tools=[google_news_api_tool, sentiment_analysis_tool],
        output_key="news_results"
    )

# Sub-Agent 3: Academic Researcher
def create_academic_researcher_agent() -> Agent:
    return Agent(
        name="ScholarlyArticleResearcher",
        model=root_model,
        instruction=(
            "Query academic databases for peer-reviewed papers on the topic using 'arxiv_search_tool'. "
            "Extract the titles, authors, and summary abstracts of the top 3 papers. "
            "Optionally utilize the 'pdf_scraper_tool' to extract deeper methodologies on matching links. "
            "Return your findings, writing the outcome to the session state under 'academic_results'."
        ),
        description="Queries scholarly publications and peer-reviewed journals on arXiv.",
        tools=[arxiv_search_tool, pdf_scraper_tool],
        output_key="academic_results"
    )

# Sub-Agent 4: Merging / Synthesizing Agent
def create_synthesizer_agent() -> Agent:
    return Agent(
        name="OmniChannelSynthesizer",
        model=root_model,
        instruction=(
            "You are a master research synthesizer. Your job is to compile a stunning, comprehensive 360-degree "
            "report on the user's research topic. Ingest the factual data from state '{wikipedia_results}', news "
            "sentiments and headlines from state '{news_results}', and scholarly academic publications from state "
            "'{academic_results}'. Write an authoritative, premium, and well-structured executive summary report "
            "that groups these insights into logical sections with clear markdown titles, tables, bullet highlights, "
            "and scientific citations. Always attribute findings back to their respective channel sources. "
            "Do not use placeholders; provide a fully-detailed brief. Write the output to 'final_report'."
        ),
        description="Synthesizes concurrent factual, news, and scholarly findings into a 360-degree report.",
        tools=[],
        output_key="final_report"
    )


# Define the parallel sweep agent combining the three researchers
comprehensive_research_agent = ParallelAgent(
    name="OmniChannelResearchAgent",
    sub_agents=[
        create_wikipedia_expert_agent(),
        create_news_analyst_agent(),
        create_academic_researcher_agent()
    ],
    description=(
        "Executes a concurrent, multi-disciplinary research sweep. Gathers baseline facts from Wikipedia, "
        "current sentiment from global news, and scholarly data from academic databases simultaneously to "
        "provide a 360-degree view of a topic."
    )
)

# Root Agent: Executes the parallel sweep first, then synthesizes the results
root_agent = SequentialAgent(
    name="ResearchPipelineAgent",
    sub_agents=[
        comprehensive_research_agent,
        create_synthesizer_agent()
    ],
    description="Coordinates concurrent research sweeping and compiles a consolidated executive research brief."
)

# Set up the App container
app = App(
    root_agent=root_agent,
    name="app",
)
