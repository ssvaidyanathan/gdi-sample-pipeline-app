#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-sample-pipeline-app}"
REGION="${REGION:-us-central1}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_NAME="${IMAGE_NAME:-gcr.io/${PROJECT_ID:-my-project}/${SERVICE_NAME}:${IMAGE_TAG}}"
MEMORY="${MEMORY:-512Mi}"
CPU="${CPU:-1}"
EXTRA_ENV_VARS="${EXTRA_ENV_VARS:-}"

echo "=================================================="
echo "Deploying ${SERVICE_NAME} to Google Cloud Run"
echo "Region:      ${REGION}"
echo "Image:       ${IMAGE_NAME}"
echo "Memory:      ${MEMORY}"
echo "=================================================="

ENV_ARGS=()
if [[ -n "${EXTRA_ENV_VARS}" ]]; then
    ENV_ARGS=("--set-env-vars" "${EXTRA_ENV_VARS}")
fi

PROJECT_ARGS=()
if [[ -n "${PROJECT_ID:-}" ]]; then
    PROJECT_ARGS=("--project" "${PROJECT_ID}")
fi

if [[ "${DRY_RUN:-false}" == "true" ]]; then
    echo "Dry-run validation successful for ${SERVICE_NAME}."
    exit 0
fi

"${GCLOUD:-gcloud}" run deploy "${SERVICE_NAME}" \
    --image="${IMAGE_NAME}" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --memory="${MEMORY}" \
    --cpu="${CPU}" \
    "${PROJECT_ARGS[@]}" \
    "${ENV_ARGS[@]}"
