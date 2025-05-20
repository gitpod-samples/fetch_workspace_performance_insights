#!/usr/bin/env bash

read -p ">> Enter your Gitpod access token: " token
read -ei '2025-04-01' -p ">> Enter the from date to collect data until: " from_date
read -ei 'gitpod.io' -p ">> Enter your Gitpod host domain: " host
read -p ">> Enter your organization ID: " orgid

API_TOKEN="$token" FROM_DATE="$from_date" API_HOST="$host" ORG_ID="$orgid" python3 fetch_workspace_sessions.py 