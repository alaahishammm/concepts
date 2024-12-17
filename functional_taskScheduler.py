from typing import List, Dict
from datetime import datetime
import json
from datetime import timedelta

def parse_and_validate_date(date_str):
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d')
        if due_date < datetime.now():
            raise ValueError("This date has already ended.")
        return date_str
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")
    
def add_task(tasks, description, due_date, priority):
    new_task = {
        'id': 0,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'completed': False,
        'nearly_overdue':False
    }
    updated_tasks = tasks + [new_task]
    sorted_tasks = sorted(updated_tasks, key=lambda t: datetime.strptime(t['due_date'], '%Y-%m-%d'))

    def assign_ids(tasks_list, idx= 0):
        if idx < len(tasks_list):
            tasks_list[idx]['id'] = idx + 1
            assign_ids(tasks_list, idx + 1)

    assign_ids(sorted_tasks)

    return sorted_tasks


def delete_task(tasks, task_id):
    if not tasks:  
        return []
    
    head, *tail = tasks  
    if head['id'] == task_id:
        return delete_task(tail, task_id)  
    else:
        return [head] + delete_task(tail, task_id) 


def filter_tasks_by_priority(tasks, priority):
    if not tasks:  
        return []
    
    head, *tail = tasks 
    if head.get('priority') == priority:
        return [head] + filter_tasks_by_priority(tail, priority)
    else:
        return filter_tasks_by_priority(tail, priority)  # Skip task and continue

def format_tasks(tasks):
    if not tasks:  # Base case: if no tasks remain
        return "No tasks available."
    
    head, *tail = tasks  # Split list into head and tail
    task_str = (
        f"ID: {head['id']}, Description: {head['description']}, "
        f"Priority: {head['priority']}, Due Date: {head['due_date']}, "
        f"Completed: {'Yes' if head['completed'] else 'No'}"
    )
    return task_str + ('\n' + format_tasks(tail) if tail else '')

def update_task_priority(tasks, task_id, new_priority):
    
    def update_task_recursively(tasks_list, index):
        if index >= len(tasks_list):  # Base case: if we've processed all tasks
            return []
        
        task = tasks_list[index]
        if task['id'] == task_id:
            updated_task = {**task, 'priority': new_priority}  # Update priority
        else:
            updated_task = task
        
        # Recursively process the rest of the list
        return [updated_task] + update_task_recursively(tasks_list, index + 1)
    
    return update_task_recursively(tasks)

    
def update_task_status(tasks):
    try:
        task_id = int(input("Enter Task ID to mark as completed: ").strip())
        
        def update_status_recursively(tasks_list, index=0):
            if index >= len(tasks_list):
                return []
            
            current_task = tasks_list[index]
            if current_task['id'] == task_id:
                updated_task = {**current_task, 'completed': True}  
                print(f"Task ID {task_id} marked as completed.")
            else:
                updated_task = current_task
            
            return [updated_task] + update_status_recursively(tasks_list, index + 1)
        
        return update_status_recursively(tasks)
    
    except ValueError:
        print("Invalid Task ID. Please enter a valid number.")
        return tasks



def get_delayed_tasks(tasks, current_time):
    if not tasks:
        return []
    
    head, *tail = tasks  
    if not head.get('completed', False) and is_date_delayed(head['due_date'], current_time):
        return [head] + get_delayed_tasks(tail, current_time)
    else:
        return get_delayed_tasks(tail, current_time)  
    

def is_date_delayed(due_date, current_time):
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return task_due_date < current_time
    except ValueError:
        return False
    

def get_tasks_nearing_deadlines(tasks, current_time, days_before_deadline= 3):
    if not tasks: 
        return []
    
    head, *tail = tasks 
    deadline_threshold = current_time + timedelta(days=days_before_deadline)
    
    if 'due_date' in head and not head.get('completed', False) and \
       is_date_nearing_deadline(head['due_date'], current_time, deadline_threshold):
        return [head] + get_tasks_nearing_deadlines(tail, current_time, days_before_deadline)
    else:
        return get_tasks_nearing_deadlines(tail, current_time, days_before_deadline)


def is_date_nearing_deadline(due_date, current_time, deadline_threshold):
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return current_time <= task_due_date <= deadline_threshold
    except ValueError:
        return False

    
    
def save_to_data(tasks):
    return json.dumps(tasks, indent=4)


def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


def load_from_data(data):
    try:
        tasks = json.loads(data)
        if not isinstance(tasks, list):
            raise ValueError("Invalid data format: not a list.")
        return tasks
    except (json.JSONDecodeError, ValueError):
        return []

# --- I/O Wrapper Functions ---
def read_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "[]"


# --- Functional Task Manager ---
def perform_add_task(tasks):
    description = input("Enter Task Description: ").strip()
    priority = input("Enter Task priority [high, low]: ").strip()
    
    while True:
        try:
            date_input = input("Enter Due Date (YYYY-MM-DD): ").strip()
            due_date = parse_and_validate_date(date_input)
            print("task added sucssesfully")
            break
        except ValueError as e:
            print(e)
    
    return add_task(tasks, description, due_date, priority)


def filter_tasks_priority(tasks):
    priority = input("Enter Priority [high, low]: ").strip()
    return filter_tasks_by_priority(tasks, priority)

def delete_task_by_id(tasks):
    try:
        task_id = int(input("Enter Task ID: ").strip())  # Convert input to integer
        updated_tasks = delete_task(tasks, task_id)  # Pass the integer ID to delete_task
        print("Task deleted successfully.")
        return updated_tasks
    except ValueError:
        print("Invalid Task ID. Please enter a number.")
        return tasks
    
def view_tasks(tasks):
    print("\n--- All Tasks ---")
    print(format_tasks(tasks))


def view_delayed_tasks(tasks):
    delayed_tasks = get_delayed_tasks(tasks, datetime.now())
    print("\n--- Delayed Tasks ---")
    print(format_tasks(delayed_tasks))


def view_tasks_nearing_deadlines(tasks):
    nearing_deadline_tasks = get_tasks_nearing_deadlines(tasks, datetime.now(), days_before_deadline=3)
    print("\n--- Tasks Nearing Deadlines ---")
    print(format_tasks(nearing_deadline_tasks))


def save_and_exit(tasks):
    save_data = save_to_data(tasks)
    write_to_file('tasks2.json', save_data)
    print("Tasks saved successfully. Exiting...")


def task_manager(tasks):
    def menu_choice() -> str:
        print("\n--- Task Manager ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. View Delayed Tasks")
        print("4. Filter Tasks by Priority")
        print("5. View Tasks Nearing Deadlines")
        print("6. delete task id")
        print("7. Mark Task as Completed")
        print("8. Save and Exit")
        
        return input("Enter your choice: ").strip()
    
    choice = menu_choice()
    
    if choice == "1":
        tasks = perform_add_task(tasks)
    elif choice == "2":
        view_tasks(tasks)
    elif choice == "3":
        view_delayed_tasks(tasks)
    elif choice == "4":
        view_tasks(filter_tasks_priority(tasks))
    elif choice == "5":
        view_tasks_nearing_deadlines(tasks)
    elif choice == "6":
        tasks = delete_task_by_id(tasks)
    elif choice == "7":
        tasks = update_task_status(tasks)
    elif choice == "8":
        save_and_exit(tasks)
        return  # Exit function
    else:
        print("Invalid choice. Please try again.")
    
    # Recursively call task_manager to continue after the action
    task_manager(tasks)


# --- Execution ---
if __name__ == "__main__":
    data = read_from_file('tasks2.json')
    tasks = load_from_data(data)
    task_manager(tasks)

