#!/bin/bash

CONTAINER_NAME="browser"
IMAGE="docker.io/chromedp/headless-shell"
PORT=9222
WINDOW_SIZE="1280,720"

# Check if container is already running
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Container '${CONTAINER_NAME}' already exists. Restarting..."
    docker rm -f "${CONTAINER_NAME}"
fi

# Run the container
echo "Starting container '${CONTAINER_NAME}'..."
docker run -d \
    -p ${PORT}:9222 \
    --name "${CONTAINER_NAME}" \
    ${IMAGE} \
    --window-size=${WINDOW_SIZE} \
    --remote-debugging-port=9222 \
    --disable-gpu \
    --no-sandbox

echo "Headless browser running on port ${PORT} with window size ${WINDOW_SIZE}."
