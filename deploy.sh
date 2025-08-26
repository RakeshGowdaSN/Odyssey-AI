#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# -----------------------------------------------------------------------------
# Configuration - Adjust these variables as needed
# -----------------------------------------------------------------------------
PROJECT_ID="pitchhubsmes"
REGION="us-central1"

# Name for your Cloud Run service AND the image name in Artifact Registry
CLOUD_RUN_SERVICE_NAME="dreamscape-engine"

# Name of your Artifact Registry repository
ARTIFACT_REGISTRY_REPO_NAME="dreamscape-engine"

# Name of the local Docker image you build (e.g., with 'docker build -t ...')
LOCAL_DOCKER_IMAGE_NAME="dreamscape-engine" # This is what you used in 'docker build -t travel-ai-backend .'

# Directory containing your Dockerfile and application source for the build context
# Since deploy.sh is IN the app/ directory, the build context is the current directory ('.')
DOCKERFILE_DIR="."

# The port your application listens on inside the Docker container
CONTAINER_PORT=8000

# Full URI for the image in Artifact Registry
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO_NAME}/${CLOUD_RUN_SERVICE_NAME}:latest"

# -----------------------------------------------------------------------------
# Optional: Authenticate gcloud CLI (uncomment if needed)
# -----------------------------------------------------------------------------
# echo "Ensure you are logged into gcloud and the correct project is set."
# echo "Current gcloud project: $(gcloud config get-value project)"
# echo "If this is not $PROJECT_ID, run: gcloud config set project $PROJECT_ID"
# To login (if not already): gcloud auth login

# -----------------------------------------------------------------------------
# 1. Configure Docker for Artifact Registry
# -----------------------------------------------------------------------------
echo ""
echo "STEP 1: Configuring Docker authentication for Artifact Registry (${REGION})..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
echo "Docker configured."

# -----------------------------------------------------------------------------
# 2. Check for and create Artifact Registry repository if it doesn't exist
# -----------------------------------------------------------------------------
echo ""
echo "STEP 2: Checking if Artifact Registry repository '$ARTIFACT_REGISTRY_REPO_NAME' exists..."
if ! gcloud artifacts repositories describe "$ARTIFACT_REGISTRY_REPO_NAME" --location="$REGION" --project="$PROJECT_ID" > /dev/null 2>&1; then
  echo "Repository '$ARTIFACT_REGISTRY_REPO_NAME' not found. Creating it now..."
  gcloud artifacts repositories create "$ARTIFACT_REGISTRY_REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Docker repository for $CLOUD_RUN_SERVICE_NAME (created by deploy.sh)" \
    --project="$PROJECT_ID" --quiet
  echo "Repository '$ARTIFACT_REGISTRY_REPO_NAME' created successfully."
else
  echo "Repository '$ARTIFACT_REGISTRY_REPO_NAME' already exists."
fi

# -----------------------------------------------------------------------------
# 3. Build the Docker image
# -----------------------------------------------------------------------------
echo ""
echo "STEP 3: Building Docker image '$LOCAL_DOCKER_IMAGE_NAME' from context '$DOCKERFILE_DIR'..."
# The -t flag names the image LOCALLY. The Dockerfile itself is expected to be in $DOCKERFILE_DIR (which is '.')
docker build -t "$LOCAL_DOCKER_IMAGE_NAME" "$DOCKERFILE_DIR"
echo "Docker image '$LOCAL_DOCKER_IMAGE_NAME' built successfully."

# -----------------------------------------------------------------------------
# 4. Tag the Docker image for Artifact Registry
# -----------------------------------------------------------------------------
echo ""
echo "STEP 4: Tagging Docker image '$LOCAL_DOCKER_IMAGE_NAME' as '$IMAGE_URI'..."
docker tag "$LOCAL_DOCKER_IMAGE_NAME" "$IMAGE_URI"
echo "Image tagged."

# -----------------------------------------------------------------------------
# 5. Push the Docker image to Artifact Registry
# -----------------------------------------------------------------------------
echo ""
echo "STEP 5: Pushing Docker image to Artifact Registry: '$IMAGE_URI'..."
docker push "$IMAGE_URI"
echo "Docker image pushed successfully."

# -----------------------------------------------------------------------------
# 6. Deploy the service to Cloud Run
# -----------------------------------------------------------------------------
echo ""
echo "STEP 6: Deploying to Cloud Run service '$CLOUD_RUN_SERVICE_NAME' from image '$IMAGE_URI'..."
echo "         Container will listen on port: $CONTAINER_PORT"
echo ""
echo "IMPORTANT NOTE ON ENVIRONMENT VARIABLES FOR CLOUD RUN:"
echo "This script currently relies on the .env file being bundled into your Docker image"
echo "via 'python-dotenv'. For production, it's STRONGLY recommended to manage"
echo "secrets and configurations using Cloud Run's built-in environment variable settings"
echo "or by integrating with Google Secret Manager, rather than embedding them in the image."
echo "You can set environment variables during deployment using the --set-env-vars flag"
echo "or by updating the service revision later. For example:"
echo "gcloud run deploy \"$CLOUD_RUN_SERVICE_NAME\" \\"
echo "    --image \"$IMAGE_URI\" \\"
echo "    --set-env-vars \"GOOGLE_API_KEY=YOUR_KEY_HERE,FIRESTORE_PROJECT=$PROJECT_ID\" \\"
echo "    # ... other flags"
echo ""

gcloud run deploy "$CLOUD_RUN_SERVICE_NAME" \
    --image "$IMAGE_URI" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --port "${CONTAINER_PORT}" \
    --allow-unauthenticated \
    --quiet # Use --no-quiet to see more detailed deployment progress

echo ""
echo "Cloud Run deployment command executed for '$CLOUD_RUN_SERVICE_NAME'."
echo "Service URL will be available once the revision is ready."
echo "You can check the status in the Google Cloud Console or by running:"
echo "gcloud run services describe \"$CLOUD_RUN_SERVICE_NAME\" --region \"$REGION\" --project \"$PROJECT_ID\" --format 'value(status.url)'"
echo ""
echo "Deployment script finished."
