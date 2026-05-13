# Coding Agent Guide

## Prerequisites

Install the CLI (one-time):
```bash
uv tool install google-agents-cli
```

---

## Project Overview

This is an automated monitoring agent that tracks third-party mentions of Google Agents CLI across the web. It uses Google Search Grounding to find content on news sites, blogs, YouTube, social media, and other platforms, then validates and stores relevant mentions.

### Key files
- `app/agent.py` — agent definition, system prompt, tool configuration
- `app/tools/batch_search.py` — executes 41 search queries targeting third-party platforms
- `app/tools/search_grounding.py` — Google Search Grounding API integration with redirect resolution
- `app/tools/search.py` — pattern detection and relevance validation (excludes Google first-party content)
- `app/tools/tracking.py` — read/write tracking file (local or GCS), duplicate detection
- `run_monitoring_sweep.py` — standalone script for batch search + validation workflow
- `.deploy.yaml` — Cloud Run and Cloud Scheduler configuration

### Environment variables
All configuration is in env vars (see `.env.example`):
- `GOOGLE_CLOUD_PROJECT` — your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` — region for Gemini API (us-central1)
- `GOOGLE_GENAI_USE_VERTEXAI` — use Vertex AI (True)
- `TRACKING_FILE_PATH` — where to store results (local: data/agents_cli_mentions.md or GCS: gs://bucket/file.md)

### Architecture

**Search Strategy**: The agent runs 41 optimized queries targeting third-party platforms:
- Platform-specific: "agents-cli medium", "agents-cli infoq", "agents-cli reddit"
- Tutorial searches: "agents-cli tutorial", "agents-cli walkthrough"
- Video content: "agents-cli youtube", "agents-cli demo"
- International: "agents-cli français", "agents-cli 日本語"

**Validation Logic**: Three-tier confidence scoring system:
- High confidence (0.4 points): explicit "agents-cli" mentions, CLI commands
- Medium confidence (0.2 points): tutorials, videos with agent context
- Low confidence (0.1 points): tech publications mentioning agents

**First-Party Filtering**: Excludes all Google-owned domains to focus on third-party coverage:
- google.github.io, docs.cloud.google.com, adk.dev, cloud.google.com, etc.

**Results Storage**: Markdown file with URL list, stored in GCS for persistence

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, understand the project's requirements, constraints, and success criteria.

**For this project**: The goal is to discover NEW third-party content about Agents CLI, not to catalog Google's own documentation. Evaluation dataset has 7 third-party URLs, 10 social media URLs, and 9 first-party URLs (which should be excluded).

### Phase 2: Build and Implement
Implement agent logic in `app/`. Use `agents-cli playground` for interactive testing. Iterate based on user feedback.

**For this project**: The main workflow is implemented in `run_monitoring_sweep.py` which:
1. Reads existing tracking file
2. Runs batch search (41 queries)
3. Validates each URL using pattern detection
4. Saves new valid URLs to tracking file

### Phase 3: The Evaluation Loop (Main Iteration Phase)
Start with 1-2 eval cases, run `agents-cli eval run`, iterate. Expect 5-10+ iterations. See the **Evaluation Guide** for metrics, evalset schema, LLM-as-judge config, and common gotchas.

**For this project**: Evaluation is based on recall against known third-party URLs. Current performance: 42.9% recall on third-party eval set (3/7 URLs matched). The system has discovered 20 additional URLs not in the evaluation dataset across 11 different platforms.

### Phase 4: Pre-Deployment Tests
Run `uv run pytest tests/unit tests/integration`. Fix issues until all tests pass.

**For this project**: Test locally first:
```bash
# Test the monitoring sweep
uv run python scripts/test_sweep.py

# Test with GCS (requires auth)
export TRACKING_FILE_PATH=gs://your-bucket/agents_cli_mentions.md
uv run python run_monitoring_sweep.py
```

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `agents-cli deploy` only after user confirms. See the **Deployment Guide** for details.

**For this project**: Deployment creates:
- Cloud Run service (agents-cli-monitor) in us-central1
- Cloud Scheduler job running daily at 9:07 AM Pacific
- Automatic GCS integration for persistent storage

### Phase 6: Production Deployment
Ask the user: Option A (simple single-project) or Option B (full CI/CD pipeline with `agents-cli infra cicd`).

## Development Commands

| Command | Purpose |
|---------|---------|
| `agents-cli playground` | Interactive local testing |
| `uv run python run_monitoring_sweep.py` | Run monitoring sweep locally |
| `uv run python scripts/test_sweep.py` | Test sweep with detailed output |
| `uv run python scripts/view_results.py` | View tracking file contents |
| `./scripts/trigger_sweep.sh` | Manually trigger Cloud Run deployment |
| `agents-cli eval run` | Run evaluation against evalsets |
| `agents-cli lint` | Check code quality |
| `agents-cli deploy` | Deploy to Cloud Run |

---

## Operational Guidelines for Coding Agents

- **Code preservation**: Only modify code directly targeted by the user's request. Preserve all surrounding code, config values (e.g., `model`), comments, and formatting.
- **NEVER change the model** unless explicitly asked.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (e.g., `global` instead of `us-east1`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module: `from google.adk.tools.load_web_page import load_web_page`
- **Run Python with `uv`**: `uv run python script.py`. Run `agents-cli install` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause instead of retrying.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of retrying creation.

---

## Project-Specific Guidelines

### DO NOT Cheat or Overfit
- Do NOT use evaluation data to improve search queries
- Focus on discovering NEW third-party content, not matching known URLs
- If you discover content that's in the eval set, it's by legitimate search, not cheating

### Search Quality Over Quantity
- The batch search already runs 41 queries - don't add more unless truly valuable
- Focus on improving pattern detection and validation, not search volume
- Timeout is 540 seconds (9 minutes) - keep total execution time under this limit

### First-Party Content is NOT Success
- Exclude all Google-owned domains (google.github.io, docs.cloud.google.com, adk.dev, etc.)
- The goal is third-party adoption and community content only
- Finding Google's own docs is not a monitoring success

### Confidence Threshold
- Current threshold: 0.3 (minimum for relevance)
- Don't lower the threshold to increase recall - this adds false positives
- Instead, improve pattern detection to better identify genuine mentions

### Title Extraction
- Parse titles from Gemini's formatted text response, not from grounding_metadata
- Use regex patterns to extract from formats like "* **Title:** Actual Title"
- Fallback to domain name only if no title can be extracted
