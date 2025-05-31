#!/usr/bin/env bash
set -e

# === CONFIGURATION ===
export DOCKER_DEFAULT_PLATFORM=linux/amd64

MODEL="ipipan/silver-retriever-base-v1"
# For Ampere GPUs (A10/A40, etc.), use tag "1.6"
IMAGE="ghcr.io/huggingface/text-embeddings-inference:1.6"
VOLUME="$PWD/embedding_model_data"
HOST_PORT=8080
CONTAINER_PORT=80
CONTAINER_NAME="embedding_server"

# === FUNCTIONS ===

# Create the container only if it doesn't already exist
create_container() {
  if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}\$"; then
    echo "Creating container ${CONTAINER_NAME}…"
    docker create \
      --gpus all \
      --name "${CONTAINER_NAME}" \
      -p "${HOST_PORT}:${CONTAINER_PORT}" \
      -v "${VOLUME}:/data" \
      --pull always \
      "${IMAGE}" \
      --model-id "${MODEL}"
  fi
}

# Start (or restart) the container and show logs
start() {
  create_container
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}\$"; then
    echo "Container is already running, restarting…"
    docker restart "${CONTAINER_NAME}"
  else
    echo "Starting container ${CONTAINER_NAME}…"
    docker start "${CONTAINER_NAME}"
  fi
  echo "Tailing logs (Ctrl+C to exit):"
  docker logs -f "${CONTAINER_NAME}"
}

# Stop the container
stop() {
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}\$"; then
    echo "Stopping container ${CONTAINER_NAME}…"
    docker stop "${CONTAINER_NAME}"
  else
    echo "Container is not running."
  fi
}

# Restart = stop + start
restart() {
  stop
  start
}

# Show container status
status() {
  if docker ps -a --format '{{.Names}}\t{{.Status}}' | grep -q "^${CONTAINER_NAME}"; then
    docker ps -a --format '  {{.Names}}\t{{.Status}}' | grep "^${CONTAINER_NAME}"
  else
    echo "Container ${CONTAINER_NAME} does not exist."
  fi
}

# === MAIN CASE ===
case "$1" in
  start)    start    ;;
  stop)     stop     ;;
  restart)  restart  ;;
  status)   status   ;;
  *)
    cat <<EOF
Usage: $0 {start|stop|restart|status}

  start     — create (if needed) and start the server
  stop      — stop the running container
  restart   — stop and then start the container
  status    — display container status
EOF
    exit 1
    ;;
esac
