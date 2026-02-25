"""
PSEUDOCODE FOR TASK MANAGER:

1. Define a function to display a welcome message.
2. Load user credentials from 'user.txt' or create a default file if missing.
3. Define a function to register new users, ensuring unique usernames.
4. Define a function to add tasks, validating user and date inputs.
5. Define a function to view all tasks.
6. Define a function to view tasks assigned to the current user, with editing options.
7. Define a function to view completed tasks.
8. Define a function to delete tasks.
9. Define a function to generate reports on tasks and user performance.
10. Define a function to display statistics using generated report files.
11. In the main function:
    - Display welcome page.
    - Loop login until valid credentials.
    - Display menu options based on user role.
    - Execute selected menu functions.
    - On exit, show goodbye and return to welcome screen.
"""
from datetime import datetime
import os

# ===== Welcome Page Function =====
def show_welcome_page():
    # Displays a welcome banner
    print("""
====================================
      WELCOME TO TASK MANAGER
====================================
""")

# ===== Load Users Function =====
def load_users():
    # Loads user credentials from user.txt into a dictionary
    users = {}
    if os.path.exists("user.txt"):
        with open("user.txt", "r") as user_file:
            for line in user_file:
                try:
                    username, password = line.strip().split(", ")
                    users[username] = password
                except ValueError:
                    continue  # Skip lines that don't have exactly two parts
    else:
        # Create default admin user if file doesn't exist
        print("user.txt file is missing. Creating a default one with admin user.")
        with open("user.txt", "w") as user_file:
            user_file.write("admin, adm1n\n")
        users["admin"] = "adm1n"
    return users

# ===== Register User Function =====
def reg_user(users):
    # Allows the admin to register a new user
    while True:
        new_user = input("Enter new username (or 'e' to cancel): ").strip()
        if new_user.lower() == 'e':
            return
        if new_user in users:
            print("This username already exists. Try another one.")
            continue
        new_pass = input("Enter new password (or 'e' to cancel): ").strip()
        if new_pass.lower() == 'e':
            return
        confirm_pass = input("Confirm password: ").strip()
        if new_pass == confirm_pass:
            with open("user.txt", "a") as user_file:
                user_file.write(f"{new_user}, {new_pass}\n")
            users[new_user] = new_pass
            print("User registered successfully.")
            return
        else:
            print("Passwords do not match. Try again.")

# ===== Add Task Function =====
def add_task(users):
    # Allows a user to assign a task to any valid user
    while True:
        task_user = input("Enter the username to assign the task (or 'e' to cancel): ").strip()
        if task_user.lower() == 'e':
            return
        if task_user not in users:
            print("User does not exist. Please try again.")
            continue
        title = input("Enter task title: ")
        description = input("Enter task description: ")
        while True:
            due_date_str = input("Enter due date (e.g., 25 Oct 2024): ")
            try:
                datetime.strptime(due_date_str, "%d %b %Y")
                break
            except ValueError:
                print("Incorrect format. Please use 'DD Mon YYYY' (e.g., 25 Oct 2024).")
        assigned_date = datetime.today().strftime("%d %b %Y")
        completed = input("Is the task completed? (Yes/No): ").capitalize()
        if completed not in ["Yes", "No"]:
            completed = "No"
        with open("tasks.txt", "a") as task_file:
            task_file.write(f"{task_user}, {title}, {description}, {assigned_date}, {due_date_str}, {completed}\n")
        print("Task added successfully.")
        return

# ===== View All Tasks Function =====
def view_all():
    # Displays all tasks from the file
    if not os.path.exists("tasks.txt"):
        print("No tasks found.")
        return
    with open("tasks.txt", "r") as task_file:
        tasks = task_file.readlines()
        if not tasks:
            print("No tasks found.")
            return
        for task in tasks:
            task_parts = task.strip().split(", ")
            if len(task_parts) != 6:
                continue
            print(f"""
Task: {task_parts[1]}
Assigned to: {task_parts[0]}
Date Assigned: {task_parts[3]}
Due Date: {task_parts[4]}
Task Complete? {task_parts[5]}
Description:
{task_parts[2]}
""")

# ===== Recursive function for valid task number input =====
def get_valid_task_number(max_task_num):
    # Ensures the user inputs a valid task number
    try:
        choice = int(input(f"Select a task number to edit/mark complete (or -1 to return to main menu): "))
        if choice == -1:
            return -1
        if 1 <= choice <= max_task_num:
            return choice
        else:
            print("Invalid task number.")
            return get_valid_task_number(max_task_num)
    except ValueError:
        print("Please enter a valid integer.")
        return get_valid_task_number(max_task_num)

# ===== View My Tasks Function =====
def view_mine(username, users):
    # Displays and allows editing of tasks assigned to the logged-in user
    if not os.path.exists("tasks.txt"):
        print("No tasks found.")
        return

    with open("tasks.txt", "r") as task_file:
        tasks = [task.strip().split(", ") for task in task_file if len(task.strip().split(", ")) == 6]

    user_tasks = [task for task in tasks if task[0] == username]

    if not user_tasks:
        print("No tasks found for your user.")
        return

    while True:
        print("\nYour Tasks:")
        for i, task in enumerate(user_tasks, 1):
            print(f"{i}: Task: {task[1]}, Due: {task[4]}, Completed: {task[5]}")

        choice = get_valid_task_number(len(user_tasks))
        if choice == -1:
            break

        selected_task = user_tasks[choice - 1]
        print(f"\nSelected Task: {selected_task[1]} (Completed: {selected_task[5]})")

        if selected_task[5].lower() == "yes":
            print("This task is already completed and cannot be edited.")
            continue

        action = input("Choose action - 'c' to mark complete, 'e' to edit, or 'b' to go back: ").lower()
        if action == 'c':
            selected_task[5] = "Yes"
            print("Task marked as complete.")
        elif action == 'e':
            new_user = input(f"Enter new username to assign task (current: {selected_task[0]}), or press Enter to skip: ").strip()
            if new_user and new_user in users:
                selected_task[0] = new_user
            elif new_user:
                print("Username not found, skipping username change.")
            while True:
                new_due_date = input(f"Enter new due date (DD Mon YYYY) (current: {selected_task[4]}), or press Enter to skip: ").strip()
                if not new_due_date:
                    break
                try:
                    datetime.strptime(new_due_date, "%d %b %Y")
                    selected_task[4] = new_due_date
                    break
                except ValueError:
                    print("Invalid date format. Try again.")
        elif action == 'b':
            continue
        else:
            print("Invalid action. Returning to tasks list.")
            continue

        # Update tasks list and write changes to file
        task_index = tasks.index(user_tasks[choice - 1])
        tasks[task_index] = selected_task

        with open("tasks.txt", "w") as task_file:
            for task in tasks:
                task_file.write(", ".join(task) + "\n")

        # Reload user tasks after update
        user_tasks = [task for task in tasks if task[0] == username]

# ===== View Completed Tasks Function =====
def view_completed():
    # Displays all completed tasks
    if not os.path.exists("tasks.txt"):
        print("No tasks found.")
        return
    with open("tasks.txt", "r") as task_file:
        tasks = task_file.readlines()
    found = False
    for task in tasks:
        task_parts = task.strip().split(", ")
        if len(task_parts) == 6 and task_parts[5].lower() == "yes":
            found = True
            print(f"""
Task: {task_parts[1]}
Assigned to: {task_parts[0]}
Date Assigned: {task_parts[3]}
Due Date: {task_parts[4]}
Description:
{task_parts[2]}
""")
    if not found:
        print("No completed tasks found.")

# ===== Delete Task Function =====
def delete_task():
    # Allows deletion of a task by number
    if not os.path.exists("tasks.txt"):
        print("No tasks found.")
        return
    with open("tasks.txt", "r") as task_file:
        tasks = task_file.readlines()
    if not tasks:
        print("No tasks found.")
        return
    for i, task in enumerate(tasks, 1):
        print(f"{i}: {task.strip()}")
    try:
        task_number = int(input("Enter task number to delete: "))
        if 1 <= task_number <= len(tasks):
            tasks.pop(task_number - 1)
            with open("tasks.txt", "w") as task_file:
                task_file.writelines(tasks)
            print("Task deleted.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

# ===== Generate Reports Function =====
def generate_reports(users):
    # Generates two reports: task_overview.txt and user_overview.txt
    if not os.path.exists("tasks.txt"):
        print("No tasks to generate reports from.")
        return

    with open("tasks.txt", "r") as task_file:
        tasks = [task.strip().split(", ") for task in task_file if len(task.strip().split(", ")) == 6]

    # Summary stats
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t[5].lower() == "yes")
    uncompleted_tasks = total_tasks - completed_tasks
    overdue_tasks = sum(1 for t in tasks if t[5].lower() == "no" and datetime.strptime(t[4], "%d %b %Y") < datetime.today())
    pct_incomplete = (uncompleted_tasks / total_tasks * 100) if total_tasks else 0
    pct_overdue = (overdue_tasks / total_tasks * 100) if total_tasks else 0

    # Write task overview
    with open("task_overview.txt", "w") as task_report:
        task_report.write(f"Total tasks: {total_tasks}\n")
        task_report.write(f"Completed tasks: {completed_tasks}\n")
        task_report.write(f"Uncompleted tasks: {uncompleted_tasks}\n")
        task_report.write(f"Overdue tasks: {overdue_tasks}\n")
        task_report.write(f"Percentage incomplete: {pct_incomplete:.2f}%\n")
        task_report.write(f"Percentage overdue: {pct_overdue:.2f}%\n")

    # Write user overview
    total_users = len(users)
    user_stats = {}
    for user in users:
        user_tasks = [t for t in tasks if t[0] == user]
        total_user_tasks = len(user_tasks)
        completed_user_tasks = sum(1 for t in user_tasks if t[5].lower() == "yes")
        uncompleted_user_tasks = total_user_tasks - completed_user_tasks
        overdue_user_tasks = sum(1 for t in user_tasks if t[5].lower() == "no" and datetime.strptime(t[4], "%d %b %Y") < datetime.today())
        pct_tasks_assigned = (total_user_tasks / total_tasks * 100) if total_tasks else 0
        pct_completed = (completed_user_tasks / total_user_tasks * 100) if total_user_tasks else 0
        pct_uncompleted = (uncompleted_user_tasks / total_user_tasks * 100) if total_user_tasks else 0
        pct_overdue = (overdue_user_tasks / total_user_tasks * 100) if total_user_tasks else 0

        user_stats[user] = {
            "total_tasks": total_user_tasks,
            "pct_tasks_assigned": pct_tasks_assigned,
            "pct_completed": pct_completed,
            "pct_uncompleted": pct_uncompleted,
            "pct_overdue": pct_overdue,
        }

    with open("user_overview.txt", "w") as user_report:
        user_report.write(f"Total users: {total_users}\n")
        user_report.write(f"Total tasks: {total_tasks}\n\n")
        for user, stats in user_stats.items():
            user_report.write(f"User: {user}\n")
            user_report.write(f"  Total tasks assigned: {stats['total_tasks']}\n")
            user_report.write(f"  Percentage of total tasks assigned: {stats['pct_tasks_assigned']:.2f}%\n")
            user_report.write(f"  Percentage completed: {stats['pct_completed']:.2f}%\n")
            user_report.write(f"  Percentage uncompleted: {stats['pct_uncompleted']:.2f}%\n")
            user_report.write(f"  Percentage overdue: {stats['pct_overdue']:.2f}%\n\n")

    print("Reports generated successfully.")

# ===== Display Statistics Function =====
def display_statistics(users):
    # Displays content of the generated report files
    if not (os.path.exists("task_overview.txt") and os.path.exists("user_overview.txt")):
        print("Reports not found, generating reports first...")
        generate_reports(users)

    print("\n--- Task Overview ---")
    with open("task_overview.txt", "r") as task_report:
        print(task_report.read())

    print("--- User Overview ---")
    with open("user_overview.txt", "r") as user_report:
        print(user_report.read())

# ===== Main Function =====
def main():
    # Main login and menu loop
    while True:
        show_welcome_page()
        users = load_users()

        # Login loop
        while True:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if username in users and users[username] == password:
                print(f"Welcome, {username}!")
                break
            else:
                print("Invalid username or password. Please try again.\n")

        # Main menu
        while True:
            if username == "admin":
                menu = """
Please select one of the following options:
r  - Register user
a  - Add task
va - View all tasks
vm - View my tasks
gr - Generate reports
ds - Display statistics
e  - Exit
"""
            else:
                menu = """
Please select one of the following options:
a  - Add task
va - View all tasks
vm - View my tasks
e  - Exit
"""
            print(menu)
            choice = input("Your choice: ").lower()

            if choice == "r" and username == "admin":
                reg_user(users)
            elif choice == "a":
                add_task(users)
            elif choice == "va":
                view_all()
            elif choice == "vm":
                view_mine(username, users)
            elif choice == "gr" and username == "admin":
                generate_reports(users)
            elif choice == "ds" and username == "admin":
                display_statistics(users)
            elif choice == "e":
                print("Goodbye!\n")
                break
            else:
                print("Invalid choice. Please try again.")

# ===== Run Program =====
if __name__ == "__main__":
    main()
