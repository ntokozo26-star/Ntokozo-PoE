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
   - 'e': Exit
       - Log out and return to the welcome page.
5. Program loops back to login after logging out.
6. Defensive programming and error handling throughout:
   - File existence checks.
   - Input validation.
   - Try-except blocks for parsing and I/O.
'''

# ===== Importing external modules ============
from datetime import datetime
import os

# ===== Welcome Page Function =====
def show_welcome_page():
    '''
    Displays a welcome banner. This function is called at program startup
    and after a user logs out to re-display the banner.
    '''
    print("""
====================================
      WELCOME TO TASK MANAGER
====================================
""")

# ===== Load Users Function =====
def load_users():
    '''Loads existing users from user.txt into a dictionary.'''
    users = {}
    if os.path.exists("user.txt"):
        with open("user.txt", "r") as user_file:
            for line in user_file:
                try:
                    username, password = line.strip().split(", ")
                    users[username] = password
                except ValueError:
                    continue
    else:
        # If the file does not exist, create a default admin user
        print("user.txt file is missing. Creating a default one with admin user.")
        with open("user.txt", "w") as user_file:
            user_file.write("admin, adm1n\n")
        users["admin"] = "adm1n"
    return users

# ===== Main Program Loop =====
# This loop allows returning to the login screen after logging out.
while True:
    show_welcome_page()  # Show welcome page on every restart

    # ===== Login Section =====
    users = load_users()  # Load users from file
    while True:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        if username in users and users[username] == password:
            print(f"\nWelcome, {username}!")
            break
        else:
            print("Invalid username or password. Please try again.\n")

    # ===== Main Menu =====
    while True:
        # Present options to the user
        menu = input(
            '''\nSelect one of the following options:
r - register a user
a - add task
va - view all tasks
vm - view my tasks
e - exit
: ''').lower()

        if menu == 'r':
            # Only admin is allowed to register users
            if username != 'admin':
                print("Only admin can register new users.")
                continue

            # Prompt for new user details with exit options
            new_username = input("Enter new username (or type 'q' or 'e' to quit): ").strip()
            if new_username.lower() in ['q', 'e']:
                if new_username.lower() == 'e':
                    print("Logging out...\n")
                    break
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

            # Ensure passwords match
            if new_password != confirm_password:
                print("Passwords do not match. Try again.")
                continue

            # Save new user
            with open("user.txt", "a") as user_file:
                user_file.write(f"{new_username}, {new_password}\n")
            users[new_username] = new_password
            print("New user registered successfully.")

        elif menu == 'a':
            # Prompt for task details with quit option
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

            # Get due date and validate format
            while True:
                due_date = input("Enter the due date (e.g. 25 Oct 2024) (or type 'q' or 'e' to quit): ").strip()
                if due_date.lower() in ['q', 'e']:
                    if due_date.lower() == 'e':
                        print("Logging out...\n")
                        break
                    break
                try:
                    datetime.strptime(due_date, "%d %b %Y")
                    break
                except ValueError:
                    print("Invalid date format. Please use 'DD Mon YYYY' format.")
            else:
                continue

            if due_date.lower() in ['q', 'e']:
                continue

            # Ask if the task is completed
            while True:
                completed = input("Is the task completed? (Yes/No): ").strip().capitalize()
                if completed in ["Yes", "No"]:
                    break
                print("Invalid input. Please enter 'Yes' or 'No'.")

            assigned_date = datetime.today().strftime("%d %b %Y")

            # Write task to file
            with open("tasks.txt", "a") as task_file:
                task_file.write(f"{assigned_user}, {title}, {description}, {assigned_date}, {due_date}, {completed}\n")
            print("Task successfully added.")

        elif menu == 'va':
            # View all tasks
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

        elif menu == 'vm':
            # View tasks assigned to the current user
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

        elif menu == 'e':
            # Log out to welcome page
            print("Logging out...\n")
            break

        else:
            print("Invalid input. Please select a valid option.")
