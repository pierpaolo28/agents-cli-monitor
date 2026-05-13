# Deployment Guide

This guide explains how to deploy the Agents CLI Monitoring agent to Google Cloud.

## Prerequisites

1. **Google Cloud Project**: Create or select a project
2. **Agents CLI**: Install the CLI tool
   ```bash
   uv tool install google-agents-cli
   ```
3. **Authentication**: Authenticate with Google Cloud
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

## Deployment Configuration

The deployment is configured in `.deploy.yaml`:

- **Platform**: Cloud Run
- **Region**: us-central1
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Timeout**: 540 seconds (9 minutes)
- **Scheduled Runs**: Daily at 9:07 AM Pacific Time

## Step-by-Step Deployment

### 1. Set Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `TRACKING_FILE_PATH`: GCS path for tracking file (e.g., `gs://your-bucket/agents_cli_mentions.md`)

### 2. Create GCS Bucket

Create a Google Cloud Storage bucket for storing tracking data:

```bash
export PROJECT_ID=your-project-id
export BUCKET_NAME=agents-cli-monitor-${PROJECT_ID}

gsutil mb -p ${PROJECT_ID} -l us-central1 gs://${BUCKET_NAME}
```

Update `.env` with the bucket path:
```
TRACKING_FILE_PATH=gs://agents-cli-monitor-${PROJECT_ID}/agents_cli_mentions.md
```

### 3. Enable Required APIs

```bash
gcloud services enable run.googleapis.com --project=${PROJECT_ID}
gcloud services enable cloudscheduler.googleapis.com --project=${PROJECT_ID}
gcloud services enable cloudbuild.googleapis.com --project=${PROJECT_ID}
```

### 4. Deploy to Cloud Run

Deploy using Agents CLI:

```bash
agents-cli deploy
```

This will:
- Build a container image
- Deploy to Cloud Run
- Create a Cloud Scheduler job for daily runs
- Set up environment variables from `.deploy.yaml`

### 5. Verify Deployment

Check the Cloud Run service:

```bash
gcloud run services list --region=us-central1
```

Check the Cloud Scheduler job:

```bash
gcloud scheduler jobs list --location=us-central1
```

## Testing the Deployment

### Manual Trigger

You can manually trigger a monitoring sweep:

```bash
gcloud scheduler jobs run agents-cli-monitor-scheduler --location=us-central1
```

### View Logs

Monitor the Cloud Run logs:

```bash
gcloud run services logs read agents-cli-monitor --region=us-central1 --limit=50
```

### Check Results

Download and view the tracking file:

```bash
gsutil cat gs://${BUCKET_NAME}/agents_cli_mentions.md
```

## Local Testing

Before deploying, test locally:

```bash
# Install dependencies
agents-cli install

# Test the monitoring sweep script
uv run python run_monitoring_sweep.py

# Test the agent in playground mode
agents-cli playground
```

## Troubleshooting

### Build Failures

If deployment fails during build:
1. Check that all dependencies are in `pyproject.toml`
2. Verify Python version is 3.11-3.13
3. Review build logs: `gcloud builds list --limit=5`

### Permission Errors

If you get permission errors accessing GCS:
1. Ensure the Cloud Run service account has Storage Object Admin role
2. Grant permissions:
   ```bash
   PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='get(projectNumber)')
   gcloud projects add-iam-policy-binding ${PROJECT_ID} \
     --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

### Timeout Issues

If searches timeout:
- The default timeout is 540 seconds (9 minutes)
- Reduce the number of search queries in `app/tools/batch_search.py`
- Or increase timeout in `.deploy.yaml` (max 3600 seconds for 2nd gen Cloud Run)

## Updating the Deployment

To update after code changes:

```bash
# Deploy new version
agents-cli deploy

# Cloud Run will automatically roll out the new revision
```

## Monitoring and Maintenance

### View Search Results

Results are saved to the GCS tracking file. Download and review:

```bash
gsutil cat gs://${BUCKET_NAME}/agents_cli_mentions.md > local_results.md
```

### Adjust Schedule

To change the daily run schedule, edit `.deploy.yaml`:

```yaml
scheduler:
  schedule: "7 9 * * *"  # Format: minute hour day month weekday
  timezone: America/Los_Angeles
```

Then redeploy:

```bash
agents-cli deploy
```

## Cost Optimization

The deployment is designed to be cost-effective:

- Cloud Run charges only when invoked (daily runs + manual triggers)
- Minimum instances: 0 (no standby costs)
- Maximum instances: 1 (prevents runaway costs)
- Estimated cost: < $5/month for daily runs

## Security

- Cloud Run service requires authentication by default
- Use service accounts with minimal necessary permissions
- Store sensitive data (API keys) in Google Secret Manager if needed
- Never commit `.env` files to version control

## Infrastructure as Code

For production deployments, consider using Terraform:

```bash
agents-cli infra single-project
```

This generates Terraform configurations for:
- Cloud Run service
- Cloud Scheduler
- IAM permissions
- GCS bucket
