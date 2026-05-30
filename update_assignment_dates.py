import csv
import os
import sys
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

def local_to_utc(date_string):

    if not date_string:
        return None

    local_dt = datetime.strptime(
        date_string,
        "%Y-%m-%d %H:%M"
    )

    local_dt = local_dt.replace(
        tzinfo=ZoneInfo(COURSE_TIMEZONE)
    )

    utc_dt = local_dt.astimezone(
        ZoneInfo("UTC")
    )

    return utc_dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

def update_assignment(
    assignment_id,
    due_at,
    unlock_at,
    lock_at
):

    payload = {
        "assignment": {}
    }

    if due_at:
        payload["assignment"]["due_at"] = due_at

    if unlock_at:
        payload["assignment"]["unlock_at"] = unlock_at

    if lock_at:
        payload["assignment"]["lock_at"] = lock_at

    url = (
        f"{API_URL}/courses/{COURSE_ID}"
        f"/assignments/{assignment_id}"
    )

    response = requests.put(
        url,
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        print(f"✅ Updated {assignment_id}")
        return True

    print(
        f"❌ Failed {assignment_id} "
        f"({response.status_code})"
    )

    print(response.text)

    return False


def main():

    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "python update_assignment_dates.py file.csv [--dry-run]"
        )
        sys.exit(1)

    csv_file = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    updates = []

    with open(
        csv_file,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            updates.append({
                "assignment_id": row["assignment_id"],
                "assignment_name": row["assignment_name"],
                "due_at": local_to_utc(row["due_at"].strip()),
                "unlock_at": local_to_utc(row["unlock_at"].strip()),
                "lock_at": local_to_utc(row["lock_at"].strip())
            })

    print("\nAssignments Found:\n")

    for item in updates:

        print(
            f"{item['assignment_name']} "
            f"(ID {item['assignment_id']})"
        )

        print(
            f"    Due At:    {item['due_at'] or '[unchanged]'}"
        )

        print(
            f"    Unlock At: {item['unlock_at'] or '[unchanged]'}"
        )

        print(
            f"    Lock At:   {item['lock_at'] or '[unchanged]'}"
        )

        print()

    if dry_run:

        print(
            "\n=============================="
            "\nDRY RUN MODE"
            "\nNo changes will be made."
            "\n=============================="
        )

        return

    confirm = input(
        "\nProceed with updates? (y/n): "
    ).lower()

    if confirm != "y":
        print("Cancelled.")
        return

    success = 0
    failed = 0

    for item in updates:

        result = update_assignment(
            item["assignment_id"],
            item["due_at"],
            item["unlock_at"],
            item["lock_at"]
        )

        if result:
            success += 1
        else:
            failed += 1

    print("\nFinished.")
    print(f"Success: {success}")
    print(f"Failed:  {failed}")

if __name__ == "__main__":
    main()
