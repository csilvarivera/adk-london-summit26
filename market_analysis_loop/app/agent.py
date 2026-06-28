# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Load local environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Import custom tools
from app.tools import fetch_market_intelligence, exit_loop

# Standard Google Cloud environment credentials configuration
try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
except Exception:
    pass

# Ensure location and execution properties are correctly configured
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Model definition (Gemini 3.5 Flash)
shared_model = Gemini(
    model="gemini-3.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# 1. Generator Agent (Drafts the initial report)
market_analysis_generator = Agent(
    name="market_analysis_generator",
    model=shared_model,
    instruction=(
        "You are an elite, senior market research analyst.\n"
        "Your task is to research the target industry requested by the user. Use the `fetch_market_intelligence` tool to gather "
        "accurate, data-backed details (sizing, growth, cagr, drivers, challenges, and competitors).\n"
        "Then, write a high-quality initial raw draft of the market analysis report.\n"
        "This is a first working draft. Focus on presenting the raw facts, numbers, and data points cleanly, but do NOT "
        "worry about formatting them into highly polished, comprehensive, or narrative executive analysis paragraphs yet. "
        "Keep sections like SWOT and Strategic Recommendations very brief or in raw bullet points, as those will be elaborated "
        "during the refinement loop.\n"
        "Your draft must use the following structure:\n"
        "1. Executive Summary\n"
        "2. Market Size, Growth, and CAGR (be extremely precise with actual figures from the tool)\n"
        "3. Key Market Drivers (raw data-backed details)\n"
        "4. Industry Challenges and Bottlenecks\n"
        "5. Key Competitors, Market Shares, and Strategic Focus Areas\n"
        "6. Initial SWOT Analysis (raw bullets)\n"
        "7. Actionable Strategic Recommendations (brief overview)\n\n"
        "Save your initial raw draft to the state key `market_analysis_draft`."
    ),
    description="Researches the market sector and writes a highly rigorous, structured initial analysis draft.",
    tools=[fetch_market_intelligence],
    output_key="market_analysis_draft",
)

# 2. Critic Agent (Editor in Loop)
critic_agent_in_loop = Agent(
    name="critic_agent_in_loop",
    model=shared_model,
    instruction=(
        "You are an exceptionally strict, demanding, and meticulous Executive Editor-in-Chief.\n"
        "Your task is to critically evaluate the market analysis draft found in the state variable `{market_analysis_draft}`.\n"
        "Assess the draft on the following standards:\n"
        "1. Data Integrity: Are all numbers, CAGR %, sizing estimates, and competitor shares correctly and fully utilized?\n"
        "2. Narrative Depth: Are SWOT and Challenges expanded into rich, detailed paragraphs explaining 'why' and 'how', or are they just raw bullets?\n"
        "3. Actionable Outlook: Are the strategic recommendations concrete, structured, and deeply realistic for the specific competitors?\n"
        "4. Visual and Executive Polish: Is the formatting stunning, utilizing elegant tables, ASCII-art volume projections, and authoritative language?\n\n"
        "CRITICAL TERMINATION DECISION:\n"
        "- Since you demand absolute masterclass-grade, publication-ready quality, you MUST NEVER approve the initial raw draft (on the very first iteration). "
        "You must reject it and request detailed expansions and narrative polish. Provide extremely specific, bulleted, and constructive editorial annotations "
        "on how to turn the raw points into narrative masterpieces (e.g., expanding the SWOT, detailing the future outlook, adding structured sections).\n"
        "- Only when the draft has gone through at least one round of critique and revision, and fully incorporates all of your previous requested improvements, "
        "should you call the `exit_loop` tool to finalize the process.\n"
        "Write your detailed editorial annotations to the output state key `critic_feedback`."
    ),
    description="Critically reviews the current draft and decides whether to approve (exit loop) or request revisions.",
    tools=[exit_loop],
    output_key="critic_feedback",
)

# 3. Refiner Agent (Writer in Loop)
refiner_agent_in_loop = Agent(
    name="refiner_agent_in_loop",
    model=shared_model,
    instruction=(
        "You are an expert senior business report writer.\n"
        "Your task is to revise and improve the current market analysis report found in `{market_analysis_draft}` "
        "by fully incorporating the editorial feedback and critiques found in `{critic_feedback}`.\n\n"
        "For every gap, issue, or request raised by the editor, rewrite the corresponding section to be deeper, "
        "more professional, and fully complete. Ensure all facts are cohesive and the final output is highly polished.\n"
        "Do not invent fake stats, but expand details, elaborate SWOT points, and refine strategic recommendations.\n"
        "Write your fully revised and improved market analysis report back to the state key `market_analysis_draft`."
    ),
    description="Polishes and revises the report based on the editor's constructive feedback, rewriting back to the draft.",
    output_key="market_analysis_draft",
)

# 4. Refinement Loop Agent (Manages the editor-writer iteration cycle)
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[critic_agent_in_loop, refiner_agent_in_loop],
    max_iterations=5,
)

# 5. Root Pipeline (Sequence: 1. Generate first draft, 2. Run critique-revision loop)
root_agent = SequentialAgent(
    name="MarketAnalysisPipeline",
    sub_agents=[market_analysis_generator, refinement_loop],
)

app = App(
    root_agent=root_agent,
    name="app",
)
