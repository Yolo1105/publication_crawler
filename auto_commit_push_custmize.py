import os
import subprocess
import git
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

# Configuration paths
repo_path = r"YOUR_REPO_PATH"  # Replace with your Git repository path
script_path = os.path.join(repo_path, 'YOUR_SCRIPT.py')  # Replace with your Python script path
log_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'log')
log_file = os.path.join(log_dir, 'last_run.log')  # Log file to store the last run time

# Ensure the log directory exists
os.makedirs(log_dir, exist_ok=True)

# Show popup message
def show_message(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Always on top
    messagebox.showinfo(title, message)
    root.destroy()

# Log message
def log_message(message):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")

# Log the last run time
def log_last_run_time():
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}: Last run time logged.\n")

# Get the last run time
def get_last_run_time():
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f.readlines():
                if "Last run time logged." in line:
                    return datetime.fromisoformat(line.split(":")[0])
    return None

# Check if the script should run
def should_run():
    last_run_time = get_last_run_time()
    if last_run_time is None:
        return True
    next_run_time = last_run_time + timedelta(days=15)  # Adjust the interval as needed
    return datetime.now() >= next_run_time

# Run the Python script
def run_script():
    log_message("Attempting to run the script.")
    try:
        subprocess.run(['python', script_path], check=True)
        log_message("Script executed successfully.")
    except subprocess.CalledProcessError as e:
        log_message(f"Error executing script: {e}")

# Commit and push changes to GitHub
def commit_and_push_changes():
    log_message("Attempting to commit and push changes.")
    try:
        repo = git.Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.set_url('YOUR_SSH_GITHUB_URL')  # Replace with your SSH GitHub URL
        repo.git.add(A=True)  # Add all changes
        repo.index.commit(f"Auto-commit on {datetime.now()}")
        origin.push()
        log_message("Changes pushed to GitHub.")
        show_message("Upload Success", "Changes have been successfully pushed to GitHub.")
    except Exception as e:
        log_message(f"Error during commit/push: {e}")
        show_message("Upload Failed", "There was an error pushing changes to GitHub.")

if __name__ == "__main__":
    log_message("Script started.")
    if should_run():
        show_message("Script Start", "The script is starting to run.")
        log_message("Script start running.")
        
        # Run the Python script
        run_script()

        # Commit and push changes to GitHub
        commit_and_push_changes()

        # Log the run time
        log_last_run_time()

        show_message("Script End", "The script has finished running.")
        log_message("Script finished running.")
    else:
        log_message("Not time to run yet.")
