from typing import List, Dict
from datetime import datetime
import json
from datetime import timedelta

# --- Pure Utility Functions ---
def parse_and_validate_date(date_str: str) -> str:
    """Validate and return a valid date string."""
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d')
        if due_date < datetime.now():
            raise ValueError("This date has already ended.")
        return date_str
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")
    

def add_task(tasks: List[Dict], description: str, due_date: str, priority: str) -> List[Dict]:
    """Add a new task and return a new sorted task list."""
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
    for index, task in enumerate(sorted_tasks):
        task['id'] = index + 1
    return sorted_tasks


def delete_task(tasks: List[Dict], task_id: int) -> List[Dict]:
    """Return a new list with the task removed, without mutating the original tasks."""
    return [task for task in tasks if task['id'] != task_id]


def filter_tasks_by_priority(tasks: List[Dict], priority: str) -> List[Dict]:
    """Filter tasks by priority level."""
    return [task for task in tasks if task.get('priority') == priority]


def format_tasks(tasks: List[Dict]) -> str:
    """Format tasks as a string."""
    if not tasks:
        return "No tasks available."
    return '\n'.join(
        f"ID: {task['id']}, Description: {task['description']}, Priority: {task['priority']}, Due Date: {task['due_date']}, Completed: {'Yes' if task['completed'] else 'No'},"
        for task in tasks
    )


def update_task_priority(tasks: List[Dict], task_id: int, new_priority: str) -> List[Dict]:
    """Update the priority of a task and return the new list of tasks."""

    return [
        {**task, 'priority': new_priority} if task['id'] == task_id else task 
        for task in tasks   
    ]


    
def  update_task_status(tasks: List[Dict]) -> List[Dict]:
    """Handles marking a task as completed."""
    try:
        task_id = int(input("Enter Task ID to mark as completed: ").strip())
        updated_tasks = [
            {**task, 'completed': True} if task['id'] == task_id else task
            for task in tasks
        ]
        print(f"Task ID {task_id} marked as completed.")
        return updated_tasks
    except ValueError:
        print("Invalid Task ID. Please enter a valid number.")
        return tasks




def get_delayed_tasks(tasks: List[Dict], current_time: datetime) -> List[Dict]:
    """Return a list of delayed tasks."""
    return [
        task for task in tasks
        if not task.get('completed', False) and is_date_delayed(task['due_date'], current_time)
    ]
    

def is_date_delayed(due_date: str, current_time: datetime) -> bool:
    """Check if a task's due date is in the past."""
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return task_due_date < current_time
    except ValueError:
        return False
    


def get_tasks_nearing_deadlines(tasks: List[Dict], current_time: datetime, days_before_deadline: int = 3) -> List[Dict]:
    """Return a list of tasks that are nearing their deadlines (within a certain number of days)."""
    deadline_threshold = current_time + timedelta(days=days_before_deadline)
    
    # Filter tasks that are nearing their deadline
    nearing_deadline_tasks = [
        task for task in tasks
        if 'due_date' in task and not task.get('completed', False)  # Task is not completed
        and is_date_nearing_deadline(task['due_date'], current_time, deadline_threshold)  # Task due date is nearing
    ]
    
    return nearing_deadline_tasks

def is_date_nearing_deadline(due_date: str, current_time: datetime, deadline_threshold: datetime) -> bool:
    """Check if a task's due date is nearing its deadline."""
    try:
        task_due_date = datetime.strptime(due_date, '%Y-%m-%d')
        # Check if the task's due date is within the threshold
        return current_time <= task_due_date <= deadline_threshold
    except ValueError:
        return False

    
    
    
    
    

def save_to_data(tasks: List[Dict]) -> str:
    """Serialize tasks to JSON."""
    return json.dumps(tasks, indent=4)


def write_to_file(filename: str, data: str) -> None:
    """Write raw data to a file."""
    with open(filename, 'w') as f:
        f.write(data)


def load_from_data(data: str) -> List[Dict]:
    """Deserialize tasks from JSON."""
    try:
        tasks = json.loads(data)
        if not isinstance(tasks, list):
            raise ValueError("Invalid data format: not a list.")
        return tasks
    except (json.JSONDecodeError, ValueError):
        return []

# --- I/O Wrapper Functions ---
def read_from_file(filename: str) -> str:
    """Read raw data from a file."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "[]"


# --- Functional Task Manager ---
def perform_add_task(tasks: List[Dict]) -> List[Dict]:
    """Handles adding a task."""
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


def filter_tasks_priority(tasks: List[Dict]) -> List[Dict]:
    """Handles filtering tasks by priority."""
    priority = input("Enter Priority [high, low]: ").strip()
    return filter_tasks_by_priority(tasks, priority)

def delete_task_by_id(tasks: List[Dict]) -> List[Dict]:
    """Handles deleting a task by its ID."""
    try:
        task_id = int(input("Enter Task ID: ").strip())  # Convert input to integer
        updated_tasks = delete_task(tasks, task_id)  # Pass the integer ID to delete_task
        print("Task deleted successfully.")
        return updated_tasks
    except ValueError:
        print("Invalid Task ID. Please enter a number.")
        return tasks
    
def view_tasks(tasks: List[Dict]) -> None:
    """Displays all tasks."""
    print("\n--- All Tasks ---")
    print(format_tasks(tasks))


def view_delayed_tasks(tasks: List[Dict]) -> None:
    """Displays delayed tasks."""
    delayed_tasks = get_delayed_tasks(tasks, datetime.now())
    print("\n--- Delayed Tasks ---")
    print(format_tasks(delayed_tasks))


def view_tasks_nearing_deadlines(tasks: List[Dict]) -> None:
    """Displays tasks nearing deadlines."""
    nearing_deadline_tasks = get_tasks_nearing_deadlines(tasks, datetime.now(), days_before_deadline=3)
    print("\n--- Tasks Nearing Deadlines ---")
    print(format_tasks(nearing_deadline_tasks))


def save_and_exit(tasks: List[Dict]) -> None:
    """Saves tasks to a file and exits."""
    save_data = save_to_data(tasks)
    write_to_file('tasks2.json', save_data)
    print("Tasks saved successfully. Exiting...")


def task_manager(tasks: List[Dict]) -> None:
    """Main task manager function with functional programming style."""
    def menu_choice() -> str:
        """Prompts user for input and returns the choice."""
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

