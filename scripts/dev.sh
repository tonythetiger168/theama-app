#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
cd "$(dirname "$0")/.."
exec uvicorn theama_app.server:app --reload --app-dir src "${@}"
