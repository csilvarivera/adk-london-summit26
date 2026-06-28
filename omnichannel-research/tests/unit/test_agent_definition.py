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

from app.agent import (
    create_wikipedia_expert_agent,
    create_news_analyst_agent,
    create_academic_researcher_agent,
    create_synthesizer_agent,
    comprehensive_research_agent,
    root_agent,
    app
)
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.apps import App


def test_wikipedia_expert_agent_definition() -> None:
    """Verifies wikipedia expert sub-agent parameters and tools."""
    agent = create_wikipedia_expert_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "WikipediaFactualResearcher"
    assert agent.output_key == "wikipedia_results"
    assert len(agent.tools) == 2
    tool_names = [t.__name__ for t in agent.tools]
    assert "wikipedia_search_tool" in tool_names
    assert "text_summarizer_tool" in tool_names


def test_news_analyst_agent_definition() -> None:
    """Verifies news analyst sub-agent parameters and tools."""
    agent = create_news_analyst_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "CurrentEventsResearcher"
    assert agent.output_key == "news_results"
    assert len(agent.tools) == 2
    tool_names = [t.__name__ for t in agent.tools]
    assert "google_news_api_tool" in tool_names
    assert "sentiment_analysis_tool" in tool_names


def test_academic_researcher_agent_definition() -> None:
    """Verifies academic researcher sub-agent parameters and tools."""
    agent = create_academic_researcher_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "ScholarlyArticleResearcher"
    assert agent.output_key == "academic_results"
    assert len(agent.tools) == 2
    tool_names = [t.__name__ for t in agent.tools]
    assert "arxiv_search_tool" in tool_names
    assert "pdf_scraper_tool" in tool_names


def test_synthesizer_agent_definition() -> None:
    """Verifies synthesizer sub-agent parameters."""
    agent = create_synthesizer_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "OmniChannelSynthesizer"
    assert agent.output_key == "final_report"
    assert len(agent.tools) == 0


def test_parallel_research_agent_orchestration() -> None:
    """Verifies parallel sweep agent combines the three researchers concurrently."""
    assert isinstance(comprehensive_research_agent, ParallelAgent)
    assert comprehensive_research_agent.name == "OmniChannelResearchAgent"
    assert len(comprehensive_research_agent.sub_agents) == 3
    
    sub_agent_names = [sa.name for sa in comprehensive_research_agent.sub_agents]
    assert "WikipediaFactualResearcher" in sub_agent_names
    assert "CurrentEventsResearcher" in sub_agent_names
    assert "ScholarlyArticleResearcher" in sub_agent_names


def test_root_sequential_agent_orchestration() -> None:
    """Verifies root agent executes parallel research first then compiles via synthesizer."""
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.name == "ResearchPipelineAgent"
    assert len(root_agent.sub_agents) == 2
    
    # Check execution sequence order
    assert root_agent.sub_agents[0].name == "OmniChannelResearchAgent"
    assert root_agent.sub_agents[1].name == "OmniChannelSynthesizer"


def test_app_container() -> None:
    """Verifies app naming matches the local execution environment."""
    assert isinstance(app, App)
    assert app.name == "app"
    assert app.root_agent == root_agent
