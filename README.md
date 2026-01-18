# DirectoryMonitor (Smart File Organizer with GUI)

Десктопний додаток для автоматичної організації файлової системи в реальному часі. Програма моніторить вказані папки (наприклад, "Downloads") і миттєво сортує нові файли за категоріями (Зображення, Документи, Програми тощо) у відповідні директорії.

Проєкт поєднує сучасний GUI, системне програмування та роботу з фоновими процесами.

### 🛠 Технічні особливості (System Programming):
* **Real-time Monitoring:** Використання бібліотеки `watchdog` (Observer pattern) для миттєвої реакції на події файлової системи (створення, переміщення файлів).
* **Concurrency & Threading:** Реалізація мультипоточності для роботи графічного інтерфейсу та системного трею (System Tray) без блокування основного потоку.
* **Cross-Platform Locking:** Унікальна логіка перевірки зайнятості файлу системою (File Locking Check) з підтримкою як Windows (OS rename check), так і Linux (subprocess `lsof`).
* **Security & Integrity:** Прив'язка конфігурації до апаратного забезпечення (HWID check) через MAC-адресу для запобігання підміні конфігів.

### 📋 Функціонал:
* **Smart Sorting:** Автоматичне розпізнавання типів файлів та переміщення їх у налаштовані користувачем папки.
* **Modern GUI:** Інтерфейс на базі `CustomTkinter` із підтримкою темної/світлої теми та адаптивних налаштувань.
* **Background Mode:** Згортання в системний трей (Tray Icon) для ненав'язливої роботи у фоні.
* **Config Persistence:** Збереження налаштувань та правил сортування у JSON.

### 🚀 Stack:
* **Core:** Python 3.13
* **GUI:** CustomTkinter, Pystray (Tray), Pillow
* **System:** Watchdog, Platformdirs, Subprocess
* **Concepts:** OOP, Threading, Event-Driven Programming.

### Project Structure:
* `app/monitor.py` - Логіка Observer'а та обробка файлів.
* `app/gui.py` - Графічний інтерфейс та налаштування.
* `app/user.py` - Управління даними користувача та JSON.
