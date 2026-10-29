#!/bin/sh
set -eu
# Core and installed packages do not need the Supervisor control credential.
unset SUPERVISOR_TOKEN HASSIO_TOKEN
export WORKSPACE_HOST_PLATFORM=home-assistant
export CORE_DATA_PATH=/data
export HOST=0.0.0.0
export PORT=3000
exec /usr/local/bin/workspace-core "$@"
