import os
import subprocess
import git
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

repo_path = r"C:\Users\mohan\OneDrive\Desktop\GitHub_Repo\publication_crawler"
script_path = os.path.join(repo_path, 'test_script.py')
log_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'log')
log_file = os.path.join(log_dir, 'last_run.log')

os.makedirs(log_dir, exist_ok=True)

def show_message(title, message):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, message)
    root.destroy()

def log_message(message):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")

def log_last_run_time():
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}: Last run time logged.\n")

def get_last_run_time():
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f.readlines():
                if "Last run time logged." in line:
                    return datetime.fromisoformat(line.split(":")[0])
    return None

# def should_run():
#     last_run_time = get_last_run_time()
#     if last_run_time is None:
#         return True
#     next_run_time = last_run_time + timedelta(days=15)
#     return datetime.now() >= next_run_time

# def run_script():
#     log_message("Attempting to run the test script.")
#     try:
#         subprocess.run(['python', script_path], check=True)
#         log_message("Script executed successfully.")
#     except subprocess.CalledProcessError as e:
#         log_message(f"Error executing script: {e}")

def commit_and_push_changes():
    log_message("Attempting to commit and push changes.")
    try:
        repo = git.Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.set_url('git@github.com:Yolo1105/task_auto_scheduler.git')
        repo.git.add(A=True)
        repo.index.commit(f"Auto-commit on {datetime.now()}")
        origin.push()
        log_message("Changes pushed to GitHub.")
        show_message("Upload Success", "Changes have been successfully pushed to GitHub.")
    except Exception as e:
        log_message(f"Error during commit/push: {e}")
        show_message("Upload Failed", "There was an error pushing changes to GitHub.")

if __name__ == "__main__":
    log_message("Script started.")
    show_message("Script Start", "The script is starting to run.")
    log_message("Script start running.")
    
    run_script()
    commit_and_push_changes()
    log_last_run_time()

    show_message("Script End", "The script has finished running.")
    log_message("Script finished running.")
