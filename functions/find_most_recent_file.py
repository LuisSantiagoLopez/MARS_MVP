import glob
import os

def find_most_recent_file(directory_path):
    file_extensions=['jpg', 'jpeg', 'png', 'heic']
    files = []
    for ext in file_extensions:
        full_pattern = os.path.join(directory_path, f"*.{ext}")
        files.extend(glob.glob(full_pattern))

    if not files:
        return None

    files.sort()
    most_recent_file = files[-1]

    return most_recent_file