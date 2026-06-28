# ruff: noqa
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
from typing import Any
import google.auth

from google.adk.workflow import Workflow, START
from google.adk.events.event import Event
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.genai import types
from pydantic import model_validator

# Setup GCP Project/Location for Gemini Enterprise
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# Custom WorkflowAgent class that dynamically groups user-provided 3-tuple edges
# (from_node, to_node, route) into a valid ADK 2.0 routing map (dict).
class WorkflowAgent(Workflow):
    def __init__(self, name: str, edges: list, **kwargs):
        processed_edges = []
        conditional_groups = {}
        for edge in edges:
            if isinstance(edge, tuple) and len(edge) == 3:
                from_node, to_node, route = edge
                if from_node not in conditional_groups:
                    conditional_groups[from_node] = {}
                conditional_groups[from_node][route] = to_node
            else:
                processed_edges.append(edge)
        
        for from_node, routing_map in conditional_groups.items():
            processed_edges.append((from_node, routing_map))
            
        super().__init__(name=name, edges=processed_edges, **kwargs)


# Custom Content class that inherits from types.Content but adds a Pydantic 
# before-validator to auto-coerce incoming strings into a valid dict structure.
class Content(types.Content):
    @model_validator(mode="before")
    @classmethod
    def _coerce_content(cls, v: Any) -> Any:
        if isinstance(v, str):
            return {"role": "user", "parts": [{"text": v}]}
        return v

# Override types.Content with our custom class to ensure that any type hints
# in the node signatures referencing types.Content will resolve to this class.
types.Content = Content


# 1. Classifier Node (uses Gemini API internally as a FunctionNode to prevent streaming raw classification labels)
def classifier(node_input: types.Content) -> str:
    from google import genai
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"""Classify the user message into one or more of these categories: "BILLING", "CUSTOMER_SUPPORT", or "LOGISTICS".
If the message is about the user's bill, billing, payment, or invoice, classify it as "BILLING".
If the message applies to more than one category, reply with a comma-separated list of categories. Do not include any other text or explanation.

User message: {node_input.parts[0].text}""",
    )
    return response.text.strip()

# 2. Router Function Node
def router(node_input: str):
    routes = node_input.split(",")
    routes = [route.strip() for route in routes]
    yield Event(route=routes)

# 3. Handler LLM Agent Nodes
billing_handler = LlmAgent(
    name="billing_handler",
    model="gemini-3.5-flash",
    instruction="You are the billing specialist. If the user asks about their bill or billing, generate a direct, professional, and helpful response addressing the customer's billing or bill query.",
)

customer_support_handler = LlmAgent(
    name="customer_support_handler",
    model="gemini-3.5-flash",
    instruction="You are a specialized customer support assistant. Generate a helpful response addressing the customer's general support query.",
)

logistics_handler = LlmAgent(
    name="logistics_handler",
    model="gemini-3.5-flash",
    instruction="You are a specialized logistics and shipping support assistant. Generate a helpful response addressing the customer's shipping or delivery query.",
)

# 4. Collector / Join Node
def collector(node_input: Any):
    yield

# 5. Workflow Definition using the user's requested syntax
t_agent = WorkflowAgent(
   name="routing_workflow",
   edges=[
       ("START", classifier),
       (classifier, router),
       (router, billing_handler, "BILLING"),
       (router, customer_support_handler, "CUSTOMER_SUPPORT"),
       (router, logistics_handler, "LOGISTICS"),
       (billing_handler, collector),
       (customer_support_handler, collector),
       (logistics_handler, collector),
   ],
)

# 5. App Container
root_agent = t_agent

app = App(
    root_agent=root_agent,
    name="app",
)
