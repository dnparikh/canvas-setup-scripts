# Canvas API Automation Toolkit

A collection of Python scripts for automating Canvas LMS tasks via the Canvas REST API. These tools streamline content management and backup for instructors and instructional technologists.

---

## Included Scripts

| Script Name                | Purpose |
|---------------------------|---------|
| `reorder_assignments.py`  | Sort and reorder assignments alphabetically in a selected assignment group |
| `merge_pages.py`          | Merge all Canvas course wiki pages into a single HTML backup |
| `restore_pages.py`        | Restore individual wiki pages from a merged HTML file |
| `get_panoptolinks.py`        | Get the Viewer URL for the Panopto Videos in a given Panopto Folder|

---

## Setup and Installation

### 1. Install Dependencies

Make sure you have Python 3.7+ installed, then run:

```bash
pip install requests python-dotenv beautifulsoup4 python-slugify
pip install requests oauthlib requests_oauthlib
```

### 2. Get Canvas Access Tokens

Get it from Canvas via Account → Settings → New Access Token.

### 3. Setup API Client on Panopto server
-  Sign in to the Panopto web site
- Click the System icon at the left-bottom corner.
- Click API Clients
- Click New
- Enter arbitrary Client Name
- Select Server-side Web Application type.
- Enter ```https://localhost``` into CORS Origin URL.
- Enter ```http://localhost:9127/redirect``` into Redirect URL.
- The rest can be blank. Click "Create API Client" button.
- Note the created Client ID and Client Secret.

### 4. Create a .env File

Place a .env file in the same folder as your scripts:

```
CANVAS_API_URL=https://yourinstitution.instructure.com/api/v1
CANVAS_ACCESS_TOKEN=your_canvas_api_token
COURSE_ID=123456

PANOPTO_API_URL=yourinstitution.hosted.panopto.com
PANOPTO_CLIENT_ID=panopto_client_id
PANOPTO_CLIENT_SECRET=client_secret
```
 -   CANVAS_API_URL: Your Canvas domain with the /api/v1 path.

 -   CANVAS_ACCESS_TOKEN: Obtained from Step 2.

 -   COURSE_ID: The Canvas internal course number (found in the course URL).

 - PANOPTO_API_URL: Panopto Server Name
 - PANOPTO_CLIENT_ID: Obtained from Step 3.
 - PANOPTO_CLIENT_SECRET: Obtained from Step 3.


## Usage Examples

### 1. Reorder Assignments Alphabetically

This script will:

- List all assignment groups in the course

- Prompt you to select one group

- Backup the current assignment order to a JSON file

- Sort assignments alphabetically by name

- Reorder them using the Canvas position field

Run it:

```
python reorder_assignments.py
```


Sample Output:

```
📚 Assignment Groups:
  1. Homework (ID: 123)
  2. Labs (ID: 124)

Enter the number of the group to sort alphabetically: 1

📂 Selected Group: Homework (ID: 123)
🔤 Sorted Assignment Order:
  1. HW 01
  2. HW 02
  3. HW 03
📁 Backup saved to: backup_assignment_group_123_20250624_143011.json
```

### 2. Merge All Wiki Pages into One File

This script:

- Retrieves all wiki pages from the Canvas course

- Follows pagination to get everything

- Saves them into a single HTML file (includes full page content)

Run it:
```
python merge_pages.py
```
Sample Output:
```
🔍 Retrieving Canvas pages...
📄 Fetching: Welcome
📄 Fetching: Syllabus
📄 Fetching: Week 1 Overview
✅ Merged HTML saved to: merged_canvas_pages_20250624_153002.html
```

### 3. Restore Canvas Pages from Merged HTML

This script:

- Accepts a merged HTML file from merge_pages.py

- Parses the file and splits pages using `<h1>` tags

- Recreates each page in Canvas, preserving title and content

- Updates existing pages or creates new ones as needed

Run it:

```
python restore_pages.py
```

Sample Output:
```
Enter the path to the merged HTML file: merged_canvas_pages_20250624_153002.html
🔍 Splitting merged HTML...
🔧 Restoring 3 page(s)...
🆕 Created: Welcome
🆕 Created: Syllabus
🆕 Created: Week 1 Overview
```

### 4. Get the Viewer URL for the Panopto Videos in a given Panopto Folder 

This script will list the Viewer URLs of all the vidoes in the folder that is identified by folder_id.

The script brings up the sign-in screen on the browser for the first time. Go through the sign in process.
This application saves OAuth2 refresh token in a *.cache file, so later runs of this application do not require signing in.

This script displays the list of folders that are accessible by the user who signed in at the sign-in screen.
When this runs for more than an hour, which is the token expiration, it goes through the authorization again and retries.

```
python3 get_panoptolinks.py --folder <folder_id>
```
Sample Output:

```
ccfd10f3-5bf5-45fe-a769-b30700790167: 01.01.00 Building Blocks of Boolean Logic https://utexas.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=ccfd10f3-5bf5-45fe-a769-b30700790167
125b3c1b-534a-459d-8e10-b3070079019a: 01.01.01 Logical Operators https://utexas.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=125b3c1b-534a-459d-8e10-b3070079019a
43aeded6-471b-4199-92f7-b30700790221: 01.01.02 Truth Tables https://utexas.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=43aeded6-471b-4199-92f7-b30700790221
```

### 5. Export Assignment Dates to CSV

This script will:

- List all assignment groups in the course

- Prompt you to select one group

- Export all assignments in the selected group to a CSV file

- Convert Canvas UTC timestamps to your configured course timezone

- Generate a spreadsheet that can be edited in Excel, LibreOffice, or Google Sheets

- Include assignment IDs required for updating assignments later

Run it:

```bash
python export_assignments.py
```

Sample Output:

```text
Assignment Groups:

1. Homework
2. Labs
3. Quizzes

Select group: 1

CSV exported to:
assignments_12345_20260530_142500.csv
```

Sample CSV:

```csv
assignment_id,assignment_name,due_at,unlock_at,lock_at
10001,Homework 1,2026-09-01 23:59,2026-08-25 00:00,2026-09-08 23:59
10002,Homework 2,2026-09-08 23:59,2026-09-01 00:00,2026-09-15 23:59
10003,Homework 3,2026-09-15 23:59,2026-09-08 00:00,2026-09-22 23:59
```

The exported dates are displayed in the timezone specified by:

```text
COURSE_TIMEZONE
```

from your `.env` file.

---

### 6. Update Assignment Dates from CSV

This script will:

- Read assignment information from a CSV file

- Convert local course times to Canvas UTC timestamps

- Update Due Dates (`due_at`)

- Update Available From dates (`unlock_at`)

- Update Until dates (`lock_at`)

- Prompt for confirmation before making any changes

- Display success and failure counts after processing

Run it:

```bash
python update_assignment_dates.py assignments.csv
```

Sample Output:

```text
Assignments to update:

Homework 1 (ID 10001)
Homework 2 (ID 10002)
Homework 3 (ID 10003)

Proceed with updates? (y/n): y

✅ Updated 10001
✅ Updated 10002
✅ Updated 10003

Finished.
Success: 3
Failed:  0
```

---

## 4. Dry Run Mode

Before making changes to Canvas, you can preview all updates using dry-run mode.

This mode:

- Reads the CSV file

- Performs timezone conversion

- Displays all assignment updates

- Does not make any Canvas API calls

- Allows verification before modifying a live course

Run it:

```bash
python update_assignment_dates.py assignments.csv --dry-run
```

Sample Output:

```text
Assignments Found:

Homework 1 (ID 10001)
    Due At:    2026-09-01 23:59
    Unlock At: 2026-08-25 00:00
    Lock At:   2026-09-08 23:59

Homework 2 (ID 10002)
    Due At:    2026-09-08 23:59
    Unlock At: 2026-09-01 00:00
    Lock At:   2026-09-15 23:59

==============================
DRY RUN MODE
No changes will be made.
==============================
```

---

## Timezone Configuration

Assignment dates in the CSV should be entered using the course's local timezone.

Example `.env` configuration:

```text
COURSE_TIMEZONE=America/Chicago
```

Supported examples:

```text
COURSE_TIMEZONE=America/New_York
COURSE_TIMEZONE=America/Chicago
COURSE_TIMEZONE=America/Denver
COURSE_TIMEZONE=America/Los_Angeles
COURSE_TIMEZONE=UTC
```

CSV dates should use the format:

```text
YYYY-MM-DD HH:MM
```

Example:

```text
2026-09-01 23:59
```

The script automatically converts these values to the UTC format required by Canvas before sending updates through the API.




## Best Practices & Warnings

- 💾 Always back up your Canvas content before running scripts that make changes.

- 🧪 Test assignment reordering in a sandbox course — it uses an undocumented API trick.

- 🔄 You can rerun restore_pages.py to update page content as needed.

- 🧼 If restoring from HTML, make sure the file is structured with clean `<h1>` tags separating each page.

## Disclaimer

`reorder_assignments.py`, `merge_pages.py` and `restore_pages.py`   scripts were created with assistance from ChatGPT using OpenAI's GPT-4 model. Please review and test thoroughly before using in production environments.

 `get_panoptolinks.py` has been taken from https://github.com/Panopto/panopto-api-python-examples/tree/master/auth-server-side-web-app.

