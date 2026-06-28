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

from app.tools import fetch_market_intelligence, exit_loop
from app.agent import (
    market_analysis_generator,
    critic_agent_in_loop,
    refiner_agent_in_loop,
    refinement_loop,
    root_agent,
)
from google.adk.agents import Agent, SequentialAgent, LoopAgent


def test_fetch_market_intelligence_curated() -> None:
    """Verifies that the market intelligence tool returns high-quality curated data for matching topics."""
    # Test matching "Electric Vehicles" case-insensitively
    result = fetch_market_intelligence("Electric Vehicles")
    assert result["status"] == "success"
    assert "Curated Market" in result["source"]
    data = result["data"]
    assert "EV" in data["sector_name"]
    assert "Tesla Inc." in [c["name"] for c in data["key_competitors"]]
    assert "BYD Auto Co., Ltd." in [c["name"] for c in data["key_competitors"]]
    assert len(data["key_drivers"]) > 0
    assert len(data["challenges"]) > 0


def test_fetch_market_intelligence_fallback() -> None:
    """Verifies that the tool handles unmatched topics gracefully with fallback search/generation logic."""
    result = fetch_market_intelligence("Sub-Orbital Space Tourism")
    assert result["status"] == "success"
    assert "Fallback" in result["source"] or "Wikipedia" in result["source"]
    data = result["data"]
    assert data["sector_name"] == "Sub-Orbital Space Tourism"
    assert len(data["key_drivers"]) > 0
    assert len(data["challenges"]) > 0


def test_agent_structure_instantiation() -> None:
    """Verifies that all required agents, loop orchestrators, and root pipelines are correctly instantiated."""
    # Check that individual agents are standard LlmAgents (type Agent)
    assert isinstance(market_analysis_generator, Agent)
    assert isinstance(critic_agent_in_loop, Agent)
    assert isinstance(refiner_agent_in_loop, Agent)

    # Check loop agent
    assert isinstance(refinement_loop, LoopAgent)
    assert refinement_loop.name == "RefinementLoop"
    assert refinement_loop.max_iterations == 5
    assert refinement_loop.sub_agents == [critic_agent_in_loop, refiner_agent_in_loop]

    # Check parent pipeline
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.name == "MarketAnalysisPipeline"
    assert root_agent.sub_agents == [market_analysis_generator, refinement_loop]


def test_agent_tools_and_outputs() -> None:
    """Verifies the correct tool bindings and output keys across agents to ensure proper state-sharing."""
    # Generator should use fetch_market_intelligence and output to draft
    assert fetch_market_intelligence in market_analysis_generator.tools
    assert market_analysis_generator.output_key == "market_analysis_draft"

    # Critic (Editor) should use exit_loop and output feedback
    assert exit_loop in critic_agent_in_loop.tools
    assert critic_agent_in_loop.output_key == "critic_feedback"

    # Refiner should write back to the draft key
    assert refiner_agent_in_loop.output_key == "market_analysis_draft"


def test_exit_loop_safeguard() -> None:
    """Verifies that the custom exit_loop safeguard prevents exiting on the first iteration."""
    from unittest.mock import MagicMock

    # Test case 1: No feedback in state (first iteration)
    mock_context = MagicMock()
    mock_context.state = {}
    mock_context.actions.escalate = False
    mock_context.actions.skip_summarization = False

    result = exit_loop(mock_context)
    assert result["status"] == "error"
    assert "Cannot exit the loop on the very first iteration" in result["message"]
    assert mock_context.actions.escalate is False

    # Test case 2: Previous feedback exists (subsequent iteration)
    mock_context.state = {"critic_feedback": "Looks good but expand SWOT."}
    result = exit_loop(mock_context)
    assert result["status"] == "success"
    assert mock_context.actions.escalate is True
    assert mock_context.actions.skip_summarization is True

