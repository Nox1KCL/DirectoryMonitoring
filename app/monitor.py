import os
import re
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
def file_moving(file: Path, 
                path_to_save: Path, 
                folder_name: str, 
                create_subfolder: bool) -> None:
    if create_subfolder:
        path_to_save = path_to_save / folder_name
    else:
        path_to_save = path_to_save

    # шлях куда зберігати сам файл
    final_path = path_to_save / file.name

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
            final_path = path_to_save / new_name
            
            if not final_path.exists():
                break
            counter += 1
    # Створюємо папку призначення якщо не існує
    path_to_save.mkdir(parents=True, exist_ok=True)
    
    try:
        time.sleep(0.1)
        # Перевіряємо чи файл все ще існує
        if not file.exists():
            print(f"File {file.name} no longer exists")
            return None
        shutil.move(file, final_path)
        print(f"File {file.name} moved to {final_path}")
    except FileNotFoundError:
        print(f"File not Found: {file}")
    except Exception as e:
        print(f"Undefined Error {e}")

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


class DownloadHandler(FileSystemEventHandler):
    """
    Хендлер папки downloads, слідкує за подіями
    """
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

    # Отримуємо шлях куди зберегти файл
    def get_path(self, file: Path):
        # Перезавантажуємо дані з JSON щоб отримати актуальні налаштування
        fresh_data = user.load_from_json(file_name)
        
        for folder_name, extension in rules.items():
            if file.suffix.lower() in extension:
                # Беремо назву папки, шукаємо чи в файлі json є такий шлях і витягуємо
                json_key = folder_name.lower() + "_path"
                if json_key in fresh_data:
                    path_to_save = Path(fresh_data[json_key])
                    create_subfolder = False
                else:
                    path_to_save = Path(user.data.get("monitoring_path", user.default_path))
                    create_subfolder = True

                return folder_name, path_to_save, create_subfolder

        return None, None, None

    # Обробка файлу
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

            # Перевіряємо чи файл зайнятий іншою прогою
            while attempts < max_attempts:
                # Перевіряємо чи файл ще існує
                if not file.exists():
                    self.log(f"File {file.name} no longer exists.")
                    return
                
                locked = is_file_locked(file)
                
                try:
                    last_modified_delta = time.time() - file.stat().st_mtime
                except FileNotFoundError:
                    self.log(f"File {file.name} disappeared during processing.")
                    return
                
                is_fresh = last_modified_delta < 1.0 

                if locked:
                    self.log(f"File {file.name} is busy with the system. Waiting...")
                elif is_fresh:
                    self.log(f"File {file.name} so 'hot' (Saving). Waiting...")
                else:
                    is_ready = True
                    break

                time.sleep(1)
                attempts += 1

            if not is_ready:
                self.log(f"Skip: {file.name} couldn't catch (busy).")
                return


            folder_name, path_to_save, create_subfolder = self.get_path(file)
            if folder_name and path_to_save and create_subfolder is not None:
                file_moving(file=file, 
                            path_to_save=path_to_save, # type: ignore
                            folder_name=folder_name, # type: ignore
                            create_subfolder=create_subfolder) # type: ignore
            else:
                self.log("Path Error..")

        except Exception as e:
            self.log(f"Error in processing: {e}")
        
        finally:
            # Видаляємо з сету файли які обробляли
            if str(file) in self.processing_files:
                self.processing_files.remove(str(file))

    # Реагує на файл який створено / добавлено
    def on_created(self, event) -> None:
        self.process_file(event.src_path)

    # Реагує на переміщення / копіювання / перейменування файлу
    def on_moved(self, event) -> None:
        print(f"File renamed: was {Path(str(event.src_path)).name} current {Path(str(event.dest_path)).name}")
        self.process_file(event.dest_path)


class MonitorManager:
    """
    Головний клас, серце моніторингу
    """
    def __init__(self, log_callback=None):
        self.observer = Observer()
        self.handler = DownloadHandler(callback_func=log_callback) 
        self.path = str(user.data.get("monitoring_path", user.default_path))
        self.is_running = False


    def start(self):
        if not self.is_running:
            fresh_data = user.load_from_json('user_data.json')
            
            is_recursive = fresh_data.get('recursive', False)
            self.path = str(fresh_data.get("monitoring_path", user.default_path))
            self.observer.schedule(self.handler, self.path, recursive=is_recursive)
            self.observer.start()
            self.is_running = True
            return "Start monitoring"


    def stop(self):
        if self.is_running:
            self.observer.stop() 
            self.observer.join() 
            # Так як обсервер одноразовий, готуємо наступний
            self.observer = Observer() 
            self.is_running = False
            return "Stop monitoring"
    
    
    def restart(self):
        self.stop()
        self.start()
        return "Restart monitoring"
