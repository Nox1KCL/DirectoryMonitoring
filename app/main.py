import os
from pathlib import Path
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from platformdirs import user_downloads_dir, user_pictures_dir

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

rules = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Audio": [".mp3", ".wav"],
    "Programs": [".exe", ".deb", ".appimage"]
}

downloads_path = Path(user_downloads_dir())
pictures_path = Path(user_pictures_dir())

def file_moving(folder_name: str, file: Path, is_picture=False):
    if is_picture:
        destination_path = pictures_path / folder_name
    else:
        destination_path = downloads_path / folder_name

    destination_path.mkdir(exist_ok=True)

    final_path = destination_path / file.name

    if final_path.exists():
        counter = 1
        stem = file.stem
        suffix = file.suffix
        
        while final_path.exists():
            new_name = f"{stem} ({counter}){suffix}"
            final_path = destination_path / new_name
            counter += 1

    try:
        time.sleep(0.5)
        shutil.move(file, final_path)
        print(f"Файл {file.name} переміщено в {folder_name}")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Невідома помилка {e}")

    return None

class DownloadHandler(FileSystemEventHandler):
    def process_file(self, file) -> None:
        file = Path(file)

        if not file.exists():
            return
        
        if file.is_dir():
            return

        if file.suffix in ['.crdownload', '.part', '.tmp']:
            return

        for folder_name, extension in rules.items():
            if file.suffix.lower() in extension:
                is_picture = (folder_name == "Images")
                file_moving(folder_name=folder_name, file=file, is_picture=is_picture)

        return


    def on_created(self, event) -> None:
        self.process_file(event.src_path)

    def on_moved(self, event) -> None:
        print(f"Файл перейменовано: з {Path(str(event.src_path)).name} на {Path(str(event.dest_path)).name}")
        self.process_file(event.dest_path)


download_handler = DownloadHandler()
observer = Observer()

observer.schedule(download_handler, str(downloads_path), recursive=False)
observer.start()

# Main start

clear_console()

print('-' * 20)
print(downloads_path)
print(pictures_path)
print('-' * 20)

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()
observer.join()

