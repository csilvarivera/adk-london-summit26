# routing-workflow

**Dynamic Routing Graph Workflow Agent**  
An advanced, graph-based routing agent built with the Google Agent Development Kit (ADK 2.0) orchestration engine. It defines a dynamic graph (`WorkflowAgent`) containing a classification function node, a router event node, and three highly-specialized handler LLM nodes (`billing_handler`, `customer_support_handler`, and `logistics_handler`). Incoming customer requests are automatically categorized by the LLM classifier, and routed simultaneously to the correct billing, customer support, or logistics handler for a direct, professional, and context-aware solution.

### 🚀 Sample Prompt
You can run this agent in the playground or via the CLI with a prompt like:
```bash
agents-cli run "My billing has a bug, it charged me twice. Can support help me refund it?"
```

## Project Structure

```
routing-workflow/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   ├── agent_runtime_app.py    # Agent Runtime application logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |
| `agents-cli deploy`  | Deploy agent to Agent Runtime                                                                |
| `agents-cli publish gemini-enterprise` | Register deployed agent to Gemini Enterprise                    |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment & Platform Registration

### 1. Deploying to Agent Runtime

You can deploy your agent directly to **Agent Runtime** using the modern `agents-cli`:

```bash
# 1. Set your target Google Cloud Project
gcloud config set project <your-project-id>

# 2. Deploy to Agent Runtime
agents-cli deploy
```

> 💡 **Tip:** To supply environment variables during deployment (e.g., matching your `.env-example` keys), use the `--update-env-vars` flag:
> ```bash
> agents-cli deploy --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=<your-project-id>
> ```

---

### 2. Registering with Gemini Enterprise

Once deployed, you can publish and register your agent to the **Gemini Enterprise** platform so users can interact with it.

#### Option A: Interactive Registration (Recommended)
This guides you through registering the agent, automatically querying your GCP project and detecting your deployment metadata:

```bash
agents-cli publish gemini-enterprise --interactive
```

#### Option B: Programmatic Command
If you already know your Gemini Enterprise App ID, register the agent with a single command:

```bash
agents-cli publish gemini-enterprise \
  --gemini-enterprise-app-id "projects/<your-project-id>/locations/global/collections/default_collection/engines/<your-app-id>" \
  --display-name "Routing Workflow Agent" \
  --description "Classifies user messages and routes tasks across specialized sub-agents or handles billing queries directly."
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
