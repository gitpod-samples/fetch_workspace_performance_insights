import requests
import json
import os
import time

# Load and validate required environment variables
auth_token = os.getenv("API_TOKEN")
if not auth_token:
    raise EnvironmentError("Missing required environment variable: API_TOKEN")

host = os.getenv("API_HOST")
if not host:
    raise EnvironmentError("Missing required environment variable: API_HOST")

organization_id = os.getenv("ORG_ID")
if not organization_id:
    raise EnvironmentError("Missing required environment variable: ORG_ID")

# Optional environment variables with defaults
from_date = os.getenv("FROM_DATE", "2025-04-01")
from_date = f"{from_date}T00:00:00.000Z"
page_size = 1
rate_limit_delay = 0.35  # seconds between requests
endpoint = f"https://api.{host}/gitpod.v1.WorkspaceService/ListWorkspaceSessions"

# HTTP Headers
headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

# Aggregated results
all_workspace_sessions = []

# Start paging
page = 0
while True:
    payload = {
        "organizationId": organization_id,
        "pagination": {
            "page": page,
            "pageSize": page_size
        },
        "from": from_date
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)

        # Check if it's a "user deleted" style error
        if response.status_code == 404:
            try:
                error_data = response.json()
                if (
                    error_data.get("code") == "not_found"
                    and "user deleted" in error_data.get("message", "").lower()
                ):
                    print(f"Page {page}: Skipped due to deleted user.")
                    page += 1
                    time.sleep(rate_limit_delay)
                    continue
            except Exception:
                pass  # fallback to regular error handling if parsing fails

        response.raise_for_status()
        data = response.json()

        if not data or "workspaceSessions" not in data or not data["workspaceSessions"]:
            print(f"No more data on page {page}. Ending pagination.")
            break

        all_workspace_sessions.extend(data["workspaceSessions"])
        session_ids = [s["id"] for s in data["workspaceSessions"]]
        print(f"Page {page}: Retrieved {len(session_ids)} session(s): {session_ids}")
        page += 1
        time.sleep(rate_limit_delay)

    except requests.RequestException as e:
        print(f"Request failed on page {page}: {e}")
        break

# Save to file
with open("all_workspace_sessions.json", "w") as f:
    json.dump(all_workspace_sessions, f, indent=2)

print(f"Total sessions collected: {len(all_workspace_sessions)}")
