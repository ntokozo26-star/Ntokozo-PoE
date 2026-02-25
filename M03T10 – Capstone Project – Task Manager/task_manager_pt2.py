'''
TASK MANAGER PROGRAM
--------------------
Pseudocode Overview:

1. Display a welcome banner.
2. Load users from "user.txt" into a dictionary:
   - If the file does not exist, create it and add the default admin credentials.
3. Prompt user to log in:
   - Ask for username and password.
   - If credentials are invalid, loop until valid credentials are entered.
4. After login, display the main menu:
   - 'r': Register a new user (admin only)
       - Prompt for new username and password (with confirmation).
       - Ensure passwords match.
       - Validate input and allow user to quit registration.
       - If successful, append to user.txt.
   - 'a': Add a task
       - Prompt for task details (user, title, description, due date).
       - Validate assigned user and prompt to re-enter if not found.
       - Confirm due date is in the correct format (e.g., 25 Oct 2024).
       - Allow user to quit or exit mid-task input.
       - Prompt whether task is completed ('Yes' or 'No').
       - Append the task to tasks.txt.
   - 'va': View all tasks
       - Read and display each task in a formatted output.
       - Handle missing or malformed task entries.
   - 'vm': View only the logged-in user's tasks
       - Display tasks assigned to the current user.
   - 'vc': View completed tasks (admin only)
       - Show only tasks marked as completed.
   - 'del': Delete tasks (admin only)
       - Display all tasks with index numbers.
       - Prompt to select a task number for deletion.
       - Remove the selected task from the file.
   - 'e': Exit
       - Log out and return to the welcome page.
5. Program loops back to login after logging out.
6. Defensive programming and error handling throughout:
   - File existence checks.
   - Input validation.
   - Try-except blocks for parsing and I/O.
'''

from datetime import datetime
import os

# ===== Welcome Page Function =====
def show_welcome_page():
    # Print the welcome banner
    print("""
====================================
      WELCOME TO TASK MANAGER
====================================
""")

# ===== Load Users Function =====
def load_users():
    users = {}  # Dictionary to store username:password pairs

    # Check if user.txt exists
    if os.path.exists("user.txt"):
        with open("user.txt", "r") as user_file:
            for line in user_file:
                try:
                    # Split each line into username and password
                    username, password = line.strip().split(", ")
                    users[username] = password
                except ValueError:
                    # Skip malformed lines
                    continue
    else:
        # If file doesn't exist, create one with default admin user
        print("user.txt file is missing. Creating a default one with admin user.")
        with open("user.txt", "w") as user_file:
            user_file.write("admin, adm1n\n")
        users["admin"] = "adm1n"
    
    return users  # Return the loaded users

# ===== Main Program Loop =====
while True:
    show_welcome_page()  # Display welcome banner

    # ===== Login Section =====
    users = load_users()  # Load user credentials from file

    while True:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        # Validate login
        if username in users and users[username] == password:
            print(f"\nWelcome, {username}!")
            break  # Successful login
        else:
            print("Invalid username or password. Please try again.\n")

    # ===== Main Menu =====
    while True:
        # Display menu based on whether user is admin
        if username == "admin":
            menu = input(
                '''\nPlease select one of the following options:
r - register user
a - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
del - delete tasks
e - exit
Enter selection: ''').lower()
        else:
            menu = input(
                '''\nPlease select one of the following options:
a - add task
va - view all tasks
vm - view my tasks
e - exit
Enter selection: ''').lower()

        # ===== Register New User (Admin Only) =====
        if menu == 'r' and username == 'admin':
            new_username = input("Enter new username (or type 'q' or 'e' to quit): ").strip()
            if new_username.lower() in ['q', 'e']:
                if new_username.lower() == 'e':
                    print("Logging out...\n")
                    break  # Exit to login screen
                continue
            if new_username in users:
                print("Username already exists. Try again.")
                continue

            new_password = input("Enter new password (or type 'q' or 'e' to quit): ").strip()
            if new_password.lower() in ['q', 'e']:
                if new_password.lower() == 'e':
                    print("Logging out...\n")
                    break
                continue

            confirm_password = input("Confirm password (or type 'q' or 'e' to quit): ").strip()
            if confirm_password.lower() in ['q', 'e']:
                if confirm_password.lower() == 'e':
                    print("Logging out...\n")
                    break
                continue

            if new_password != confirm_password:
                print("Passwords do not match. Try again.")
                continue

            # Add new user to file and dictionary
            with open("user.txt", "a") as user_file:
                user_file.write(f"{new_username}, {new_password}\n")
            users[new_username] = new_password
            print("New user registered successfully.")

        # ===== Add Task =====
        elif menu == 'a':
            while True:
                assigned_user = input("Enter the username the task is assigned to (or type 'q' or 'e' to quit): ").strip()
                if assigned_user.lower() in ['q', 'e']:
                    if assigned_user.lower() == 'e':
                        print("Logging out...\n")
                        break
                    break
                if assigned_user not in users:
                    print("User does not exist. Please re-enter a valid username.")
                    continue
                break
            if assigned_user.lower() in ['q', 'e']:
                continue

            # Get task details
            title = input("Enter the title of the task (or type 'q' or 'e' to quit): ").strip()
            if title.lower() in ['q', 'e']:
                if title.lower() == 'e':
                    print("Logging out...\n")
                    break
                continue
            description = input("Enter the description of the task (or type 'q' or 'e' to quit): ").strip()
            if description.lower() in ['q', 'e']:
                if description.lower() == 'e':
                    print("Logging out...\n")
                    break
                continue

            # Validate due date
            while True:
                due_date = input("Enter the due date (e.g. 25 Oct 2024) (or type 'q' or 'e' to quit): ").strip()
                if due_date.lower() in ['q', 'e']:
                    if due_date.lower() == 'e':
                        print("Logging out...\n")
                        break
                    break
                try:
                    datetime.strptime(due_date, "%d %b %Y")  # Check format
                    break
                except ValueError:
                    print("Invalid date format. Please use 'DD Mon YYYY' format.")
            else:
                continue
            if due_date.lower() in ['q', 'e']:
                continue

            # Ask if task is completed
            while True:
                completed = input("Is the task completed? (Yes/No): ").strip().capitalize()
                if completed in ["Yes", "No"]:
                    break
                print("Invalid input. Please enter 'Yes' or 'No'.")

            assigned_date = datetime.today().strftime("%d %b %Y")  # Get today's date

            # Write task to file
            with open("tasks.txt", "a") as task_file:
                task_file.write(f"{assigned_user}, {title}, {description}, {assigned_date}, {due_date}, {completed}\n")
            print("Task successfully added.")

        # ===== View All Tasks =====
        elif menu == 'va':
            if not os.path.exists("tasks.txt"):
                print("No tasks found.")
                continue

            with open("tasks.txt", "r") as task_file:
                found_task = False
                for line in task_file:
                    try:
                        user, title, description, date_assigned, due_date, completed = line.strip().split(", ")
                        print(f"\nTask: {title}\nAssigned to: {user}\nDate Assigned: {date_assigned}\nDue Date: {due_date}\nCompleted: {completed}\nDescription: {description}\n")
                        found_task = True
                    except ValueError:
                        print("Malformed task entry. Skipping.")
                if not found_task:
                    print("No tasks to display.")

        # ===== View My Tasks =====
        elif menu == 'vm':
            if not os.path.exists("tasks.txt"):
                print("No tasks found.")
                continue

            found = False
            with open("tasks.txt", "r") as task_file:
                for line in task_file:
                    try:
                        user, title, description, date_assigned, due_date, completed = line.strip().split(", ")
                        if user == username:
                            found = True
                            print(f"\nTask: {title}\nAssigned to: {user}\nDate Assigned: {date_assigned}\nDue Date: {due_date}\nCompleted: {completed}\nDescription: {description}\n")
                    except ValueError:
                        continue
            if not found:
                print("No tasks assigned to you.")

        # ===== View Completed Tasks (Admin Only) =====
        elif menu == 'vc' and username == 'admin':
            if not os.path.exists("tasks.txt"):
                print("No tasks found.")
                continue

            found = False
            with open("tasks.txt", "r") as task_file:
                for line in task_file:
                    try:
                        user, title, description, date_assigned, due_date, completed = line.strip().split(", ")
                        if completed.lower() == "yes":
                            found = True
                            print(f"\nTask: {title}\nAssigned to: {user}\nDate Assigned: {date_assigned}\nDue Date: {due_date}\nCompleted: {completed}\nDescription: {description}\n")
                    except ValueError:
                        continue
            if not found:
                print("No completed tasks found.")

        # ===== Delete Tasks (Admin Only) =====
        elif menu == 'del' and username == 'admin':
            if not os.path.exists("tasks.txt"):
                print("No tasks available to delete.")
                continue

            with open("tasks.txt", "r") as file:
                tasks = file.readlines()

            # Display tasks with numbers
            for i, task in enumerate(tasks, 1):
                try:
                    user, title, description, date_assigned, due_date, completed = task.strip().split(", ")
                    print(f"{i}. Task: {title} | Assigned to: {user} | Due: {due_date} | Completed: {completed}")
                except ValueError:
                    print(f"{i}. [Malformed task entry]")

            # Prompt user to choose task to delete
            try:
                task_num = int(input("Enter the task number to delete (or 0 to cancel): "))
                if task_num == 0:
                    continue
                if 1 <= task_num <= len(tasks):
                    deleted = tasks.pop(task_num - 1)  # Remove the selected task
                    with open("tasks.txt", "w") as file:
                        file.writelines(tasks)
                    print("Task deleted successfully.")
                else:
                    print("Invalid task number.")
            except ValueError:
                print("Please enter a valid number.")

        # ===== Exit Program =====
        elif menu == 'e':
            print("Logging out...\n")
            break

        # ===== Invalid Input =====
        else:
            print("Invalid input. Please select a valid option.")
