from typing import List, Dict
from datetime import datetime
import json
from datetime import timedelta

tasks = []  # This will hold the list of tasks

def add_task(description, due_date, priority):
    new_task = {
        'id': 0,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'completed': False,
        'nearly_overdue': False
    }
    tasks.append(new_task)
    # Sort the tasks by due date and update the task ids
    tasks.sort(key=lambda t: datetime.strptime(t['due_date'], '%Y-%m-%d'))
    for index, task in enumerate(tasks):
        task['id'] = index + 1

# Update the priority of a task
def update_task_priority(task_id, new_priority):
    for task in tasks:
        if task['id'] == task_id:
            task['priority'] = new_priority

# Update the status of a task
def update_task_status(task_id, new_status):
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = new_status.lower() == 'completed'

def parse_and_validate_date(date_str):
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d')
        if due_date < datetime.now():
            raise ValueError("This date has already ended.")
        return date_str
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

# Filter tasks by priority 
def filter_tasks_by_priority(priority):
    return [task for task in tasks if task.get('priority') == priority]

def format_tasks(tasks):
    if not tasks:
        return "No tasks available."
    return '\n'.join(
        f"ID: {task['id']}, Description: {task['description']}, Priority: {task['priority']}, Due Date: {task['due_date']}, Completed: {'Yes' if task['completed'] else 'No'}"
        for task in tasks
    )

def get_delayed_tasks(current_time: datetime):
    return [task for task in tasks if not task.get('completed', False) and is_date_delayed(task['due_date'], current_time)]

def is_date_delayed(due_date: str, current_time: datetime) -> bool:
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return task_due_date < current_time
    except ValueError:
        return False

def get_tasks_nearing_deadlines(current_time, days_before_deadline = 3):
    deadline_threshold = current_time + timedelta(days=days_before_deadline)
    return [
        task for task in tasks
        if 'due_date' in task and not task.get('completed', False)
        and is_date_nearing_deadline(task['due_date'], current_time, deadline_threshold)
    ]

def is_date_nearing_deadline(due_date, current_time, deadline_threshold):
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return current_time <= task_due_date <= deadline_threshold
    except ValueError:
        return False

def save_to_data():
    return json.dumps(tasks, indent=4)

def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)

def load_from_data(data):
    try:
        loaded_tasks = json.loads(data)
        if not isinstance(loaded_tasks, list):
            raise ValueError("Invalid data format: not a list.")
        return loaded_tasks
    except (json.JSONDecodeError, ValueError):
        return []

def read_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "[]"

def delete_task_by_id(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    
def update_task_status_by_id(task_id, status):
    update_task_status(task_id, status)

def perform_add_task():
    description = input("Enter Task Description: ").strip()
    priority = input("Enter Task priority [high, low]: ").strip()
    while True:
        try:
            date_input = input("Enter Due Date (YYYY-MM-DD): ").strip()
            due_date = parse_and_validate_date(date_input)
            break
        except ValueError as e:
            print(e)
    add_task(description, due_date, priority)

def delete_task():
    try:
        task_id = int(input("Enter Task ID to delete: ").strip())
        delete_task_by_id(task_id)
        print(f"Task ID {task_id} has been deleted.")
    except ValueError:
        print("Invalid Task ID. Please enter a number.")

def update_task_status():
    try:
        task_id = int(input("Enter Task ID to update: ").strip())
        new_status = input("Enter new status (completed/not completed): ").strip()
        update_task_status_by_id(task_id, new_status)
        print(f"Task ID {task_id} has been updated to {new_status}.")
    except ValueError:
        print("Invalid Task ID. Please enter a number.")

def view_tasks():
    print("\n--- All Tasks ---")
    print(format_tasks(tasks))

def view_delayed_tasks():
    delayed_tasks = get_delayed_tasks(datetime.now())
    print("\n--- Delayed Tasks ---")
    print(format_tasks(delayed_tasks))

def view_tasks_nearing_deadlines():
    nearing_deadline_tasks = get_tasks_nearing_deadlines(datetime.now(), days_before_deadline=3)
    print("\n--- Tasks Nearing Deadlines ---")
    print(format_tasks(nearing_deadline_tasks))

def save_and_exit():
    save_data = save_to_data()
    write_to_file('tasks2.json', save_data)
    print("Tasks saved successfully. Exiting...")

# --- Main App ---
def task_manager():
    global tasks  # Use global variable tasks

    while True:
        print("\n--- Task Manager ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. View Delayed Tasks")
        print("4. Filter Tasks by Priority")
        print("5. View Tasks Nearing Deadlines")
        print("6. Delete Task by ID")
        print("7. Update Task Status by ID")
        print("8. Save and Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            perform_add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            view_delayed_tasks()
        elif choice == "4":
            filter_priority = input("Enter Priority [high, low]: ").strip()
            print(format_tasks(filter_tasks_by_priority(filter_priority)))
        elif choice == "5":
            view_tasks_nearing_deadlines()
        elif choice == "6":
            delete_task()
        elif choice == "7":
            update_task_status()
        elif choice == "8":
            save_and_exit()
            return  # Exit function
        else:
            print("Invalid choice. Please try again.")

# --- Execution ---
if __name__ == "__main__":
    data = read_from_file('tasks2.json')
    tasks = load_from_data(data)
    task_manager()
