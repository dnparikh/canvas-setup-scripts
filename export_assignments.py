import csv
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
COURSE_ID = int(os.getenv("COURSE_ID"))

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

COURSE_TIMEZONE = os.getenv(
    "COURSE_TIMEZONE",
    "America/Chicago"
)

def utc_to_local(canvas_date):

    if not canvas_date:
        return ""

    utc_dt = datetime.fromisoformat(
        canvas_date.replace("Z", "+00:00")
    )

    local_dt = utc_dt.astimezone(
        ZoneInfo(COURSE_TIMEZONE)
    )

    return local_dt.strftime(
        "%Y-%m-%d %H:%M"
    )

def get_paginated(url):
    results = []

    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        results.extend(response.json())

        url = None

        if "Link" in response.headers:
            links = requests.utils.parse_header_links(
                response.headers["Link"].rstrip(">").replace(">,", ">,")
            )

            for link in links:
                if link.get("rel") == "next":
                    url = link.get("url")

    return results


def get_assignment_groups():
    url = f"{API_URL}/courses/{COURSE_ID}/assignment_groups"
    return get_paginated(url)


def get_assignments(group_id):
    url = (
        f"{API_URL}/courses/{COURSE_ID}"
        f"/assignment_groups/{group_id}/assignments"
    )
    return get_paginated(url)


def choose_group(groups):
    print("\nAssignment Groups:\n")

    for i, group in enumerate(groups):
        print(f"{i+1}. {group['name']}")

    while True:
        try:
            selection = int(input("\nSelect group: "))
            if 1 <= selection <= len(groups):
                return groups[selection - 1]
        except ValueError:
            pass

        print("Invalid selection.")


def export_csv(group, assignments):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"assignments_{group['id']}_{timestamp}.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "assignment_id",
            "assignment_name",
            "due_at",
            "unlock_at",
            "lock_at"
        ])

        for assignment in assignments:
            writer.writerow([
                assignment["id"],
                assignment["name"],
                utc_to_local(assignment.get("due_at", "")),
                utc_to_local(assignment.get("unlock_at", "")),
                utc_to_local(assignment.get("lock_at", ""))
            ])

    print(f"\nCSV exported to: {filename}")


def main():

    groups = get_assignment_groups()

    group = choose_group(groups)

    assignments = get_assignments(group["id"])

    export_csv(group, assignments)


if __name__ == "__main__":
    main()
