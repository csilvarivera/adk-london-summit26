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
    create_data_cleaner,
    create_data_analyzer,
    create_chart_generator,
    root_agent,
    app
)
from google.adk.agents import Agent, SequentialAgent
from google.adk.apps import App


def test_data_cleaner_agent_definition() -> None:
    """Tests that the data cleaner agent is defined with the correct parameters."""
    cleaner = create_data_cleaner()
    assert isinstance(cleaner, Agent)
    assert cleaner.name == "data_cleaner_agent"
    assert cleaner.output_key == "cleaned_data"
    assert len(cleaner.tools) == 1
    assert cleaner.tools[0].__name__ == "clean_missing_values"


def test_data_analyzer_agent_definition() -> None:
    """Tests that the data analyzer agent is defined with the correct parameters."""
    analyzer = create_data_analyzer()
    assert isinstance(analyzer, Agent)
    assert analyzer.name == "data_analyzer_agent"
    assert analyzer.output_key == "analysis_results"
    assert len(analyzer.tools) == 1
    # The tool should be BigQueryToolset
    assert analyzer.tools[0].__class__.__name__ == "BigQueryToolset"


def test_chart_generator_agent_definition() -> None:
    """Tests that the chart generator agent is defined with the correct parameters."""
    generator = create_chart_generator()
    assert isinstance(generator, Agent)
    assert generator.name == "chart_generator_agent"
    assert generator.output_key == "final_report"
    assert len(generator.tools) == 1
    assert generator.tools[0].__name__ == "generate_and_save_chart"


def test_sequential_agent_orchestration() -> None:
    """Tests that the root sequential agent is correctly composed and sequenced."""
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.name == "DataReportingPipelineAgent"
    assert len(root_agent.sub_agents) == 3
    
    # Check execution sequence order
    assert root_agent.sub_agents[0].name == "data_cleaner_agent"
    assert root_agent.sub_agents[1].name == "data_analyzer_agent"
    assert root_agent.sub_agents[2].name == "chart_generator_agent"


def test_app_container() -> None:
    """Tests that the ADK App container is properly initialized."""
    assert isinstance(app, App)
    assert app.name == "app"
    assert app.root_agent == root_agent
