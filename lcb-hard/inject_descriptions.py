"""Inject task descriptions into codeTasks.ts"""
import json, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load task data
all_tasks = {}
for path in ["lcb_tasks_batch1.json", "lcb_tasks_batch2.json", "lcb_tasks_batch3.json"]:
    with open(path) as f:
        for t in json.load(f):
            all_tasks[t["question_title"]] = t

selected = [
    ("LCB-01", "Best Performances"),
    ("LCB-02", "Tangency of Cuboids"),
    ("LCB-03", "Art Gallery on Graph"),
    ("LCB-04", "Roulettes"),
    ("LCB-05", "Defect"),
    ("LCB-06", "Sleep Log"),
    ("LCB-07", "Complete Binary Tree"),
    ("LCB-08", "Cans and Openers"),
    ("LCB-09", "MEX"),
    ("LCB-10", "Square Permutation"),
]

# Read current codeTasks.ts
ts_path = "c:/Users/frank/Desktop/ejentum/ejentum website/packages/frontend/src/data/codeTasks.ts"
with open(ts_path, "r", encoding="utf-8") as f:
    content = f.read()

for task_id, title in selected:
    t = all_tasks[title]
    desc = t["question_content"].strip()
    # Escape for template literal
    desc = desc.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    # Find the narrative line for this task and insert taskDescription before it
    old = f"        narrative: `"
    # We need to find the specific occurrence for this task
    # Find the id line first
    id_marker = f"id: '{task_id}'"
    pos = content.find(id_marker)
    if pos == -1:
        print(f"ERROR: {task_id} not found")
        continue

    # Find the narrative line after this position
    narr_pos = content.find("        narrative: `", pos)
    if narr_pos == -1:
        print(f"ERROR: narrative not found for {task_id}")
        continue

    # Check if taskDescription already exists
    check_area = content[pos:narr_pos]
    if "taskDescription:" in check_area:
        print(f"SKIP: {task_id} already has taskDescription")
        continue

    # Insert taskDescription before narrative
    insert = f"        taskDescription: `{desc}`,\n"
    content = content[:narr_pos] + insert + content[narr_pos:]
    print(f"ADDED: {task_id} ({len(desc)} chars)")

with open(ts_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
