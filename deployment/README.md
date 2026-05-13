# Deployment Guide

This guide explains how to deploy the Agents CLI Monitoring agent to Google Cloud.

## Prerequisites

1. **Google Cloud Project**: Create or select a project
2. **Google Cloud SDK**: Install the gcloud CLI
   ```bash
   # See: https://cloud.google.com/sdk/docs/install
   ```
3. **Authentication**: Authenticate with Google Cloud
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

## Deployment Configuration

The deployment uses Cloud Run Jobs for scheduled batch processing:

- **Platform**: Cloud Run Jobs
- **Region**: us-central1
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Timeout**: 540 seconds (9 minutes)
- **Scheduled Runs**: Daily at 9:07 AM Pacific Time via Cloud Scheduler

## Quick Start

### One-Command Deployment

Deploy everything with a single script:

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy_job.sh
```

This automated script will:
1. Create a GCS bucket (gs://agents-cli-monitor-${PROJECT_ID})
2. Grant Storage Object Admin permissions to the default service account
3. Build and deploy the Cloud Run Job
4. Create a Cloud Scheduler job for daily runs at 9:07 AM Pacific
5. Configure all environment variables automatically

### Verify Deployment

Check the Cloud Run Job:

```bash
gcloud run jobs list --region=us-central1
```

Check the Cloud Scheduler job:

```bash
gcloud scheduler jobs list --location=us-central1
```

## Testing the Deployment

### Manual Trigger

Trigger a monitoring sweep manually:

```bash
# Via Cloud Scheduler (recommended)
gcloud scheduler jobs run agents-cli-monitor-daily --location=us-central1

# Or execute the job directly
gcloud run jobs execute agents-cli-monitor --region=us-central1
```

### View Job Status

Check recent executions:

```bash
gcloud run jobs executions list --job=agents-cli-monitor --region=us-central1
```

### View Logs

Monitor the Cloud Run Job logs:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=agents-cli-monitor" --limit=50
```

### Check Results

Download and view the tracking file:

```bash
gsutil cat gs://agents-cli-monitor-${GOOGLE_CLOUD_PROJECT}/agents_cli_mentions.md
```

## Local Testing

Before deploying, test locally:

```bash
# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set your project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Test the monitoring sweep script
uv run python run_monitoring_sweep.py

# Or test the full sweep (third-party + first-party)
uv run python run_full_monitoring_sweep.py

# View results
cat data/agents_cli_mentions.md
cat data/agents_cli_mentions_first_party.md
```

## Troubleshooting

### Build Failures

If deployment fails during build:
1. Check that all dependencies are in `pyproject.toml`
2. Verify Python version is 3.11-3.13
3. Review build logs: `gcloud builds list --limit=5`

### Permission Errors

If you get permission errors accessing GCS:
1. Ensure the default service account has Storage Object Admin role
2. The `deploy_job.sh` script grants permissions automatically, but you can also do it manually:
   ```bash
   export SERVICE_ACCOUNT=${GOOGLE_CLOUD_PROJECT}@appspot.gserviceaccount.com
   gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
     --member="serviceAccount:${SERVICE_ACCOUNT}" \
     --role="roles/storage.objectAdmin"
   ```

### Job Execution Failures

If the Cloud Run Job fails:
1. Check execution status:
   ```bash
   gcloud run jobs executions list --job=agents-cli-monitor --region=us-central1
   ```
2. View detailed logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=agents-cli-monitor" --limit=100
   ```

### Timeout Issues

If searches timeout:
- The default timeout is 540 seconds (9 minutes)
- Reduce the number of search queries in `app/tools/batch_search.py`
- Or increase timeout in `deploy_job.sh` (max 3600 seconds for Cloud Run Jobs)

## Updating the Deployment

To update after code changes:

```bash
# Simply run the deployment script again
./deploy_job.sh

# This will:
# - Build a new container image
# - Deploy the updated Cloud Run Job
# - Update the Cloud Scheduler job if needed
```

Alternatively, deploy just the job without updating the scheduler:

```bash
gcloud run jobs deploy agents-cli-monitor \
    --source . \
    --region us-central1 \
    --max-retries 1 \
    --task-timeout 540 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=True,TRACKING_FILE_PATH=gs://agents-cli-monitor-${GOOGLE_CLOUD_PROJECT}/agents_cli_mentions.md" \
    --memory 512Mi \
    --cpu 1
```

## Monitoring and Maintenance

### View Search Results

Results are saved to the GCS tracking file. Download and review:

```bash
gsutil cat gs://agents-cli-monitor-${GOOGLE_CLOUD_PROJECT}/agents_cli_mentions.md > local_results.md
```

### Adjust Schedule

To change the daily run schedule, edit `deploy_job.sh` and update the schedule:

```bash
# Change line 66 and 75:
--schedule "7 9 * * *"  # Format: minute hour day month weekday
```

Then redeploy:

```bash
./deploy_job.sh
```

## Cost Optimization

The deployment is designed to be cost-effective:

- Cloud Run Jobs charge only when executing (daily runs + manual triggers)
- No standby instances (zero cost when idle)
- Typical execution time: ~8 minutes per run
- Estimated cost: < $5/month for daily runs

## Security

- Cloud Run Jobs require authentication by default
- Uses default App Engine service account with minimal permissions
- GCS bucket is private (not publicly accessible)
- No sensitive secrets or API keys needed (uses Application Default Credentials)
- Never commit `.env` files to version control

## Architecture

The system uses Cloud Run Jobs instead of Cloud Run Services for better reliability:

- **Cloud Run Jobs**: Designed for scheduled batch processing
- **Direct Execution**: Runs `run_monitoring_sweep.py` directly (no ADK agent orchestration)
- **GCS Integration**: Reads/writes tracking file with MD5-based deduplication
- **Pattern Detection**: Three-tier confidence scoring (high: 0.5, medium: 0.3, low: 0.2)
- **Batch Search**: 41 queries targeting third-party platforms

### Why Cloud Run Jobs?

Cloud Run Jobs provide better reliability for scheduled batch processing compared to Cloud Run Services:

1. **Task-based execution**: Each run is an independent task with clear start/end
2. **Better logging**: Execution-level logs instead of request-based logs
3. **Automatic retries**: Built-in retry logic for failed tasks
4. **Resource efficiency**: No cold start delays, resources allocated only during execution
