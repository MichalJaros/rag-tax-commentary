#!/usr/bin/env bash
set -e

# for WSL/Linux on AMD64
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# name of your image (build before: docker build . -t bielik_serve)
IMAGE="bielik_serve"

# directory for HuggingFace cache (models/tokenizers)
# this way downloaded artifacts survive container restarts
VOLUME="$PWD/hf_cache"

# ports: host:container
HOST_PORT=8000
CONTAINER_PORT=8000

# name your container
CONTAINER_NAME="bielik_server"

# 1) create the container only if it doesn't exist yet
create_container() {
  if ! docker ps -a --format '{{.Names}}' | grep -x "${CONTAINER_NAME}" &>/dev/null; then
    echo "Creating container ${CONTAINER_NAME}..."
    docker create \
      --gpus all \
      --name "${CONTAINER_NAME}" \
      -p "${HOST_PORT}:${CONTAINER_PORT}" \
      -v "${VOLUME}:/root/.cache/huggingface" \
      "${IMAGE}"
  fi
}

# 2) start / view logs
start() {
  create_container
  if docker ps --format '{{.Names}}' | grep -x "${CONTAINER_NAME}" &>/dev/null; then
    echo "Container is already running, restarting..."
    docker restart "${CONTAINER_NAME}"
  else
    echo "Starting container ${CONTAINER_NAME}..."
    docker start "${CONTAINER_NAME}"
  fi
  echo "Container logs (Ctrl+C to exit):"
  docker logs -f "${CONTAINER_NAME}"
}

# 3) stop
stop() {
  if docker ps --format '{{.Names}}' | grep -x "${CONTAINER_NAME}" &>/dev/null; then
    echo "Stopping container ${CONTAINER_NAME}..."
    docker stop "${CONTAINER_NAME}"
  else
    echo "Container ${CONTAINER_NAME} is not running."
  fi
}

# 4) restart = stop + start
restart() {
  stop
  start
}

# 5) status
status() {
  docker ps -a --filter "name=${CONTAINER_NAME}" --format '{{.Names}}\t{{.Status}}'
}

# 6) dispatcher
case "$1" in
  start)    start    ;;
  stop)     stop     ;;
  restart)  restart  ;;
  status)   status   ;;
  *)
    cat <<EOF
Usage: $0 {start|stop|restart|status}

  start     — create (if missing) and start the Bielik server
  stop      — stop the running container
  restart   — stop and restart
  status    — show the container status
EOF
    exit 1
    ;;
esac
