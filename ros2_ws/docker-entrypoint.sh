#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source "/opt/ros/${ROS_DISTRO:-humble}/setup.bash"
# shellcheck disable=SC1091
source "${PHS_WS:?}/install/setup.bash"

exec "$@"
