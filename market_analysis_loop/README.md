# market-analysis-loop

**Market Analysis Self-Improving Loop Agent**  
An advanced, self-improving market research agent utilizing the `LoopAgent` pattern to drive an iterative reflection process (Draft $\rightarrow$ Critique $\rightarrow$ Revise). It coordinates an industry-specialized Writer and an executive Editor equipped with a curated market intelligence database (and Wikipedia fallback search) to deliver publication-ready, deeply-critiqued business briefs. It automatically exits the loop once high quality standards are achieved.

### 🚀 Sample Prompt
You can run this agent in the playground or via the CLI with a prompt like:
```bash
agents-cli run "Analyze the 2026 Electric Vehicle battery materials market."
```

Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.41.3`

## Project Structure

```
market-analysis-loop/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
├── Makefile                   # Development commands
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install dependencies using uv                                                               |
| `make playground`    | Launch local development environment                                                        |
| `make lint`          | Run code quality checks                                                                     |
| `make test`          | Run unit and integration tests                                                              |

For full command options and usage, refer to the [Makefile](Makefile).

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `uvx agent-starter-pack enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `uvx agent-starter-pack setup-cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `uvx agent-starter-pack upgrade` | Auto-upgrade to latest version while preserving customizations |
| `uvx agent-starter-pack extract` | Extract minimal, shareable version of your agent |

---

## Development

Edit your agent logic in `app/agent.py` and test with `make playground` - it auto-reloads on save.
See the [development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide) for the full workflow.

## Deployment & Platform Registration

### 1. Deploying to Agent Runtime

#### Option A: Using Google Agents CLI (Recommended)
You can deploy your agent directly to **Agent Runtime** using the modern `agents-cli`:

```bash
# 1. Set your target Google Cloud Project
gcloud config set project <your-project-id>

# 2. Deploy to Agent Runtime
agents-cli deploy
```

> 💡 **Tip:** To supply environment variables during deployment (e.g., matching your `.env-example` keys), use the `--update-env-vars` flag:
> ```bash
> agents-cli deploy --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=True,VERTEX_LOCATION=us-central1,BIGQUERY_LOCATION=US,GOOGLE_CLOUD_STORAGE_BUCKET=gs://your-staging-bucket-name
> ```

#### Option B: Programmatic Deployment via Makefile / `deploy.py`
Alternatively, you can run the pre-configured programmatic Python deployment script using `make`:

```bash
# Ensure your environment variables are configured in your local .env file, then run:
make deploy
```

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
  --display-name "Market Analysis Loop Agent" \
  --description "Executes deep critique and refinement loops to deliver market analysis briefs."
```

To add CI/CD and Terraform, run `uvx agent-starter-pack enhance`.
To set up your production infrastructure, run `uvx agent-starter-pack setup-cicd`.
See the [deployment guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment) for details.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
See the [observability guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability) for queries and dashboards.
