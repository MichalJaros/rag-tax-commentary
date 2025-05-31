#!/usr/bin/env bash
set -e

# === CONFIGURATION ===
export DOCKER_DEFAULT_PLATFORM=linux/amd64
IMAGE="cr.weaviate.io/semitechnologies/weaviate:1.30.0"
VOLUME="$PWD/vector_db_data"
HOST_PORT_HTTP=8081
HOST_PORT_GRPC=50051
CONTAINER_NAME="weaviate_server"

# === CREATE CONTAINER (only once) ===
create_container() {
  if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}\$"; then
    echo "Creating container ${CONTAINER_NAME}…"
    docker create \
      --name "${CONTAINER_NAME}" \
      -p "${HOST_PORT_HTTP}:8080" \
      -p "${HOST_PORT_GRPC}:50051" \
      -v "${VOLUME}:/data" \
      -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
      -e QUERY_DEFAULTS_LIMIT=20 \
      -e PERSISTENCE_DATA_PATH="/data" \
      -e DEFAULT_VECTORIZER_MODULE="none" \
      -e SINGLE_NODE="true" \
      --pull always \
      "${IMAGE}"
  fi
}

# === START / STOP / STATUS ===
start() {
  create_container
  echo "Starting container ${CONTAINER_NAME}…"
  docker start "${CONTAINER_NAME}"
  echo "Tailing logs (Ctrl+C to exit):"
  docker logs -f "${CONTAINER_NAME}"
}

stop() {
  echo "Stopping container ${CONTAINER_NAME}…"
  docker stop "${CONTAINER_NAME}" || echo "Container was not running."
}

status() {
  docker ps -a --filter "name=${CONTAINER_NAME}" --format '  {{.Names}}\t{{.Status}}'
}

case "$1" in
  start)   start   ;;
  stop)    stop    ;;
  status)  status  ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
