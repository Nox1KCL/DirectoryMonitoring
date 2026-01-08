import os
import re
from pathlib import Path
import shutil
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from user import User

# Добавити в документацію для Linux скачати lsof

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

    # Створюємо папку по остаточному шляху
    destination_path.mkdir(exist_ok=True)

    # шлях куда зберігати сам файл
    final_path = destination_path / file.name

    if final_path.exists():
        stem = file.stem  
        suffix = file.suffix
        
        match = re.search(r'^(.*) \((\d+)\)$', stem)
        
        if match:
            base_name = match.group(1)
            counter = int(match.group(2)) + 1
        else:
            base_name = stem
            counter = 1
            
        while True:
            new_name = f"{base_name} ({counter}){suffix}"
            final_path = destination_path / new_name
            
            if not final_path.exists():
                break
            counter += 1

    try:
        time.sleep(0.1)
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
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Programs": [".exe", ".deb", ".appimage"]
}

downloads_path = user.downloads_path
pictures_path = user.pictures_path


# Обробник бібліотеки watchdog, який слідкує за подіями у папці Download
class DownloadHandler(FileSystemEventHandler):
    def __init__(self, callback_func):
        self.callback_func = callback_func
        # Створюємо структуру для уникнення проблеми багаторазового збереження
        self.processing_files = set()

    # Колбек
    def log(self, message):
        if self.callback_func:      
            self.callback_func(message) 
        else:
            print(message)          

    
    def process_file(self, file_path) -> None:
        file = Path(file_path)

        # Перевірка чи в сеті є файл який вже обробляли
        if str(file) in self.processing_files:
            return
        
        # Додаємо в сет файл який обробляємо
        self.processing_files.add(str(file))

        try:
            
            if file.parent.name in rules:
                return
            
            if not file.exists() or file.is_dir():
                return

            if file.suffix in ['.crdownload', '.part', '.tmp']:
                return

            if file.name.startswith('.') or file.name.startswith('~'):
                return
            
            attempts = 0
            max_attempts = 10
            is_ready = False

            while attempts < max_attempts:
                locked = is_file_locked(file)
                
                last_modified_delta = time.time() - file.stat().st_mtime
                is_fresh = last_modified_delta < 1.0 

                if locked:
                    self.log(f"Файл {file.name} зайнятий системою. Чекаю...")
                elif is_fresh:
                    self.log(f"Файл {file.name} занадто 'гарячий' (зберігається). Чекаю...")
                else:
                    is_ready = True
                    break

                time.sleep(1)
                attempts += 1

            if not is_ready:
                self.log(f"Пропуск: {file.name} не вдалося захопити (зайнятий).")
                return


            for folder_name, extension in rules.items():
                if file.suffix.lower() in extension:
                    is_picture = (folder_name == "Images")
                    file_moving(folder_name=folder_name, file=file, is_picture=is_picture)

            return
        
        except Exception as e:
            self.log(f"Помилка при обробці: {e}")
        
        finally:
            # Видаляємо з сету файли які обробляли
            if str(file) in self.processing_files:
                self.processing_files.remove(str(file))

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
            fresh_data = user.load_from_json('user_data.json')
            is_recursive = fresh_data.get('recursive', False)
            self.observer.schedule(self.handler, self.path, recursive=is_recursive)
            self.observer.start()
            self.is_running = True
            return "Моніторинг запущено"

    # Функція СТОП
    def stop(self):
        if self.is_running:
            self.observer.stop() 
            self.observer.join() 
            # Так як обсервер одноразовий, готуємо наступний
            self.observer = Observer() 
            self.is_running = False
            return "Моніторинг зупинено"
    
    def restart(self):
        self.stop()
        self.start()
        return "Моніторинг перезапущено"
