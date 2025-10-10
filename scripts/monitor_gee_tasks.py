# scripts/monitor_gee_tasks.py
import ee
import time
import os

# Ensure GEE is initialized (using your project ID from config/regions.py for consistency)
# This script will need to be run from an environment where GEE is authenticated.
# It's good practice to get the project ID dynamically or from config.
# For now, let's hardcode it for simplicity based on your setup.
GEE_PROJECT_ID = 'gaias-ark' # <--- REPLACE WITH YOUR ACTUAL GEE PROJECT ID!

def monitor_all_gee_tasks():
    """Monitors all currently running GEE tasks until they complete or fail."""
    try:
        ee.Initialize(project=GEE_PROJECT_ID)
        print("GEE initialized for task monitoring.")
    except ee.EEException as e:
        print(f"Error initializing GEE: {e}")
        print("Please ensure you've authenticated 'earthengine authenticate' for this environment.")
        return

    print("\n--- Monitoring GEE Export Tasks ---")
    tasks_to_monitor = []

    # Get a list of all current tasks
    # ee.data.getTaskList() is a useful low-level API call
    task_list = ee.data.getTaskList()

    for task_info in task_list:
        if task_info['state'] in ['RUNNING', 'READY', 'UNSUBMITTED']:
            tasks_to_monitor.append(task_info['id'])
            print(f"Monitoring Task ID: {task_info['id']} | Description: {task_info.get('description', 'N/A')} | State: {task_info['state']}")

    if not tasks_to_monitor:
        print("No active GEE tasks to monitor.")
        return

    while tasks_to_monitor:
        completed_tasks = []
        for task_id in tasks_to_monitor:
            status = ee.data.getTaskStatus(task_id)[0] # getTaskStatus returns a list
            current_state = status['state']
            description = status.get('description', 'N/A')

            if current_state == 'RUNNING':
                print(f"[{time.strftime('%H:%M:%S')}] Task ID: {task_id} | Desc: {description} | State: {current_state} | Progress: {status.get('progress', 0):.2f}%")
            elif current_state == 'COMPLETED':
                print(f"[{time.strftime('%H:%M:%S')}] Task ID: {task_id} | Desc: {description} | *** COMPLETED SUCCESSFULLY ***")
                completed_tasks.append(task_id)
            elif current_state == 'FAILED':
                error_message = status.get('error_message', 'No specific error message.')
                print(f"[{time.strftime('%H:%M:%S')}] Task ID: {task_id} | Desc: {description} | !!! FAILED !!! Error: {error_message}")
                completed_tasks.append(task_id)
            # You can add checks for 'CANCELED' or 'READY' states if needed

        for task_id in completed_tasks:
            tasks_to_monitor.remove(task_id)

        if tasks_to_monitor:
            time.sleep(60) # Check every 60 seconds

    print("\n--- All monitored GEE tasks have completed or failed. ---")

if __name__ == "__main__":
    monitor_all_gee_tasks()