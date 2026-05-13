#!/bin/bash
# Deploy Agents CLI Monitor as Cloud Run Job with Cloud Scheduler

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="us-central1"
JOB_NAME="agents-cli-monitor"
SCHEDULER_NAME="agents-cli-monitor-daily"
BUCKET_NAME="agents-cli-monitor-${PROJECT_ID}"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

echo "=================================================="
echo "Deploying Agents CLI Monitor"
echo "=================================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Job: ${JOB_NAME}"
echo "Bucket: gs://${BUCKET_NAME}"
echo "=================================================="
echo ""

# Step 1: Create GCS bucket if it doesn't exist
echo "Step 1: Setting up GCS bucket..."
if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    echo "  Creating bucket gs://${BUCKET_NAME}..."
    gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}
    echo "  ✓ Bucket created"
else
    echo "  ✓ Bucket already exists"
fi
echo ""

# Step 2: Grant Storage permissions to default service account
echo "Step 2: Granting permissions..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.objectAdmin" \
    --condition=None \
    >/dev/null 2>&1 || echo "  (permissions may already exist)"
echo "  ✓ Permissions granted"
echo ""

# Step 3: Build and deploy Cloud Run Job
echo "Step 3: Building and deploying Cloud Run Job..."
gcloud run jobs deploy ${JOB_NAME} \
    --source . \
    --region ${REGION} \
    --max-retries 1 \
    --task-timeout 540 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=True,TRACKING_FILE_PATH=gs://${BUCKET_NAME}/agents_cli_mentions.md" \
    --memory 512Mi \
    --cpu 1
echo "  ✓ Cloud Run Job deployed"
echo ""

# Step 4: Create or update Cloud Scheduler job
echo "Step 4: Setting up Cloud Scheduler..."

# Check if scheduler exists
if gcloud scheduler jobs describe ${SCHEDULER_NAME} --location=${REGION} &>/dev/null; then
    echo "  Updating existing scheduler job..."
    gcloud scheduler jobs update http ${SCHEDULER_NAME} \
        --location ${REGION} \
        --schedule "7 9 * * *" \
        --time-zone "America/Los_Angeles" \
        --uri "https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
        --http-method POST \
        --oauth-service-account-email ${SERVICE_ACCOUNT}
else
    echo "  Creating new scheduler job..."
    gcloud scheduler jobs create http ${SCHEDULER_NAME} \
        --location ${REGION} \
        --schedule "7 9 * * *" \
        --time-zone "America/Los_Angeles" \
        --description "Daily Agents CLI monitoring sweep" \
        --uri "https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
        --http-method POST \
        --oauth-service-account-email ${SERVICE_ACCOUNT}
fi
echo "  ✓ Cloud Scheduler configured"
echo ""

# Summary
echo "=================================================="
echo "Deployment Complete!"
echo "=================================================="
echo ""
echo "Cloud Run Job: ${JOB_NAME}"
echo "Schedule: Daily at 9:07 AM Pacific Time"
echo "Tracking file: gs://${BUCKET_NAME}/agents_cli_mentions.md"
echo ""
echo "Manual trigger:"
echo "  gcloud scheduler jobs run ${SCHEDULER_NAME} --location=${REGION}"
echo ""
echo "View job executions:"
echo "  gcloud run jobs executions list --job=${JOB_NAME} --region=${REGION}"
echo ""
echo "View logs:"
echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=${JOB_NAME}\" --limit=50"
echo ""
echo "View tracking file:"
echo "  gsutil cat gs://${BUCKET_NAME}/agents_cli_mentions.md"
echo "=================================================="
