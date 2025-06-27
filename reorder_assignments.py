import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# 🔐 Load environment variables
load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
COURSE_ID = int(os.getenv("COURSE_ID"))

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


def get_paginated(url):
    """Helper to fetch all pages of a paginated Canvas API endpoint."""
    results = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        results.extend(response.json())
        url = None
        if 'Link' in response.headers:
            links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,', '>,'))            
            for link in links:
                if link.get('rel') == 'next':
                    url = link.get('url')
    return results


def get_assignment_groups(course_id):
    url = f"{API_URL}/courses/{course_id}/assignment_groups"
    return get_paginated(url)


def get_assignments(course_id, group_id):
    url = f"{API_URL}/courses/{course_id}/assignment_groups/{group_id}/assignments"
    return get_paginated(url)


def update_assignment_position(course_id, assignment_id, position):
    url = f"{API_URL}/courses/{course_id}/assignments/{assignment_id}"
    payload = {
        "assignment": {
            "position": position
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"  ✅ Set position {position} for assignment {assignment_id}")
    else:
        print(f"  ❌ Failed to update assignment {assignment_id} (status {response.status_code})")
        print("     Response:", response.text)


def choose_assignment_group(groups):
    print("\n📚 Assignment Groups:")
    for i, group in enumerate(groups):
        print(f"  {i + 1}. {group['name']} (ID: {group['id']})")

    while True:
        try:
            selection = int(input("\nEnter the number of the group to sort alphabetically: "))
            if 1 <= selection <= len(groups):
                return groups[selection - 1]
            else:
                print("❌ Invalid selection. Try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def backup_assignments(group_name, group_id, assignments):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_assignment_group_{group_id}_{timestamp}.json"
    backup_data = {
        "group_id": group_id,
        "group_name": group_name,
        "assignments": [
            {"id": a["id"], "name": a["name"]} for a in assignments
        ]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=2)
    print(f"\n📁 Backup saved to: {filename}")


def get_assignment_metadata(course_id, assignment_id, verbose=True):
    """Retrieve and display metadata for a single assignment."""
    url = f"{API_URL}/courses/{course_id}/assignments/{assignment_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch assignment {assignment_id}: {response.status_code}")
        print(response.text)
        return None

    data = response.json()

    if verbose:
        print("\n📋 Assignment Metadata:")
        print(f"  ID:               {data['id']}")
        print(f"  Name:             {data['name']}")
        print(f"  Points Possible:  {data['points_possible']}")
        print(f"  Due Date:         {data.get('due_at', 'N/A')}")
        print(f"  Unlock At:        {data.get('unlock_at', 'N/A')}")
        print(f"  Lock At:          {data.get('lock_at', 'N/A')}")
        print(f"  Submission Types: {', '.join(data.get('submission_types', []))}")
        print(f"  Grading Type:     {data.get('grading_type', 'N/A')}")
        print(f"  Published:        {'Yes' if data.get('published') else 'No'}")
        print(f"  Description:      {(data.get('description') or '').strip()[:100]}...")

    return data


def main():
    groups = get_assignment_groups(COURSE_ID)

    if not groups:
        print("❌ No assignment groups found.")
        return

    selected_group = choose_assignment_group(groups)
    group_id = selected_group["id"]
    group_name = selected_group["name"]

    print(f"\n📂 Selected Group: {group_name} (ID: {group_id})")

    assignments = get_assignments(COURSE_ID, group_id)

    if not assignments:
        print("⚠️ No assignments found in this group.")
        return

    backup_assignments(group_name, group_id, assignments)

    sorted_assignments = sorted(assignments, key=lambda a: a["name"].lower())

    print("\n🔤 Sorted Assignment Order:")
    for i, assignment in enumerate(sorted_assignments):
        print(f"  {i+1}. {assignment['name']} (ID: {assignment['id']})")

    confirm = input("\n⚠️ Proceed with reordering? (y/n): ").strip().lower()
    if confirm == "y":
    	for i, assignment in enumerate(sorted_assignments):
        	update_assignment_position(COURSE_ID, assignment["id"], i + 1)

    else: 
        print("❌ Operation cancelled.")
        for i, assignment in enumerate(sorted_assignments):
            data = get_assignment_metadata(COURSE_ID, assignment["id"], False)
            print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

