"""Deployment script for MRNA."""

import os
import sys

# Now use an absolute import from the project root
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
from app.agent import app 


# load the environment
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")


print("Project ID:", PROJECT_ID)
print("Location:", LOCATION)
print("Staging bucket:", GOOGLE_CLOUD_STORAGE_BUCKET)
if not PROJECT_ID or not LOCATION or not GOOGLE_CLOUD_STORAGE_BUCKET:
  print(
      "Missing GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, or STAGING_BUCKET",
      file=sys.stderr,
  )
  sys.exit(1)

vertexai.init(
    project=PROJECT_ID,
    location=VERTEX_LOCATION,
    staging_bucket=GOOGLE_CLOUD_STORAGE_BUCKET,
)

def test_local_agent():
  
  # create a local version of your root agent
  app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
  )

  
  session = app.create_session(user_id="u_123")
  session
  for event in app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
  ):
    print(event)


def deploy_agent():
  # Deploy to AgentEngine - Check Cloud Logging for detailed issues.
  remote_agent = agent_engines.create(
      app.root_agent,
          requirements=[
        "google-cloud-aiplatform[adk,agent-engines]",
        "google-adk(>=1.23.0, <=1.32.0)",
        "dotenv",
        "pandas",
        "pydantic>=2.11.3",
        "numpy>=2.3.1",
        "opentelemetry-sdk>=1.36.0",
        "opentelemetry-exporter-otlp-proto-http>=1.36.0",
        "protobuf>=6.31.1,<7.0.0",
        "matplotlib>=3.10.9",
      ],
      extra_packages=["app/agent.py",
      "app/tools.py"],
      display_name="data_reporting",
      env_vars = {
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
      }
    
  )
  print(f"\nSuccessfully created agent: {remote_agent.resource_name}")


def list_agents():
  for agent in agent_engines.list():
    print(agent.display_name)

if __name__ == "__main__":
    try:
        
        # Call the deployment function with the obtained values
        deploy_agent()
        print("\nDeployment script finished.")
        #call_agent()
        
    except (ValueError, FileNotFoundError) as e: # Catch specific known errors
         print(f"Configuration Error: {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e: # Catch any other unexpected errors during the process
        print(f"Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)

