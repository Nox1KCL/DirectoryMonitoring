import json
import uuid


class User:
    def __init__(self, file_name: str) -> None:
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
    def user_id(self) -> str:
        return self.__user_data['id']


    @property
    def user_first_launch(self) -> bool:
        return self.__user_data['first_launch']
    
    @user_first_launch.setter
    def user_first_launch(self, first_launch: bool) -> None:
        self.__user_data['first_launch'] = first_launch


    @property
    def user_data(self) -> dict:
        return self.__user_data


    def configuration(self) -> tuple:
        first_launch = self.__user_data['first_launch']
        id = self.__user_data['id']
        return first_launch, id


    def load_from_json(self, file_name: str) -> dict:
        data = self.open_file(file_name)
        return data

    
    def save_to_json(self, data: dict, file_name: str) -> None:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


    def get_hwid(self) -> str:
        return str(uuid.getnode())


    def open_file(self, file_name: str) -> dict:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print("File not found")
            return dict()
        except Exception as e:
            print("Undefined error", e)
            return dict()
            
