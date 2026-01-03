import os
from pathlib import Path
import shutil
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from user import User



def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# Функція яка пересуває файл 
def file_moving(folder_name: str, file: Path, is_picture=False) -> None:
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
        print("Файл не найдено")
    except Exception as e:
        print(f"Невідома помилка {e}")

    return None

# Перевіряє чи файл зайнятий іншою програмою
def is_file_locked(filepath: Path) -> bool:
    if os.name == 'nt': 
        try:
            os.rename(filepath, filepath)
            return False
        except OSError:
            return True

    else: 
        try:
            result = subprocess.run(
                ['lsof', str(filepath)], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except Exception:
            return False


file_name = 'user_data.json'
user = User(file_name)

# Словник який відповідає за "сортування" файлів по принципу розширення : папка
rules = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Audio": [".mp3", ".wav"],
    "Programs": [".exe", ".deb", ".appimage"]
}

downloads_path = user.downloads_path
pictures_path = user.pictures_path


# Обробник бібліотеки watchdog, який слідкує за подіями у папці Download
class DownloadHandler(FileSystemEventHandler):
    def __init__(self, callback_func):
        self.callback_func = callback_func


    def log(self, message):
        if self.callback_func:      
            self.callback_func(message) 
        else:
            print(message)          

    
    def process_file(self, file_path) -> None:
        file = Path(file_path)
        
        if not file.exists() or file.is_dir():
            return

        if file.suffix in ['.crdownload', '.part', '.tmp']:
            return

        if file.name.startswith('.') or file.name.startswith('~'):
            return


        retries = 5
        while retries > 0:
            if is_file_locked(file):
                self.log(f"Файл {file.name} зайнятий (качається або редагується). Чекаємо...")
                time.sleep(1)
                retries -= 1
            else:
                break 
        
        if is_file_locked(file):
            self.log(f"Пропуск: {file.name} відкритий в іншій програмі.")
            return


        for folder_name, extension in rules.items():
            if file.suffix.lower() in extension:
                is_picture = (folder_name == "Images")
                file_moving(folder_name=folder_name, file=file, is_picture=is_picture)

        return

    # Реагує на файл який створено / добавлено
    def on_created(self, event) -> None:
        self.process_file(event.src_path)

    # Реагує на переміщення / копіювання / перейменування файлу
    def on_moved(self, event) -> None:
        print(f"Файл перейменовано: з {Path(str(event.src_path)).name} на {Path(str(event.dest_path)).name}")
        self.process_file(event.dest_path)


class MonitorManager:
    def __init__(self, log_callback=None):
        self.observer = Observer()
        self.handler = DownloadHandler(callback_func=log_callback) 
        self.path = str(user.downloads_path)
        self.is_running = False

    # Функція СТАРТ
    def start(self):
        if not self.is_running:
            self.observer.schedule(self.handler, self.path, recursive=False)
            self.observer.start()
            self.is_running = True
            return "Моніторинг запущено"

    # Функція СТОП
    def stop(self):
        if self.is_running:
            self.observer.stop() 
            self.observer.join() 
            self.observer = Observer() 
            self.is_running = False
            return "Моніторинг зупинено"