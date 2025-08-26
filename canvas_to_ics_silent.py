import os
import requests
import datetime
from icalendar import Calendar, Event
import argparse

# ===== Parse command-line args =====
parser = argparse.ArgumentParser(description="Export Canvas assignments to ICS")
parser.add_argument("--all-day", action="store_true", help="Make events all-day")
parser.add_argument("--future-only", action="store_true", help="Include only future assignments")
args = parser.parse_args()

all_day = args.all_day
future_only = args.future_only

# ===== Canvas Setup =====
BASE_URL = os.environ.get("CANVAS_BASE_URL")
TOKEN = os.environ.get("CANVAS_TOKEN")

if not BASE_URL or not TOKEN:
    print("ERROR: Missing CANVAS_BASE_URL or CANVAS_TOKEN environment variables.")
    exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}

# ===== Helpers =====
def get_courses():
    url = f"{BASE_URL}/api/v1/courses?enrollment_state=active"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json()

def get_assignments(course_id):
    url = f"{BASE_URL}/api/v1/courses/{course_id}/assignments"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json()

# ===== Fetch all assignments =====
all_assignments = []
courses = get_courses()
for course in courses:
    assignments = get_assignments(course['id'])
    for a in assignments:
        all_assignments.append((a, course))

if not all_assignments:
    exit(0)

# ===== Build ICS =====
cal = Calendar()
cal.add('prodid', '-//Canvas Assignments//')
cal.add('version', '2.0')
now = datetime.datetime.now().astimezone()

for a, course in all_assignments:
    title = f"{a.get('name', 'Canvas Assignment')} [{course.get('course_code', course.get('name',''))}]"
    due = a.get("due_at")
    if not due:
        continue
    due_dt = datetime.datetime.fromisoformat(due.replace("Z","+00:00")).astimezone()
    if future_only and due_dt < now:
        continue

    event = Event()
    event.add('summary', title)

    if all_day:
        event.add('dtstart', due_dt.date())
        event.add('dtend', (due_dt + datetime.timedelta(days=1)).date())
    else:
        event.add('dtstart', due_dt)
        event.add('dtend', due_dt + datetime.timedelta(hours=1))
    # YOU MUST CHANGE THE URL BELOW FOR THE CODE TO WORK
    event.add('uid', f"{a.get('id')}_{course.get('id')}@canvas.ou.edu")
    cal.add_component(event)

# ===== Export ICS =====
today_str = datetime.datetime.now().strftime("%b%d%Y")
output_dir = os.path.expanduser("~/Desktop/Canvas_Exports")
os.makedirs(output_dir, exist_ok=True)
ics_file = os.path.join(output_dir, f"CanvasEventExport.ics")
with open(ics_file, 'wb') as f:
    f.write(cal.to_ical())
