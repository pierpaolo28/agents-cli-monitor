#!/bin/bash
# Manually trigger the monitoring sweep on Cloud Run

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Trigger Agents CLI Monitoring Sweep"
echo "========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No Google Cloud project selected${NC}"
    echo "Run: gcloud config set project PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}Using project: ${PROJECT_ID}${NC}"
echo ""

# Method 1: Trigger via Cloud Scheduler (recommended)
echo "Method 1: Trigger via Cloud Scheduler"
echo "--------------------------------------"
echo "Attempting to trigger Cloud Scheduler job..."

if gcloud scheduler jobs run agents-cli-monitor-scheduler --location=us-central1 2>/dev/null; then
    echo -e "${GREEN}✓ Scheduler job triggered successfully${NC}"
    echo ""
    echo "The monitoring sweep will run in the background."
    echo "Check logs with:"
    echo "  gcloud run services logs read agents-cli-monitor --region=us-central1 --limit=50"
    exit 0
else
    echo -e "${YELLOW}⚠ Cloud Scheduler job not found or failed to trigger${NC}"
    echo ""
fi

# Method 2: Direct Cloud Run invocation (fallback)
echo "Method 2: Direct Cloud Run Invocation"
echo "--------------------------------------"

# Get Cloud Run service URL
SERVICE_URL=$(gcloud run services describe agents-cli-monitor \
    --region=us-central1 \
    --format='value(status.url)' 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Error: Cloud Run service 'agents-cli-monitor' not found${NC}"
    echo "Deploy first with: agents-cli deploy"
    exit 1
fi

echo "Service URL: $SERVICE_URL"
echo ""

# Get authentication token
echo "Getting authentication token..."
TOKEN=$(gcloud auth print-identity-token)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Error: Failed to get authentication token${NC}"
    exit 1
fi

# Trigger the service
echo "Triggering monitoring sweep..."
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$SERVICE_URL" \
    --max-time 600)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo ""
echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Sweep completed successfully${NC}"
    echo ""
    echo "Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" -eq 307 ] || [ "$HTTP_CODE" -eq 302 ]; then
    echo -e "${YELLOW}⚠ Service returned a redirect${NC}"
    echo "This may be normal for ADK deployments."
    echo "Check logs to verify execution:"
    echo "  gcloud run services logs read agents-cli-monitor --region=us-central1 --limit=50"
else
    echo -e "${RED}✗ Request failed${NC}"
    echo "Response body:"
    echo "$BODY"
fi

echo ""
echo "========================================="
