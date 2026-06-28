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
import sys
from dotenv import load_dotenv

# Ensure we can load app package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load local environment variables from app/.env
dotenv_path = os.path.join(os.path.dirname(__file__), "app", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

def main():
    print("==========================================================")
    print("🚀 Initializing Market Analysis Reflection Pipeline Run...")
    print("==========================================================")
    
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="user_1", app_name="market_analysis")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="market_analysis")
    
    query = "Analyze the 2026 Electric Vehicle battery materials market."
    print(f"Running pipeline with query: '{query}'\n")
    
    message = types.Content(
        role="user", parts=[types.Part.from_text(text=query)]
    )
    
    # Run and stream the events
    events = runner.run(
        new_message=message,
        user_id="user_1",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    )
    
    print("🎙️ Streaming Pipeline Execution Log:\n")
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                    
    print("\n\n✅ Pipeline Run Completed Successfully!")
    
    # Fetch final state variables to demonstrate the reflection result
    print("\n==========================================================")
    print("📋 Final Session State Keys & Contents")
    print("==========================================================")
    session_state = session_service.get_session_sync(
        user_id="user_1", session_id=session.id, app_name="market_analysis"
    )
    
    for k, v in session_state.state.items():
        print(f"\n🔑 State Key: '{k}'")
        print("-" * len(k) * 2)
        # Limit to first 25 lines of value if it's too long to save space
        lines = str(v).split("\n")
        if len(lines) > 30:
            print("\n".join(lines[:30]))
            print(f"... [Truncated {len(lines) - 30} lines of detailed report] ...")
        else:
            print(v)
        print("=" * 60)

if __name__ == "__main__":
    main()
