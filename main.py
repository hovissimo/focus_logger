from datetime import datetime
import json
from pathlib import Path
import psutil
import time
import socket
import win32gui
import win32process

HOSTNAME = socket.gethostname()
LOGDIR_PATH = Path.home() / "focus_logs"

def get_logfile_path():
    '''
    Get the path that we should be logging to right now.

    This is dynamic because there's a timestamp in the filename, and we can be running overnight.
    '''
    return Path.home() / "focus_logs" / f"focus_log_{datetime.now().strftime("%Y%m%d")}.txt"

def get_foreground_window_app():
    try:
        hwnd = win32gui.GetForegroundWindow()  # Get the handle of the foreground window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)  # Get process ID
        process = psutil.Process(pid)  # Get process info using psutil
        process_name = process.name()  # Get process name
        window_title = win32gui.GetWindowText(hwnd)  # Get window title
        return process_name, window_title
    except Exception as e:
        return None, None

def poll_foreground_app():
    current_process_name = None
    while True:
        process_name, window_title = get_foreground_window_app()
        if process_name != current_process_name:  # Does a different process have focus?
            current_process_name = process_name
            on_focus_change(process_name, window_title) # Invoke the handler
        time.sleep(0.1)

def on_focus_change(process_name, window_title):
    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "process_name": process_name,
        "hostname": HOSTNAME,
        "window_title": window_title,
    }
    log_focus_change(record, debug=True)


def log_focus_change(record, debug=False):
    '''Write a focus change record to the log.'''

    # Make sure the path exists before we try to write
    LOGDIR_PATH.mkdir(exist_ok=True)

    dumped = json.dumps(record)

    if debug:
        print(dumped)

    with get_logfile_path().open('a') as log_file:
        # Also write a newline to make these easier to read by hand
        log_file.write(dumped + '\n')

if __name__ == "__main__":
    try:
        poll_foreground_app()
    except KeyboardInterrupt:
        pass

