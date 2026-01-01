import json
import uuid
from pathlib import Path
from platformdirs import user_downloads_dir, user_pictures_dir



class User:
    def __init__(self, file_name: str) -> None:
        self.downloads_path = Path(user_downloads_dir())
        self.pictures_path = Path(user_pictures_dir())

        self.__user_data = self.load_from_json(file_name)

        current_hwid = self.get_hwid()

        if self.__user_data.get('id') is None:
            self.__user_data['first_launch'] = True
            self.__user_data['id'] = current_hwid
            self.__user_data['rules'] = dict()
            self.save_to_json(self.__user_data, file_name)
            print("Пристрій зареєстровано успішно!")
        
        elif self.__user_data.get('id') != current_hwid:
            print("Помилка: Цей конфігураційний файл не належить цьому пристрою!")
            exit() 

    
    @property
    def data(self) -> dict:
        return self.__user_data


    @property
    def id(self) -> str:
        return self.__user_data['id']


    @property
    def first_launch(self) -> bool:
        return self.__user_data['first_launch']
    
    @first_launch.setter
    def first_launch(self, first_launch: bool) -> None:
        self.__user_data['first_launch'] = first_launch


    def load_from_json(self, file_name: str) -> dict:
        user_data = self.open_file(file_name)
        return user_data

    
    def save_to_json(self, data: dict, file_name: str) -> None:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    # Отримуємо унікальний айді мережевої карти ПК
    def get_hwid(self) -> str:
        return str(uuid.getnode())


    def open_file(self, file_name: str) -> dict:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                file_data = json.load(file)
                return file_data
        except FileNotFoundError:
            print("File not found")
            return dict()
        except Exception as e:
            print("Undefined error", e)
            return dict()
            
