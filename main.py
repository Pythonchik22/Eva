import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup
import threading
import time
import customtkinter as ctk
import json
import math
from PIL import Image, ImageTk
import time
import threading
import requests
import pyautogui
import speech_recognition as sr
import sounddevice as sd
import webbrowser
import random
import datetime
from gtts import gTTS
import subprocess
import psutil
import ctypes
import queue
import sys
import os
import tempfile
import atexit
import logging
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# Импорт Vosk с обработкой ошибок
try:
    from vosk import Model, KaldiRecognizer

    VOSK_AVAILABLE = True
except ImportError as e:
    print(f"Vosk не установлен: {e}")
    VOSK_AVAILABLE = False

import pygame.mixer
from playsound3 import playsound

# Скрываем консольное окно Windows
if sys.platform == "win32" and hasattr(sys, "frozen"):
    import ctypes

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

audio_threads = []
pygame.mixer.init()

num_error1 = 0
num_error2 = 0

# Остальной ваш код остается без изменений до класса VoiceAssistantApp...

# Скрываем консольное окно Windows _models
if sys.platform == "win32" and hasattr(sys, "frozen"):
    import ctypes

    # Скрываем консольное окно
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

audio_threads = []
pygame.mixer.init()

num_error1 = 0
num_error2 = 0

with open('API_key', 'r', encoding='utf-8') as file:
    API = file.read()
# Список клавиш
all_pyautogui_keys = [
    'enter', 'tab', 'space', 'backspace', 'delete',
    'escape', 'shift', 'ctrl', 'alt', 'cmd',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'up', 'down', 'left', 'right',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'prtscn'
]
# Настройки Vosk
# model_path = os.path.join(resource_path("vosk-model-small-ru-0.22"))
sample_rate = 16000
audio_queue = queue.Queue()

import winreg
import os


def get_installed_apps():
    """Получает список установленных приложений из реестра Windows"""
    installed_apps = {}

    # Ключи реестра где хранятся установленные программы
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hive, path in registry_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                # Получаем имя приложения
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                # Получаем путь к исполняемому файлу
                                try:
                                    exe_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    # Очищаем путь от иконок
                                    if exe_path and ".exe" in exe_path:
                                        exe_path = exe_path.split(",")[0].strip()
                                        exe_path = exe_path.replace('"', '')
                                except:
                                    exe_path = None

                                # Получаем путь установки
                                try:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    if install_location and os.path.exists(install_location):
                                        # Ищем exe файлы в папке установки
                                        for file in os.listdir(install_location):
                                            if file.endswith('.exe') and not file.lower().startswith('unins'):
                                                exe_path = os.path.join(install_location, file)
                                                break
                                except:
                                    pass

                                if name and exe_path and os.path.exists(exe_path):
                                    # Создаем короткое имя для команды
                                    short_name = name.lower().split(' ')[0]
                                    installed_apps[short_name] = {
                                        "name": name,
                                        "command": f'"{exe_path}"',
                                        "keywords": [name.lower(), short_name]
                                    }

                            except (FileNotFoundError, OSError):
                                continue
                    except (OSError, WindowsError):
                        continue
        except (OSError, WindowsError):
            continue

    return installed_apps


def get_common_apps():
    """Основные приложения + установленные"""
    common_apps = {
        # Системные приложения
        "калькулятор": {
            "name": "Калькулятор",
            "command": "calc",
            "keywords": ["калькулятор", "посчитать", "вычислить"]
        },
        "блокнот": {
            "name": "Блокнот",
            "command": "notepad",
            "keywords": ["блокнот", "текст", "заметки", "текстовый"]
        },
        "проводник": {
            "name": "Проводник",
            "command": "explorer",
            "keywords": ["проводник", "файлы", "диск", "файловый"]
        },
        "панель управления": {
            "name": "Панель управления",
            "command": "control",
            "keywords": ["панель управления", "настройки системы"]
        },
        "диспетчер задач": {
            "name": "Диспетчер задач",
            "command": "taskmgr",
            "keywords": ["диспетчер задач", "задачи", "процессы"]
        },
        "командная строка": {
            "name": "Командная строка",
            "command": "cmd",
            "keywords": ["командная строка", "терминал", "cmd", "консоль"]
        },
        "блокнот windows": {
            "name": "Блокнот Windows",
            "command": "notepad",
            "keywords": ["блокнот windows", "редактор текста"]
        },

        # Браузеры (попробуем найти установленные)

    }

    # Добавляем установленные приложения
    try:
        installed = get_installed_apps()
        common_apps.update(installed)
    except Exception as e:
        print(f"Не удалось получить список установленных приложений: {e}")

    return common_apps

# Алгоритм Левенштейна


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


# База команд для открытия/закрытия
OPEN_COMMANDS = {
    "проводник": {
        "keywords": ["проводник", "файлы", "диск", "explorer"],
        "action": lambda: subprocess.Popen("explorer", shell=True)
    },
    "cmd": {
        "keywords": ["cmd", "командная строка", "терминал", "цмд", "command"],
        "action": lambda: os.system('cmd')
    },
    "диспетчер": {
        "keywords": ["диспетчер задач", "диспетчер", "задачи", "task manager"],
        "action": lambda: subprocess.Popen("taskmgr", shell=True)
    },
    "корзина": {
        "keywords": ["корзина", "корзину", "мусор", "recycle bin"],
        "action": lambda: os.startfile("shell:RecycleBinFolder")
    },
    "блокнот": {
        "keywords": ["блокнот", "текст", "заметки", "notepad"],
        "action": lambda: subprocess.Popen("notepad", shell=True)
    },
    "калькулятор": {
        "keywords": ["калькулятор", "посчитать", "вычислить", "calculator"],
        "action": lambda: subprocess.Popen("calc", shell=True)
    },
    "этот компьютер": {
        "keywords": ["этот компьютер", "мой компьютер", "система", "my computer"],
        "action": lambda: subprocess.Popen(['explorer', 'shell:MyComputerFolder'])
    },
    "настройки": {
        "keywords": ["настройки", "параметры", "settings", "configuration"],
        "action": lambda: subprocess.Popen(["start", "ms-settings:"], shell=True)
    },
    "youtube": {
        "keywords": ["youtube", "ютуб", "видео", "video"],
        "action": lambda: webbrowser.open("https://youtube.com")
    },
    "вк": {
        "keywords": ["вк", "вконтакте", "vk", "соцсеть"],
        "action": lambda: webbrowser.open("https://vk.com")
    },
    "rutube": {
        "keywords": ["rutube", "рутьюб", "рутуб", "видео"],
        "action": lambda: webbrowser.open("https://rutube.ru")
    }
}
CLOSE_COMMANDS = {
    "проводник": {
        "keywords": ["проводник", "файлы", "диск", "explorer"],
        "action": lambda: close_process("explorer.exe")
    },
    "cmd": {
        "keywords": ["cmd", "командная строка", "терминал", "цмд", "command"],
        "action": lambda: close_process("cmd.exe")
    },
    "диспетчер": {
        "keywords": ["диспетчер задач", "диспетчер", "задачи", "task manager"],
        "action": lambda: close_process("Taskmgr.exe")
    },
    "блокнот": {
        "keywords": ["блокнот", "текст", "заметки", "notepad"],
        "action": lambda: close_process("notepad.exe")
    },
    "калькулятор": {
        "keywords": ["калькулятор", "посчитать", "вычислить", "calculator"],
        "action": lambda: close_process("CalculatorApp.exe")
    },
    "корзина": {
        "keywords": ["корзина", "корзину", "мусор", "recycle bin"],
        "action": lambda: close_recycle_bin()
    },
    "настройки": {
        "keywords": ["настройки", "параметры", "settings", "configuration"],
        "action": lambda: close_settings_window()
    }
}


# Функция для закрытия программ
def close_process(process_name):
    closed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                proc.kill()
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not closed:
        pass


# Закрытие корзины
def close_recycle_bin():
    try:
        hwnd = ctypes.windll.user32.FindWindowW("CabinetWClass", "Корзина")
        if hwnd:
            ctypes.windll.user32.SendMessageW(hwnd, 0x0010, 0, 0)
        else:
            pass
    except Exception as e:
        pass


# Закрытие окна настроек
def close_settings_window():
    try:
        hwnd = ctypes.windll.user32.FindWindowW("Windows.UI.Core.CoreWindow", "Настройки")
        if hwnd:
            ctypes.windll.user32.SendMessageW(hwnd, 0x0010, 0, 0)
            return
    except Exception as e:
        pass
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == "SystemSettings.exe":
                proc.kill()
                return
    except Exception as e:
        pass


# Распознавание команд с алгоритмом Левенштейна
def recognize_command(text, command_dict, threshold=3, required_keywords=1):
    text_lower = text.lower()
    # Сначала проверяем точные совпадения с ключевыми словами
    for cmd_name, cmd_data in command_dict.items():
        for keyword in cmd_data["keywords"]:
            if keyword in text_lower:
                return cmd_data["action"]
    # Затем проверяем по Левенштейну с названиями команд
    for cmd_name, cmd_data in command_dict.items():
        distance = levenshtein_distance(text_lower, cmd_name)
        if distance <= threshold:
            return cmd_data["action"]
    return None


# загруж
import feedparser
from newsapi import NewsApiClient


class VolumeController:
    def __init__(self, app_instance):
        self.app = app_instance
        self.volume_interface = None
        self.initialized = False
        self.initialization_error = None
        self._initialize_volume_interface()

    def _initialize_volume_interface(self):
        """Инициализирует интерфейс управления громкостью с детальной диагностикой"""
        try:
            self.app.add_output_text("Начинаю инициализацию модуля громкости...")

            # ШАГ 0: ИНИЦИАЛИЗАЦИЯ COM (ИСПРАВЛЕНИЕ ОШИБКИ)
            self.app.add_output_text(" Инициализирую COM...")
            try:
                import pythoncom
                pythoncom.CoInitialize()
                self.app.add_output_text("COM инициализирован успешно")
            except Exception as com_error:
                self.app.add_output_text(f"COM уже инициализирован: {com_error}")

            # Шаг 1: Получаем аудиоустройства
            self.app.add_output_text("Получаю аудиоустройства...")
            devices = AudioUtilities.GetSpeakers()
            self.app.add_output_text(f" Аудиоустройства получены: {devices}")

            # Шаг 2: Активируем интерфейс
            self.app.add_output_text(" Активирую интерфейс громкости...")
            interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None
            )
            self.app.add_output_text(f"Интерфейс активирован: {interface}")

            # Шаг 3: Приводим к правильному типу
            self.app.add_output_text("Привожу интерфейс к правильному типу...")
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            self.app.add_output_text(f"Интерфейс приведен: {self.volume_interface}")

            # Шаг 4: Проверяем, что интерфейс действительно работает
            if self.volume_interface:
                self.app.add_output_text("🔍 Тестирую работу интерфейса...")
                try:
                    test_volume = self.volume_interface.GetMasterVolumeLevelScalar()
                    self.app.add_output_text(f"Тест пройден. Текущая громкость: {test_volume:.2f}")
                    self.initialized = True
                    self.app.add_output_text(" Модуль громкости инициализирован успешно!")
                except Exception as test_error:
                    self.initialized = False
                    self.initialization_error = f"Ошибка тестирования: {test_error}"
                    self.app.add_output_text(f"❌ Ошибка тестирования интерфейса: {test_error}")
            else:
                self.initialized = False
                self.initialization_error = "Интерфейс не создан"
                self.app.add_output_text("❌ Интерфейс громкости не создан")

        except Exception as e:
            self.volume_interface = None
            self.initialized = False
            self.initialization_error = str(e)
            self.app.add_output_text(f"КРИТИЧЕСКАЯ ОШИБКА инициализации громкости: {e}")
            import traceback
            self.app.add_output_text(f"Детали ошибки: {traceback.format_exc()}")

    def __del__(self):
        """Деструктор - освобождает COM ресурсы"""
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass

    def is_available(self):
        """Проверяет, доступен ли контроллер громкости"""
        return self.initialized and self.volume_interface is not None

    def get_diagnostic_info(self):
        """Возвращает диагностическую информацию"""
        info = []
        info.append(f"Инициализирован: {'Да' if self.initialized else 'Нет'}")
        info.append(f"Интерфейс создан: {'Да' if self.volume_interface else 'Нет'}")
        if self.initialization_error:
            info.append(f"Ошибка инициализации: {self.initialization_error}")

        if self.volume_interface:
            try:
                current_vol = self.volume_interface.GetMasterVolumeLevelScalar()
                info.append(f"Текущая громкость: {int(current_vol * 100)}%")
                mute_status = self.volume_interface.GetMute()
                info.append(f"Звук отключен: {'Да' if mute_status else 'Нет'}")
            except Exception as e:
                info.append(f"Ошибка получения статуса: {e}")

        return info

    def get_current_volume(self):
        """Получает текущую громкость в процентах"""
        if not self.is_available():
            return None
        try:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            return int(current_volume * 100)
        except Exception as e:
            self.app.add_output_text(f"❌ Ошибка получения громкости: {e}")
            return None

    def set_volume(self, volume_percent):
        """Устанавливает громкость в процентах (0-100)"""
        if not self.is_available():
            self.app.speak_and_live("Модуль громкости не доступен")
            return False
        try:
            volume_percent = max(0, min(100, volume_percent))
            volume_scalar = volume_percent / 100.0
            self.volume_interface.SetMasterVolumeLevelScalar(volume_scalar, None)
            self.app.add_output_text(f"Громкость установлена на {volume_percent}%")
            return True
        except Exception as e:
            self.app.add_output_text(f"❌ Ошибка установки громкости: {e}")
            return False

    def volume_up(self, step=10):
        """Увеличивает громкость на указанный шаг"""
        current_volume = self.get_current_volume()
        if current_volume is not None:
            new_volume = min(100, current_volume + step)
            return self.set_volume(new_volume)
        return False

    def volume_down(self, step=10):
        """Уменьшает громкость на указанный шаг"""
        current_volume = self.get_current_volume()
        if current_volume is not None:
            new_volume = max(0, current_volume - step)
            return self.set_volume(new_volume)
        return False

    def mute(self):
        """Отключает звук"""
        if self.is_available():
            try:
                self.volume_interface.SetMute(1, None)
                self.app.add_output_text("Звук отключен")
                return True
            except Exception as e:
                self.app.add_output_text(f"❌ Ошибка отключения звука: {e}")
        return False

    def unmute(self):
        """Включает звук"""
        if self.is_available():
            try:
                self.volume_interface.SetMute(0, None)
                self.app.add_output_text("Звук включен")
                return True
            except Exception as e:
                self.app.add_output_text(f"❌ Ошибка включения звука: {e}")
        return False

    def speak_current_volume(self):
        """Озвучивает текущую громкость"""
        current_volume = self.get_current_volume()
        if current_volume is not None:
            message = f"Текущая громкость {current_volume} процентов"
            self.app.add_output_text(f" {message}")

        else:
            self.app.speak_and_live("Не удалось определить текущую громкость")



class AdvancedNewsReader:
    def __init__(self, app_instance):
        self.app = app_instance
        self.is_reading = False
        self.stop_reading = False
        self.rss_feeds = [
            'https://lenta.ru/rss/news',
            'https://www.kommersant.ru/RSS/news.xml',
            'https://www.vedomosti.ru/rss/news',
            'https://ria.ru/export/rss2/index.xml',
            'https://tass.ru/rss/v2.xml'
        ]

    def stop_news(self):
        """Остановка чтения новостей"""
        self.stop_reading = True
        self.is_reading = False
        # НЕ вызываем stop_all_audio здесь, чтобы избежать рекурсии
        # Просто останавливаем воспроизведение напрямую
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def get_news_from_rss(self):
        """Получение новостей через RSS"""
        try:
            news_items = []

            for feed_url in self.rss_feeds:
                if self.stop_reading:
                    break

                try:
                    feed = feedparser.parse(feed_url)

                    for entry in feed.entries[:2]:
                        if self.stop_reading:
                            break

                        title = entry.title
                        description = ""

                        if hasattr(entry, 'summary'):
                            description = entry.summary
                        elif hasattr(entry, 'description'):
                            description = entry.description

                        # Очищаем описание от HTML тегов
                        import re
                        description = re.sub('<[^<]+?>', '', description)

                        news_items.append({
                            'title': title,
                            'description': description[:100] + "..." if len(description) > 100 else description,
                            'link': entry.link
                        })

                    if len(news_items) >= 3:
                        break

                except Exception as e:
                    continue

            return news_items

        except Exception as e:
            return []

    def get_simple_news(self):
        """Основной метод получения новостей"""
        self.app.add_output_text("Ищу свежие новости...")

        news_items = self.get_news_from_rss()

        if not news_items:
            self.app.add_output_text("⚠Использую тестовые новости")
            return self.get_fallback_news()

        self.app.add_output_text(f"Найдено {len(news_items)} новостей")
        return news_items[:3]

    def get_fallback_news(self):
        """Резервные новости"""
        return [
            {
                'title': 'Технологии искусственного интеллекта развиваются быстрыми темпами',
                'description': 'Нейросети находят применение в различных сферах жизни',
                'link': ''
            },
            {
                'title': 'Цифровая экономика продолжает трансформировать бизнес-процессы',
                'description': 'Компании внедряют инновационные решения для повышения эффективности',
                'link': ''
            },
            {
                'title': 'Образовательные платформы становятся более доступными',
                'description': 'Онлайн-обучение набирает популярность по всему миру',
                'link': ''
            }
        ]

    def read_news(self):
        """Чтение новостей с возможностью остановки"""
        try:
            if self.is_reading:
                return

            self.is_reading = True
            self.stop_reading = False

            news_items = self.get_simple_news()

            if not news_items or self.stop_reading:
                self.is_reading = False
                return

            # Короткое вступление
            self.app.speak_and_live(f"Вот последние новости. Всего {len(news_items)}.")

            # Ждем окончания вступления с проверкой остановки
            while self.app.is_playing_audio and not self.stop_reading:
                time.sleep(0.1)

            if self.stop_reading:
                self.is_reading = False
                return

            # Короткая пауза между вступлением и первой новостью
            time.sleep(0.5)

            # Читаем новости
            for i, news in enumerate(news_items, 1):
                if self.stop_reading:
                    break

                self.app.add_output_text(f"Новость {i}: {news['title']}")

                # Формируем текст (более краткий)
                news_text = f"{news['title']}"
                if news['description'] and len(news['description']) > 10:
                    news_text += f". {news['description']}"

                # Озвучиваем новость
                self.app.speak_and_live(news_text)

                # Ждем окончания с проверкой остановки
                while self.app.is_playing_audio and not self.stop_reading:
                    time.sleep(0.1)

                if self.stop_reading:
                    break

                # Короткая пауза между новостями (1 секунда вместо 2)
                if i < len(news_items):
                    time.sleep(1)

            if not self.stop_reading:
                # Короткое завершение
                self.app.speak_and_live("Новости завершены.")

            self.is_reading = False

        except Exception as e:
            self.is_reading = False
            self.app.add_output_text(f"❌ Ошибка: {e}")
            self.app.speak_and_live("Произошла ошибка при получении новостей")


def clean_text(text):
    """Улучшенная очистка текста от служебных токенов Llama и HTML тегов"""
    if not text:
        return ""

    import re

    # Удаляем все HTML-подобные теги
    text = re.sub(r'<[^>]+>', '', text)

    # Удаляем специальные токены Llama и другие служебные метки
    patterns_to_remove = [
        r'\[(OUT|INST|SYS)\][^]]*\]',  # [OUT], [INST], [SYS]
        r'<s>', r'</s>',  # <s> теги
        r'\[OUT\]', r'\[/OUT\]',  # [OUT] метки
        r'\[INST\]', r'\[/INST\]',  # [INST] метки
        r'<\|start_header_id\|>', r'<\|end_header_id\|>',  # специальные токены
        r'<\|eot_id\|>', r'<\|end_of_text\|>'  # специальные токены
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text)

    # Удаляем HTML entities
    html_entities = {
        '&quot;': '"', '&amp;': '&', '&lt;': '<',
        '&gt;': '>', '&nbsp;': ' ', '&#xA;': ' ', '&#xD;': ' '
    }

    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    # Удаляем повторяющиеся точки и пробелы
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\s+', ' ', text)

    # Обрезаем текст если он состоит только из тегов
    text = text.strip()
    if len(text) < 2 or text in ['<s>', '[OUT]', '[/OUT]', '[INST]']:
        return "Извините, я не поняла вопрос. Можете переформулировать?"

    return text


class VoiceAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.saved_output_text = ""
        # Настройка главного окна (пока скрытого)
        self.title("Голосовой помощник Ева")
        self.geometry("500x700")
        self.resizable(False, False)
        self.withdraw()  # Скрываем основное окно до завершения загрузки
        # Инициализация переменных голосового помощника
        self.hour = int(datetime.datetime.now().hour)
        self.mus = False
        self.recognizer = sr.Recognizer()
        self.stop_voice_assistant = False
        self.voice_thread = None
        self.vosk_thread = None
        self.stop_vosk = False
        self.current_image = None
        self.key_words = []
        # Цветовая схема (ярко-голубой и черный)
        self.custom_theme = {
            "bg_color": "black",
            "fg_color": "#1E1E1E",
            "button_color": "#00B4D8",
            "button_hover": "#0096C7",
            "text_color": "#FFFFFF",
            "frame_color": "#2A2A2A",
            "success_color": "#00B4D8",
            "error_color": "#FF5555"
        }
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # Параметры для анимации плавного покачивания
        self.wobble_active = False
        self.wobble_speed = 0.05  # Скорость изменения фазы
        self.wobble_phase = 0  # Текущая фаза анимации
        self.wobble_range = 40  # Амплитуда движения в пикселях
        self.icon_size = 150  # Размер иконки
        self.vosk_model = None
        self.vosk_loaded = False
        # Сначала показываем экран загрузки
        self.show_loading_screen()
        # Запускаем загрузку данных в отдельном потоке
        self.loading_complete = False
        threading.Thread(target=self.initialize_app, daemon=True).start()
        threading.Thread(target=self.load_vosk_model, daemon=True).start()
        # Проверяем завершение загрузки
        self.check_loading_complete()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.is_playing_audio = False  # Флаг, что воспроизводится аудио
        self.audio_start_time = 0  # Время начала воспроизведения
        self.news_reader = None
        self.hour = int(datetime.datetime.now().hour)
        self.mus = False
        self.update_loading_status("Инициализация модуля новостей...")
        self.news_reader = AdvancedNewsReader(self)  # Используем улучшенный класс
        self.available_apps = get_common_apps()
        self.app_names = list(self.available_apps.keys())
        self.volume_controller = None
        time.sleep(0.3)

    def diagnose_volume_module(self):
        """Показывает детальную диагностику модуля громкости"""
        self.add_output_text("\nДИАГНОСТИКА МОДУЛЯ ГРОМКОСТИ:")

        if not hasattr(self, 'volume_controller'):
            self.add_output_text("❌ Контроллер громкости не создан")
            return

        if self.volume_controller is None:
            self.add_output_text("❌ Контроллер громкости равен None")
            return

        # Получаем диагностическую информацию
        diagnostic_info = self.volume_controller.get_diagnostic_info()
        for info in diagnostic_info:
            self.add_output_text(f"📋 {info}")

        # Проверяем зависимости
        self.add_output_text("\nПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        try:
            import pycaw
            self.add_output_text("✅ pycaw установлен")
        except ImportError:
            self.add_output_text("❌ pycaw не установлен")

        try:
            import comtypes
            self.add_output_text("✅ comtypes установлен")
        except ImportError:
            self.add_output_text("❌ comtypes не установлен")

        # Проверяем аудиоустройства
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            self.add_output_text(f"Аудиоустройства найдены: {len(list(AudioUtilities.GetAllDevices()))} устройств")
        except Exception as e:
            self.add_output_text(f"❌ Ошибка получения аудиоустройств: {e}")

    def _is_volume_available(self):
        """Проверяет доступность модуля громкости с диагностикой"""
        if not hasattr(self, 'volume_controller'):
            self.add_output_text("❌ volume_controller атрибут не существует")
            return False

        if self.volume_controller is None:
            self.add_output_text("❌ volume_controller равен None")
            return False

        if not hasattr(self.volume_controller, 'is_available'):
            self.add_output_text("❌ метод is_available не существует")
            return False

        is_avail = self.volume_controller.is_available()

        if not is_avail:
            self.add_output_text("⚠ Модуль громкости недоступен. Запускаю диагностику...")
            self.diagnose_volume_module()

        return is_avail


    # Загрузка Vosk
    def load_vosk_model(self):
        """Загрузка модели Vosk с улучшенной обработкой ошибок"""
        try:
            if not VOSK_AVAILABLE:
                self.vosk_loaded = False
                return

            # Проверяем существование папки с моделью
            model_path = "vosk-model-small-ru-0.22"
            if not os.path.exists(model_path):
                print(f"❌ Папка с моделью Vosk не найдена: {model_path}")
                self.vosk_loaded = False
                return

            # Загружаем модель
            self.vosk_model = Model(model_path)
            self.vosk_loaded = True


        except Exception as e:
            print(f"❌ Ошибка загрузки модели Vosk: {e}")
            self.vosk_model = None
            self.vosk_loaded = False

    # Остановка голосовой ассистентки
    def safe_stop_voice_assistant(self):
        self.stop_voice_assistant = True
        self.stop_vosk = True
        if (hasattr(self, 'main_frame') and
                hasattr(self, 'output_text') and
                self.output_text.winfo_exists()):
            self.add_output_text("Голосовой помощник остановлен")

    # Обработчик закрытия приложения
    def on_closing(self):
        try:
            self.stop_all_audio()  # Останавливаем все аудио
            # Останавливаем голосового помощника
            self.stop_voice_assistant = True
            self.stop_vosk = True
            self.destroy()  # Закрываем окно
        except Exception as e:
            self.destroy()  # Все равно закрываем

    audio_threads = []

    def stop_all_audio(self):
        # Останавливаем микшер
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

        # Останавливаем все потоки воспроизведения
        global audio_threads
        audio_threads = []  # Просто очищаем список

        # Останавливаем новости БЕЗ рекурсии
        if hasattr(self, 'news_reader') and self.news_reader is not None:
            # Устанавливаем флаги напрямую, без вызова методов
            if hasattr(self.news_reader, 'stop_reading'):
                self.news_reader.stop_reading = True
            if hasattr(self.news_reader, 'is_reading'):
                self.news_reader.is_reading = False

        # Удаляем временные файлы
        self.cleanup_audio_files()

    def cleanup_audio_files(self):
        for file in os.listdir('.'):
            if file.startswith("AI_") and file.endswith(".mp3"):
                try:
                    os.remove(file)
                except:
                    pass

    def keep_alive():
        while audio_threads:
            pygame.time.Clock().tick(10)

    # Воспроизведение аудио
    def play_audio_complete(self, filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            pass
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            # Снимаем флаг через небольшую задержку
            time.sleep(0.5)
            self.is_playing_audio = False
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                pass
            if threading.current_thread() in audio_threads:
                audio_threads.remove(threading.current_thread())

    @staticmethod
    def delete_file_later(self, filename, retries=5, delay=0.5):
        for i in range(retries):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    return
            except Exception as e:
                if i == retries - 1:
                    pass
                time.sleep(delay)

    def speak_and_live(self, textai):
        try:
            # Очищаем текст перед озвучкой
            textai = clean_text(textai)  # Уберите self.

            # Устанавливаем флаг воспроизведения
            self.is_playing_audio = True
            self.audio_start_time = time.time()
            filename = f"AI_{random.randint(10000, 99999)}.mp3"
            tts = gTTS(text=textai, lang="ru")
            tts.save(filename)
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                time.sleep(0.1)
            # Запускаем воспроизведение
            thread = threading.Thread(target=self.play_audio_complete, args=(filename,))
            thread.daemon = False
            audio_threads.append(thread)
            thread.start()
        except Exception as e:
            self.is_playing_audio = False

    # Регистрируем функцию очистки при выходе
    @atexit.register
    def cleanup():
        # Останавливаем все воспроизведение
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        # Также очищаем возможные оставшиеся файлы при выходе
        time.sleep(0.2)
        for file in os.listdir():
            if file.startswith("AI_") and file.endswith(".mp3"):
                try:
                    os.remove(file)
                except Exception as e:
                    pass
        pygame.mixer.quit()

    def simple_stop_all(self):
        """Простая остановка всего без рекурсии"""
        # Останавливаем аудио напрямую
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

        # Останавливаем новости напрямую
        if hasattr(self, 'news_reader') and self.news_reader is not None:
            if hasattr(self.news_reader, 'stop_reading'):
                self.news_reader.stop_reading = True
            if hasattr(self.news_reader, 'is_reading'):
                self.news_reader.is_reading = False

        # Очищаем потоки
        global audio_threads
        audio_threads = []

    # Обрабатывает текстовую команду так же, как голосовую
    def process_command(self, text):
        with open('assistant_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Создаем список из элементов settings
        settings_list = list(data["settings"].values())
        Eva_system_prompt = settings_list[4]
        token = int(settings_list[5])
        user_name = settings_list[3]
        models = "meta-llama/llama-3-8b-instruct"
        search = "https://ya.ru/search?text="
        search_video = "https://www.youtube.com/results?search_query="
        if settings_list[0] == "Llama3":
            models = "meta-llama/llama-3-8b-instruct"
        elif settings_list[0] == "Mistral":
            models = "mistralai/mistral-7b-instruct"
        else:
            models = "meta-llama/llama-3-8b-instruct"
        if settings_list[1] == "Яндекс":
            search = "https://ya.ru/search?text="
        elif settings_list[1] == "Google":
            search = "https://google.com/search?q="
        else:
            search = "https://ya.ru/search?text="
        if settings_list[2] == "RuTube":
            search_video = "https://rutube.ru/search/?query="
        elif settings_list[2] == "YouTube":
            search_video = "https://www.youtube.com/results?search_query="
        elif settings_list[2] == "VKвидео":
            search_video = "https://vk.com/video?q="
        elif settings_list[2] == "Поисковая система":
            if settings_list[1] == "Яндекс":
                search_video = "https://yandex.ru/video/search?text="
            else:
                search_video = "https://www.google.com/search?q="
        try:
            textdef = text
            # Очищаем входящий текст от тегов
            textdef = clean_text(textdef)

            # Команда диагностики
            if "диагностика громкости" in textdef.lower() or "проверь громкость" in textdef.lower():
                self.diagnose_volume_module()
                return

            if "API=" in textdef:
                self.add_output_text(API)
                check = textdef.replace("API=", "")
                if check != "":
                    with open('API_key', 'w', encoding='utf-8') as file:
                        file.write(check)
                return

            # Обработка команд из JSON
            # В методе process_command, в разделе обработки команд из JSON:
            texts = [item['text'] for item in self.commands]
            actions = [item for item in self.commands]  # Теперь храним всю информацию

            for i, words in enumerate(texts):
                if words in textdef:
                    cmd = actions[i]
                    if cmd.get("action_type") == "key":
                        # Эмуляция нажатия клавиши
                        pyautogui.press(cmd["action_value"])
                        self.add_output_text(f"Нажата клавиша: {cmd['action_value']}")
                    else:
                        # Запуск приложения
                        app_key = cmd["action_value"]
                        if app_key in self.available_apps:
                            app_info = self.available_apps[app_key]
                            try:
                                os.system(app_info["command"])
                                self.add_output_text(f"Запущено: {app_info['name']}")
                            except Exception as e:
                                self.add_output_text(f"❌ Ошибка запуска {app_info['name']}: {e}")
                        else:
                            self.add_output_text(f"❌ Приложение '{app_key}' не найдено")
                    return
            # Приветствие
            if textdef.lower() in ["ева", "привет ева", "ева привет", "приветик ева"]:
                if 5 <= self.hour < 11:
                    pygame.mixer.music.load("utro.mp3")
                    pygame.mixer.music.play()
                elif 11 <= self.hour < 17:
                    pygame.mixer.music.load("den.mp3")
                    pygame.mixer.music.play()
                elif 17 <= self.hour <= 22:
                    pygame.mixer.music.load("vecher.mp3")
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.load("noch.mp3")
                    pygame.mixer.music.play()
                return


            if any(phrase in textdef.lower() for phrase in ["громкость", "звук"]):

                if self._is_volume_available():
                    import re
                    numbers = re.findall(r'\d+', textdef)

                    if numbers:
                        volume_value = int(numbers[0])
                        if 0 <= volume_value <= 100:
                            if self.volume_controller.set_volume(volume_value):
                                pass
                            else:
                                self.speak_and_live("Не удалось установить громкость")
                            return

                    # Если число не найдено, показываем текущую громкость
                    self.volume_controller.speak_current_volume()
                    return
                else:
                    self.add_output_text("❌ Модуль громкости не инициализирован")
                    self.speak_and_live("Модуль управления громкостью не доступен")
                return

            # Проверка на обращение к Еве
            if any(word in textdef.lower() for word in ["ева", "ево", "еву", "эва"]):
                text = textdef.lower()

                #
                if any(phrase in text for phrase in ["громкость", "звук", "volume"]):
                    if not self._is_volume_available():
                        self.add_output_text("❌ Модуль громкости не инициализирован")
                        self.speak_and_live("Модуль управления громкостью не доступен")
                        return

                    # Ищем число в команде
                    import re
                    numbers = re.findall(r'\d+', text)

                    if numbers:
                        # Установка конкретной громкости
                        volume_value = int(numbers[0])
                        if 0 <= volume_value <= 100:
                            if self.volume_controller.set_volume(volume_value):
                                pass
                            else:
                                pass
                        else:
                            pass
                        return


                    elif "громче" in text or "увеличь" in text or "добавь" in text or "больше" in text:
                        # Ищем шаг увеличения
                        step_numbers = re.findall(r'\d+', text)
                        step = int(step_numbers[0]) if step_numbers else 10

                        if self.volume_controller.volume_up(step):
                            current_volume = self.volume_controller.get_current_volume()

                        else:
                            self.speak_and_live("Не удалось увеличить громкость")
                        return

                    elif "тише" in text or "уменьши" in text or "убавь" in text or "меньше" in text:
                        # Ищем шаг уменьшения
                        step_numbers = re.findall(r'\d+', text)
                        step = int(step_numbers[0]) if step_numbers else 10

                        if self.volume_controller.volume_down(step):
                            current_volume = self.volume_controller.get_current_volume()
                            self.speak_and_live(f"Уменьшила громкость до {current_volume} процентов")
                        else:
                            self.speak_and_live("Не удалось уменьшить громкость")
                        return

                    elif "выключи звук" in text or "отключи звук" in text or "мут" in text or "без звука" in text:
                        if self.volume_controller.mute():
                            self.speak_and_live("Звук отключен")
                        else:
                            self.speak_and_live("Не удалось отключить звук")
                        return

                    elif "включи звук" in text or "унмут" in text or "со звуком" in text:
                        if self.volume_controller.unmute():
                            current_volume = self.volume_controller.get_current_volume()
                            self.speak_and_live(f"Звук включен, громкость {current_volume} процентов")
                        else:
                            self.speak_and_live("Не удалось включить звук")
                        return

                    elif "какая громкость" in text or "текущая громкость" in text:
                        self.volume_controller.speak_current_volume()
                        return

                    else:
                        # Если просто сказали "громкость" без параметров
                        self.volume_controller.speak_current_volume()
                        return

                # Команда остановки новостей
                if any(phrase in text for phrase in
                       ["стоп новости", "останови новости", "хватит новостей", "перестань читать новости"]):
                    if hasattr(self, 'news_reader') and self.news_reader is not None:
                        self.news_reader.stop_news()
                        self.add_output_text("Команда остановки новостей получена")
                        self.speak_and_live("Останавливаю чтение новостей")
                    return

                # Команда чтения новостей
                if any(phrase in text for phrase in
                       ["что нового", "новости", "расскажи новости", "свежие новости", "последние новости"]):
                    self.add_output_text("Получена команда: чтение новостей")
                    if hasattr(self, 'news_reader') and self.news_reader is not None:
                        self.add_output_text("Модуль новостей доступен, запускаю...")
                        news_thread = threading.Thread(target=self.news_reader.read_news, daemon=True)
                        news_thread.start()
                    else:
                        self.add_output_text("❌ Модуль новостей не инициализирован")
                        self.speak_and_live("Извините, модуль новостей временно не доступен")
                    return

                # Общая команда стоп
                if "стоп" in text.lower() or "выход" in text.lower() or "заверши" in text.lower():
                    self.stop_all_audio()
                    if hasattr(self, 'news_reader') and self.news_reader is not None:
                        self.news_reader.stop_news()
                    return

                # Открытие программ
                if any(prefix in text for prefix in ["открой", "открыть", "запусти", "включи"]):
                    action = recognize_command(text, OPEN_COMMANDS, threshold=4, required_keywords=1)
                    if action:
                        self.add_output_text(f"Открываю: {text}")
                        try:
                            action()
                            self.add_output_text("Успешно открыто")
                        except Exception as e:
                            self.add_output_text(f"❌ Ошибка при открытии: {e}")
                    else:
                        self.add_output_text("Что я должна открыть?")
                    return

                # Закрытие программ
                if any(prefix in text for prefix in ["закрой", "закрыть", "выключи", "останови"]):
                    action = recognize_command(text, CLOSE_COMMANDS, threshold=4, required_keywords=1)
                    if action:
                        self.add_output_text(f"Закрываю: {text}")
                        try:
                            action()
                            self.add_output_text("Успешно закрыто")
                        except Exception as e:
                            self.add_output_text(f"❌ Ошибка при закрытии: {e}")
                    else:
                        self.add_output_text("Что я должна закрыть?")
                    return

                if "сколько времени" in text or "который час" in text or "время" in text:
                    current_time = datetime.datetime.now().strftime("%H:%M")
                    if current_time == "20:31":
                        playsound("pribyl-godzho-satoru.mp3")
                    else:
                        time_text = f"Сейчас {current_time}"
                        self.add_output_text(f"{time_text}")
                        self.speak_and_live(f'Сейчас {current_time}')
                    return

                # Поиск информации
                if "найди" in text.lower() or "найти" in text.lower() or "поиск" in text.lower():
                    try:
                        if "видео" in text.lower() or "клип" in text.lower() or "фильм" in text.lower() or "сериал" in text.lower():
                            video_promt = text.replace("поиск", "")
                            video_promt = video_promt.replace("в интернете", "")
                            video_promt = video_promt.replace("в инете", "")
                            video_promt = video_promt.replace("ева", "")
                            video_promt = video_promt.replace("найди", "")
                            if search_video == "https://www.google.com/search?q=":
                                webbrowser.open(f"https://www.google.com/search?q={video_promt}&tbm=vid")
                            else:
                                webbrowser.open(search_video + video_promt)
                            return
                        else:
                            query = text.replace("найди", "").replace("найти", "").replace("поиск", "")
                            query = query.replace("ева", "").replace("интернете", "").replace("инете", "").strip()
                            if query:
                                try:
                                    webbrowser.open(f"{search}{query}")
                                    self.add_output_text(f"Ищу в интернете: {query}")
                                except:
                                    pass
                    except Exception as e:
                        self.add_output_text(f"❌ Ошибка поиска: {e}")
                    return

                # Общение с ИИ
                else:
                    try:
                        prompt = text.replace("ева", "").strip()
                        if not prompt:
                            return

                        sysprompt = (
                                Eva_system_prompt + 'Ты-голосовая ассистентка Ева, разработанная Замотаевым Артёмом ' +
                                'Меня зовут ' + user_name + 'Отвечай максимально кратко и на русском языке. ' +
                                'НЕ используй HTML теги в ответе. Отвечай чистым текстом без <s>, [OUT] и других разметок.')
                        system_prompt = {
                            "role": "system",
                            "content": sysprompt
                        }
                        messages = [
                            system_prompt,
                            {"role": "user", "content": prompt}
                        ]

                        # Подготовка запроса к ИИ
                        url = "https://openrouter.ai/api/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {API}",
                            "HTTP-Referer": "https://github.com/your-username/your-repo",
                            "Content-Type": "application/json"
                        }
                        response = requests.post(
                            url,
                            headers=headers,
                            json={
                                "model": models,
                                "messages": messages,
                                "max_tokens": int(token)
                            }
                        )

                        if response.status_code == 200:
                            otvet = response.json()["choices"][0]["message"]["content"]
                            # ОЧИЩАЕМ ОТВЕТ ОТ ТЕГОВ
                            otvet = clean_text(otvet)
                            self.add_output_text(f"Ева: {otvet}")
                            # Озвучивание ответа
                            self.speak_and_live(otvet)
                        else:
                            self.add_output_text(f"❌ Ошибка API: {response.status_code}")
                            pygame.mixer.music.load("internet.mp3")
                            pygame.mixer.music.play()

                    except requests.exceptions.RequestException:
                        self.add_output_text("❌ Проверьте подключение к интернету")
                        pygame.mixer.music.load("internet.mp3")
                        pygame.mixer.music.play()
                    except Exception as e:
                        self.add_output_text(f"❌ Ошибка при обращении к ИИ: {e}")

        except Exception as e:
            self.add_output_text(f"❌ Ошибка обработки команды: {e}")

    # Прослушивание ключевых слов
    def listen_keywords(self):
        """Функция Vosk для прослушивания ключевых слов"""
        try:
            # Ждем загрузки модели (максимум 30 секунд)
            timeout = 20
            start_time = time.time()
            while not self.vosk_loaded and not self.stop_vosk:
                if time.time() - start_time > timeout:
                    self.add_output_text("❌ Таймаут загрузки модели Vosk")
                    return
                time.sleep(0.1)  # Ждем 100мс
            '''if self.vosk_model is None:
                self.add_output_text("❌ Модель Vosk не загружена")
                return'''
            recognizer = KaldiRecognizer(self.vosk_model, sample_rate)
            recognizer.SetWords(True)

            def audio_callback(indata, frames, time, status):
                if status:
                    pass
                audio_queue.put(bytes(indata))

            with sd.RawInputStream(samplerate=sample_rate,
                                   blocksize=8000,
                                   dtype='int16',
                                   channels=1,
                                   callback=audio_callback):
                while not self.stop_vosk:
                    data = audio_queue.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '').strip()
                        if text and any(word in text for word in self.key_words):
                            self.add_output_text(f"\nРаспознано: {text}")
                            self.handle_keyword(text)
        except Exception as e:
            self.add_output_text(f"❌ Ошибка в потоке Vosk: {e}")

    # Обработка ключевых слов
    def handle_keyword(self, keyword):
        self.add_output_text(f"Обрабатываю ключевое слово: {keyword}")

    # Экран загрузки
    def show_loading_screen(self):
        self.loading_window = ctk.CTkToplevel(self)
        self.loading_window.title("Загрузка...")
        self.loading_window.geometry("500x700")
        self.loading_window.resizable(False, False)
        self.loading_window.overrideredirect(True)
        # Центрируем окно загрузки
        self.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry(f'+{x}+{y}')
        # Содержимое экрана загрузки
        loading_frame = ctk.CTkFrame(
            self.loading_window,
            fg_color=self.custom_theme["bg_color"]
        )
        loading_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Логотип
        try:
            icon = ctk.CTkImage(
                light_image=Image.open("logo.png").resize((80, 80)),
                dark_image=Image.open("logo.png").resize((80, 80)),
                size=(80, 80)
            )
            ctk.CTkLabel(
                loading_frame,
                image=icon,
                text=""
            ).pack(pady=10)
        except:
            ctk.CTkLabel(
                loading_frame,
                text="Ева",
                font=("Arial", 24, "bold"),
                text_color=self.custom_theme["button_color"]
            ).pack(pady=10)
        # Название приложения
        ctk.CTkLabel(
            loading_frame,
            text="Голосовой помощник",
            font=("Arial", 16),
            text_color=self.custom_theme["text_color"]
        ).pack()
        # Прогресс бар
        self.loading_progress = ctk.CTkProgressBar(
            loading_frame,
            mode="indeterminate",
            height=4,
            width=200,
            progress_color=self.custom_theme["button_color"]
        )
        self.loading_progress.pack(pady=20)
        self.loading_progress.start()
        # Статус загрузки
        self.loading_status = ctk.CTkLabel(
            loading_frame,
            text="Загрузка данных...",
            text_color=self.custom_theme["text_color"]
        )
        self.loading_status.pack()

    def update_loading_status(self, text):
        if hasattr(self, 'loading_status'):
            self.loading_status.configure(text=text)
            self.loading_window.update()

    def initialize_app(self):
        try:
            # Имитация загрузки
            self.update_loading_status("Загрузка интерфейса...")
            time.sleep(0.2)

            # Основные настройки
            self.main_frame = ctk.CTkFrame(self, fg_color=self.custom_theme["bg_color"])
            self.main_frame.pack(fill="both", expand=True)

            # Загрузка данных
            self.update_loading_status("Загрузка данных...")
            self.data_file = "assistant_data.json"
            self.commands = []
            self.settings = {}
            self.command_widgets = []
            self.load_data()
            time.sleep(0.3)

            # Инициализация модуля громкости - УЛУЧШЕННАЯ ВЕРСИЯ
            self.update_loading_status("Инициализация модуля громкости...")
            self.update_loading_status("Инициализация модуля громкости...")
            try:
                self.add_output_text("Создаю контроллер громкости...")
                self.volume_controller = VolumeController(self)

                # Ждем завершения инициализации
                time.sleep(0.5)

                if self.volume_controller.is_available():
                    current_vol = self.volume_controller.get_current_volume()
                    self.add_output_text(f"Модуль громкости готов. Текущая громкость: {current_vol}%")
                else:
                    self.add_output_text("❌ Модуль громкости не инициализирован")
                    # Сразу показываем диагностику
                    self.diagnose_volume_module()

            except Exception as e:
                self.add_output_text(f"ОШИБКА создания контроллера громкости: {e}")
                import traceback
                self.add_output_text(f"Stack trace: {traceback.format_exc()}")
                self.volume_controller = None

            time.sleep(0.3)

            # Инициализация модуля новостей
            self.update_loading_status("Инициализация модуля новостей...")
            self.news_reader = AdvancedNewsReader(self)
            time.sleep(0.2)

            # Загрузка ключевых слов для Vosk
            self.key_words = [item['text'] for item in self.commands]

            # Загрузка иконки
            self.update_loading_status("Загрузка ресурсов...")
            self.load_icon()
            time.sleep(0.1)

            # Завершение загрузки
            self.loading_complete = True
            self.add_output_text("Модуль новостей готов к работе")
            self.add_output_text("Модуль громкости готов к работе")

        except Exception as e:
            self.loading_complete = True
            print(f"Ошибка инициализации: {e}")

    def check_loading_complete(self):
        if self.loading_complete:
            self.loading_progress.stop()
            self.loading_window.destroy()
            self.deiconify()
            self.show_main_screen()
        else:
            self.after(100, self.check_loading_complete)

    # Добавление текста на главный экран
    def add_output_text(self, text):
        # Проверяем, существует ли виджет
        if not hasattr(self, 'output_text') or not self.output_text.winfo_exists():
            return
        try:
            self.output_text.configure(state="normal")
            self.output_text.insert("end", text + "\n")
            self.output_text.see("end")
            self.output_text.configure(state="disabled")
            # Сохраняем весь текущий текст
            self.saved_output_text = self.output_text.get("1.0", "end-1c")
        except Exception as e:
            pass

    def load_icon(self):
        """Загружает иконку для анимации"""
        try:
            image_path = "logo.png"

            # Проверяем существование файла
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Файл {image_path} не существует")

            self.original_image = Image.open(image_path).convert("RGBA")
            # Масштабируем
            self.base_image = self.original_image.resize(
                (self.icon_size, self.icon_size),
                Image.LANCZOS
            )
            self.current_image = ctk.CTkImage(
                light_image=self.base_image,
                dark_image=self.base_image,
                size=(self.icon_size, self.icon_size)
            )


        except Exception as e:

            # Создаем простую цветную заглушку вместо пустого изображения
            placeholder = Image.new(
                "RGBA",
                (self.icon_size, self.icon_size),
                (0, 180, 216, 255)  # Синий цвет
            )
            self.current_image = ctk.CTkImage(
                light_image=placeholder,
                dark_image=placeholder,
                size=(self.icon_size, self.icon_size)
            )

    # Запуск анимации покачивания
    def start_wobble(self):
        if not self.wobble_active:
            self.wobble_active = True
            self.wobble_phase = 0
            self.update_wobble()

    # Остановка покачивания
    def stop_wobble(self):
        self.wobble_active = False

    # Обнавление анимации покачивания
    def update_wobble(self):
        if not self.wobble_active:
            return
        try:
            # Увеличиваем фазу для плавного движения
            self.wobble_phase += self.wobble_speed
            # Рассчитываем текущее смещение по синусоиде
            current_offset = math.sin(self.wobble_phase) * self.wobble_range
            # Обновляем позицию иконки
            if hasattr(self, 'icon_label') and self.icon_label.winfo_exists():
                self.icon_label.place(x=250 - self.icon_size // 2 + current_offset,
                                      y=115)
            # Планируем следующий кадр
            self.after(30, self.update_wobble)
        except Exception as e:
            self.wobble_active = False

    # Загрузка данных из JSON файла
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.commands = data.get("commands", [])
                    self.settings = data.get("settings", {})
        except Exception as e:
            self.commands = []
            self.settings = {}
            self.save_data()

    # Сохранение данных в JSON файл
    def save_data(self):
        data = {
            "commands": self.commands,
            "settings": self.settings
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        if hasattr(self, 'icon_label'):
            self.icon_label = None

    # Запуск голосовой ассистентки
    def start_voice_assistant(self):
        if self.voice_thread and self.voice_thread.is_alive():
            return
        self.stop_voice_assistant = False
        self.stop_vosk = False
        # Запускаем Vosk для ключевых слов
        self.vosk_thread = threading.Thread(target=self.listen_keywords, daemon=True)
        self.vosk_thread.start()
        # Запускаем основной голосовой помощник
        self.voice_thread = threading.Thread(target=self.voice_assistant_loop, daemon=True)
        self.voice_thread.start()
        self.add_output_text("Голосовой помощник запущен...")

    # Остановка голосовой ассисстентки
    def stop_voice_assistant_thread(self):
        self.stop_voice_assistant = True
        self.stop_vosk = True
        # Проверяем, существует ли output_text перед обращением к нему
        if hasattr(self, 'output_text') and self.output_text.winfo_exists():
            self.add_output_text("Голосовой помощник остановлен")
        else:
            pass

    # Основной цикл
    def voice_assistant_loop(self):
        try:
            while not self.stop_voice_assistant:
                try:
                    # Пропускаем распознавание если идет воспроизведение аудио
                    if self.is_playing_audio:
                        time.sleep(0.1)
                        continue

                    # Визуальная индикация прослушивания (опционально)
                    # self.add_output_text("🎤 Слушаю...")

                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                    textdef = self.recognizer.recognize_google(audio, language='ru-RU').lower()

                    # ВЫВОДИМ РАСПОЗНАННЫЙ ТЕКСТ В ПАНЕЛЬ
                    self.add_output_text(f"Вы: {textdef}")

                    # Обрабатываем команду
                    self.process_command(textdef)

                except sr.UnknownValueError:
                    # Можно добавить сообщение о нераспознанной речи
                    pass
                except sr.RequestError as e:
                    self.add_output_text(f"❌ Ошибка сервиса распознавания: {e}")
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    self.add_output_text(f"❌ Ошибка распознавания: {repr(e)}")
        except Exception as e:
            self.add_output_text(f"❌ Критическая ошибка в голосовом помощнике: {e}")

    # Главный экран
    def show_main_screen(self):
        self.clear_screen()
        # Создаем Label для иконки
        self.icon_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            image=self.current_image
        )
        self.icon_label.pack(pady=(20, 10))
        # Запускаем анимацию покачивания
        self.start_wobble()

        # Проверяем состояние модулей
        if hasattr(self, 'volume_controller') and self.volume_controller is not None:
            if self.volume_controller.is_available():
                self.add_output_text("Модуль громкости готов")
            else:
                self.add_output_text("Модуль громкости недоступен")
        else:
            self.add_output_text("❌ Модуль громкости не инициализирован")

        # Текстовое окно для вывода
        self.output_text = ctk.CTkTextbox(
            self.main_frame,
            height=270,
            width=500,
            wrap="word",
            fg_color=self.custom_theme["frame_color"],
            font=("Arial", 12),
            scrollbar_button_color=self.custom_theme["button_color"]
        )
        self.output_text.pack(pady=(300, 0), padx=20, fill="x")
        self.output_text.configure(state="disabled")


        # Восстанавливаем сохраненный текст, если он есть
        if hasattr(self, 'saved_output_text'):
            self.output_text.configure(state="normal")
            self.output_text.insert("end", self.saved_output_text)
            self.output_text.configure(state="disabled")
        # Создаем контейнер для нижней части
        bottom_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_container.pack(side="bottom", fill="x", pady=(0, 40))
        # Строка ввода
        self.input_entry = ctk.CTkEntry(
            bottom_container,
            placeholder_text="Введите команду...",
            width=460
        )
        self.input_entry.pack(pady=(15, 15))
        self.input_entry.bind("<Return>", self.process_input)
        # Нижняя панель с кнопками
        bottom_panel = ctk.CTkFrame(
            bottom_container,
            height=60,
            fg_color=self.custom_theme["bg_color"]
        )
        bottom_panel.pack(side="bottom", fill="x")
        # Контейнер для кнопок
        button_container = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        button_container.pack(expand=True)
        # Кнопка "Настройки"
        ctk.CTkButton(
            button_container,
            text="Настройки",
            width=120,
            fg_color=self.custom_theme["button_color"],
            hover_color=self.custom_theme["button_hover"],
            command=self.show_settings_screen
        ).pack(side="left", padx=5)
        # Кнопка "Команды"
        ctk.CTkButton(
            button_container,
            text="Команды",
            width=120,
            fg_color=self.custom_theme["button_color"],
            hover_color=self.custom_theme["button_hover"],
            command=self.show_commands_screen
        ).pack(side="left", padx=5)
        # Запускаем голосового помощника автоматически при открытии главного экрана
        self.start_voice_assistant()

    # Обработка ввода пользователя
    def process_input(self, event=None):
        text = self.input_entry.get().strip()
        if not text:
            return
        # Добавляем текст в текстовое окно
        self.add_output_text(f"Вы: {text}")
        self.input_entry.delete(0, 'end')
        # Обрабатываем команду так же, как голосовой ввод
        self.process_command(text)

    # Экран настроек
    def show_settings_screen(self):
        self.stop_wobble()
        # Останавливаем ассистентку без вывода сообщения в виджет
        self.stop_voice_assistant = True
        self.stop_vosk = True
        self.clear_screen()
        # Кнопка "Назад"
        back_button = ctk.CTkButton(
            self.main_frame,
            text="← Назад",
            width=60,
            fg_color="transparent",
            hover_color="#2E2E2E",
            text_color=self.custom_theme["button_color"],
            command=self.show_main_screen
        )
        back_button.place(x=10, y=10)
        # Заголовок
        ctk.CTkLabel(
            self.main_frame,
            text="Настройки",
            font=("Arial", 20, "bold"),
            text_color=self.custom_theme["text_color"]
        ).pack(pady=20)
        # Основной контейнер
        settings_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.custom_theme["frame_color"]
        )
        settings_frame.pack(fill="x", padx=20, pady=10)
        # 1. Выпадающий список
        ctk.CTkLabel(settings_frame, text="Модель GPT:").grid(row=0, column=0, sticky="w", pady=5)
        self.setting_combo1 = ctk.CTkComboBox(
            settings_frame,
            values=["Mistral", "Llama3"],
            fg_color=self.custom_theme["frame_color"],
            button_color=self.custom_theme["button_color"]
        )
        self.setting_combo1.grid(row=0, column=1, sticky="ew", padx=10)
        # 2. Выпадающий список
        ctk.CTkLabel(settings_frame, text="Поисковая система").grid(row=1, column=0, sticky="w", pady=5)
        self.setting_combo2 = ctk.CTkComboBox(
            settings_frame,
            values=["Яндекс", "Google"],
            fg_color=self.custom_theme["frame_color"],
            button_color=self.custom_theme["button_color"]
        )
        self.setting_combo2.grid(row=1, column=1, sticky="ew", padx=10)
        # 3. Выпадающий список
        ctk.CTkLabel(settings_frame, text="Источник поиска видео").grid(row=2, column=0, sticky="w", pady=5)
        self.setting_combo3 = ctk.CTkComboBox(
            settings_frame,
            values=["RuTube", "YouTube", "VKвидео", "Поисковая система"],
            fg_color=self.custom_theme["frame_color"],
            button_color=self.custom_theme["button_color"]
        )
        self.setting_combo3.grid(row=2, column=1, sticky="ew", padx=10)
        # 4. Однострочное поле ввода
        ctk.CTkLabel(settings_frame, text="Ваше имя").grid(row=3, column=0, sticky="w", pady=5)
        self.setting_entry = ctk.CTkEntry(settings_frame)
        self.setting_entry.grid(row=3, column=1, sticky="ew", padx=10)
        # 5. Многострочное поле ввода
        ctk.CTkLabel(settings_frame, text="Промт ассистента").grid(row=4, column=0, sticky="w", pady=5)
        self.setting_textbox = ctk.CTkTextbox(settings_frame, height=80)
        self.setting_textbox.grid(row=4, column=1, sticky="ew", padx=10)
        # 6. Числовое поле
        ctk.CTkLabel(settings_frame, text="Кол-во символов в ответе").grid(row=6, column=0, sticky="w", pady=5)
        self.setting_spinbox = ctk.CTkEntry(settings_frame, placeholder_text="50")
        self.setting_spinbox.grid(row=6, column=1, sticky="ew", padx=10)
        settings_frame.columnconfigure(1, weight=1)
        # Восстановление сохраненных настроек
        if self.settings:
            self.setting_combo1.set(self.settings.get("gpt_models", "Llama3"))
            self.setting_combo2.set(self.settings.get("search_system", "Яндекс"))
            self.setting_combo3.set(self.settings.get("search_video", "RuTube"))
            self.setting_entry.insert(0, self.settings.get("name", "Артём"))
            self.setting_textbox.insert("1.0", self.settings.get("your_message", "Отвечай вежливо."))
            self.setting_spinbox.insert(0, self.settings.get("tokens", "50"))
        # Кнопка сохранения
        save_button = ctk.CTkButton(
            self.main_frame,
            text="Сохранить настройки",
            fg_color=self.custom_theme["button_color"],
            hover_color=self.custom_theme["button_hover"],
            command=self.save_settings
        )
        save_button.pack(pady=10)

    # Сохранение настроек
    def save_settings(self):
        self.settings = {
            "gpt_models": self.setting_combo1.get(),
            "search_system": self.setting_combo2.get(),
            "search_video": self.setting_combo3.get(),
            "name": self.setting_entry.get(),
            "your_message": self.setting_textbox.get("1.0", "end-1c"),
            "tokens": self.setting_spinbox.get()
        }
        self.save_data()
        # Сообщение об успехе
        success_label = ctk.CTkLabel(
            self.main_frame,
            text="Настройки сохранены!",
            text_color=self.custom_theme["success_color"]
        )
        success_label.pack(pady=5)
        self.after(2000, self.show_settings_screen)

    # Экран управления командами

    def show_commands_screen(self):
        self.stop_wobble()
        self.clear_screen()
        self.command_widgets = []
        self.selected_commands = []  # Список выбранных команд для удаления

        # Кнопка "Назад"
        back_button = ctk.CTkButton(
            self.main_frame,
            text="← Назад",
            width=60,
            fg_color="transparent",
            hover_color="#2E2E2E",
            text_color=self.custom_theme["button_color"],
            command=self.show_main_screen
        )
        back_button.place(x=10, y=10)

        # Заголовок
        ctk.CTkLabel(
            self.main_frame,
            text="Управление командами",
            font=("Arial", 20, "bold"),
            text_color=self.custom_theme["text_color"]
        ).pack(pady=20)

        # Подзаголовок с объяснением
        ctk.CTkLabel(
            self.main_frame,
            text="Выберите 'Клавиши' для эмуляции нажатия клавиш или 'Приложения' для запуска программ",
            font=("Arial", 12),
            text_color=self.custom_theme["button_color"],
            wraplength=400
        ).pack(pady=(0, 10))

        # Основной контейнер
        commands_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=self.custom_theme["frame_color"]
        )
        commands_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Восстановление команд
        for cmd in self.commands:
            action_type = cmd.get("action_type", "key")
            action_value = cmd.get("action_value", "enter")
            self._create_command_row(commands_frame, cmd["text"], action_type, action_value)

        # Нижняя панель
        bottom_panel = ctk.CTkFrame(
            self.main_frame,
            height=80,
            fg_color=self.custom_theme["bg_color"]
        )
        bottom_panel.pack(side="bottom", fill="x", pady=10)

        # Разделительная линия
        ctk.CTkFrame(
            bottom_panel,
            height=2,
            fg_color=self.custom_theme["button_color"]
        ).pack(fill="x", pady=5)

        # Контейнер для кнопок
        buttons_container = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        buttons_container.pack(fill="x", padx=10, pady=5)

        # Левый блок - счетчик и кнопка удаления
        left_buttons = ctk.CTkFrame(buttons_container, fg_color="transparent")
        left_buttons.pack(side="left", fill="x", expand=True)

        # Счетчик команд
        self.commands_counter = ctk.CTkLabel(
            left_buttons,
            text=f"Всего команд: {len(self.commands)}",
            text_color=self.custom_theme["text_color"]
        )
        self.commands_counter.pack(side="left", padx=5)

        # Кнопка "Удалить выбранные"
        self.delete_selected_button = ctk.CTkButton(
            left_buttons,
            text="Удалить",
            width=140,
            fg_color="#FF5555",
            hover_color="#CC0000",
            command=self._delete_selected_commands
        )
        self.delete_selected_button.pack(side="left", padx=10)
        self.delete_selected_button.configure(state="disabled")  # Изначально неактивна

        # Правый блок - кнопки сохранения и добавления
        right_buttons = ctk.CTkFrame(buttons_container, fg_color="transparent")
        right_buttons.pack(side="right")

        # Кнопка "Сохранить"
        save_button = ctk.CTkButton(
            right_buttons,
            text="Сохранить",
            width=100,
            fg_color=self.custom_theme["button_color"],
            hover_color=self.custom_theme["button_hover"],
            command=self._save_commands
        )
        save_button.pack(side="left", padx=5)

        # Кнопка "Добавить"
        add_button = ctk.CTkButton(
            right_buttons,
            text="Добавить",
            width=100,
            fg_color=self.custom_theme["button_color"],
            hover_color=self.custom_theme["button_hover"],
            command=lambda: self._add_command_row(commands_frame)
        )
        add_button.pack(side="left", padx=5)

    def _save_commands(self):
        self.commands = []
        for widget in self.command_widgets:
            self.commands.append({
                "text": widget["entry"].get(),
                "action": widget["combo"].get()
            })
        self.save_data()
        # Сообщение об успехе
        success_label = ctk.CTkLabel(
            self.main_frame,
            text="Команды сохранены!",
            text_color=self.custom_theme["success_color"]
        )
        success_label.pack(pady=5)
        self.after(2000, success_label.destroy)
        # Обновляем счетчик
        self._update_counter()

    # Создание новой команды
    def _create_command_row(self, parent_frame, text="", action_type="key", action_value="enter"):
        row_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=self.custom_theme["frame_color"],
            height=35
        )
        row_frame.pack(fill="x", pady=2)

        # Чекбокс для выбора команды
        checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=checkbox_var,
            width=18,
            height=18,
            command=lambda: self._update_selection(checkbox_var, row_frame)
        )
        checkbox.pack(side="left", padx=3)

        # Поле ввода команды
        entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Команда...",
            fg_color=self.custom_theme["frame_color"],
            width=130,
            height=28
        )
        entry.insert(0, text)
        entry.pack(side="left", padx=3)

        # Первый выпадающий список - тип действия
        type_combo = ctk.CTkComboBox(
            row_frame,
            values=["Клавиши", "Приложения"],
            width=130,
            height=28,
            fg_color=self.custom_theme["frame_color"],
            button_color=self.custom_theme["button_color"],
            dropdown_fg_color=self.custom_theme["frame_color"]
        )
        type_combo.set("Клавиши" if action_type == "key" else "Приложения")
        type_combo.pack(side="left", padx=3)

        # Второй выпадающий список - конкретное действие
        action_combo = ctk.CTkComboBox(
            row_frame,
            values=all_pyautogui_keys,  # по умолчанию клавиши
            width=130,
            height=28,
            fg_color=self.custom_theme["frame_color"],
            button_color=self.custom_theme["button_color"],
            dropdown_fg_color=self.custom_theme["frame_color"]
        )

        # Функция для форматирования названий приложений
        def format_app_names(apps_list):
            formatted_names = []
            for app_name in apps_list:
                # Делаем первую букву заглавной, остальные - строчными
                formatted = app_name.capitalize()
                # Особые случаи для аббревиатур и составных названий
                special_cases = {
                    '7zip': '7-Zip',
                    'notepad++': 'Notepad++',
                    'vlc': 'VLC',
                    'cmd': 'CMD',
                    'vk': 'VK',
                    'youtube': 'YouTube',
                    'rutube': 'Rutube',
                    'google chrome': 'Google Chrome',
                    'microsoft edge': 'Microsoft Edge',
                    'mozilla firefox': 'Mozilla Firefox',
                    'microsoft word': 'Microsoft Word',
                    'microsoft excel': 'Microsoft Excel',
                    'microsoft powerpoint': 'Microsoft PowerPoint',
                    'adobe photoshop': 'Adobe Photoshop',
                    'adobe reader': 'Adobe Reader',
                    'visual studio code': 'Visual Studio Code',
                    'pycharm': 'PyCharm',
                    'intellij idea': 'IntelliJ IDEA',
                    'android studio': 'Android Studio',
                    'node.js': 'Node.js',
                    'git-bash': 'Git Bash',
                    'postman': 'Postman',
                    'blender': 'Blender',
                    'unreal engine': 'Unreal Engine',
                    'obs': 'OBS',
                    'camtasia': 'Camtasia',
                    'premiere pro': 'Premiere Pro',
                    'after effects': 'After Effects',
                    'cinema 4d': 'Cinema 4D',
                    '3ds max': '3ds Max',
                    'maya': 'Maya',
                    'zbrush': 'ZBrush',
                    'substance painter': 'Substance Painter',
                    'marvelous designer': 'Marvelous Designer',
                    'clip studio paint': 'Clip Studio Paint',
                    'paint tool sai': 'Paint Tool SAI'
                }
                # Если есть специальное форматирование - используем его
                if app_name in special_cases:
                    formatted = special_cases[app_name]
                formatted_names.append(formatted)
            return formatted_names

        # Получаем отформатированные названия приложений
        formatted_app_names = format_app_names(self.app_names)

        # Создаем словарь для связи отформатированных названий с оригинальными ключами
        self.app_name_mapping = {}
        for original, formatted in zip(self.app_names, formatted_app_names):
            self.app_name_mapping[formatted] = original

        # Устанавливаем значение по умолчанию
        if action_type == "key":
            action_combo.set(action_value)
        else:
            # Для приложений используем отформатированное название
            if action_value in self.app_names:
                formatted_value = format_app_names([action_value])[0]
                action_combo.set(formatted_value)
            else:
                action_combo.set(formatted_app_names[0] if formatted_app_names else "Калькулятор")

        action_combo.pack(side="left", padx=3)

        # Обработчик изменения типа действия
        def on_type_change(event):
            selected_type = type_combo.get()
            if selected_type == "Клавиши":
                action_combo.configure(values=all_pyautogui_keys)
                if action_combo.get() not in all_pyautogui_keys:
                    action_combo.set("enter")
            else:  # Приложения
                action_combo.configure(values=formatted_app_names)
                current_value = action_combo.get()
                if current_value not in formatted_app_names:
                    action_combo.set(formatted_app_names[0] if formatted_app_names else "Калькулятор")

        type_combo.configure(command=on_type_change)

        # Сохраняем ссылки на виджеты
        widget_data = {
            "frame": row_frame,
            "entry": entry,
            "type_combo": type_combo,
            "action_combo": action_combo,
            "checkbox": checkbox,
            "checkbox_var": checkbox_var
        }
        self.command_widgets.append(widget_data)

    def _update_selection(self, checkbox_var, row_frame):
        """Обновляет список выбранных команд"""
        if checkbox_var.get():
            # Добавляем в выбранные
            if row_frame not in self.selected_commands:
                self.selected_commands.append(row_frame)
                # Подсвечиваем выбранную строку
                row_frame.configure(fg_color="#3A3A3A")
        else:
            # Убираем из выбранных
            if row_frame in self.selected_commands:
                self.selected_commands.remove(row_frame)
                # Возвращаем обычный цвет
                row_frame.configure(fg_color=self.custom_theme["frame_color"])

        # Активируем/деактивируем кнопку удаления
        if hasattr(self, 'delete_selected_button'):
            if self.selected_commands:
                self.delete_selected_button.configure(state="normal")
            else:
                self.delete_selected_button.configure(state="disabled")

    def _delete_selected_commands(self):
        """Удаляет выбранные команды"""
        if not self.selected_commands:
            return

        # Подтверждение удаления
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Подтверждение удаления")
        confirm_window.geometry("300x150")
        confirm_window.resizable(False, False)
        confirm_window.transient(self)
        confirm_window.grab_set()

        # Центрируем окно подтверждения
        confirm_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - confirm_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - confirm_window.winfo_height()) // 2
        confirm_window.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            confirm_window,
            text=f"Удалить {len(self.selected_commands)} команд?",
            font=("Arial", 14),
            wraplength=250
        ).pack(pady=20)

        def confirm_delete():
            # Удаляем выбранные команды
            for row_frame in self.selected_commands[:]:  # Копируем список для безопасного удаления
                self._remove_command_row(row_frame)

            confirm_window.destroy()
            self._update_selection_ui()

        def cancel_delete():
            confirm_window.destroy()

        buttons_frame = ctk.CTkFrame(confirm_window, fg_color="transparent")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Удалить",
            fg_color="#FF5555",
            hover_color="#CC0000",
            command=confirm_delete
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=cancel_delete
        ).pack(side="left", padx=10)

    def _update_selection_ui(self):
        """Обновляет UI после удаления"""
        self.selected_commands.clear()
        if hasattr(self, 'delete_selected_button'):
            self.delete_selected_button.configure(state="disabled")
        self._update_counter()

    # Обновите метод _remove_command_row для работы с выбранными командами
    def _remove_command_row(self, row_frame):
        """Удаляет одну команду"""
        # Убираем из выбранных если там есть
        if row_frame in self.selected_commands:
            self.selected_commands.remove(row_frame)

        # Находим и удаляем виджеты
        for widget in self.command_widgets:
            if widget["frame"] == row_frame:
                self.command_widgets.remove(widget)
                break

        row_frame.destroy()
        self._update_counter()
        self._update_selection_ui()

    # Сохранение команд
    def _save_commands(self):
        self.commands = []
        for widget in self.command_widgets:
            action_type = "key" if widget["type_combo"].get() == "Клавиши" else "app"
            action_value = widget["action_combo"].get()

            # Если это приложение, преобразуем отформатированное название обратно в ключ
            if action_type == "app" and hasattr(self, 'app_name_mapping'):
                action_value = self.app_name_mapping.get(action_value, action_value.lower())

            self.commands.append({
                "text": widget["entry"].get(),
                "action_type": action_type,
                "action_value": action_value
            })
        self.save_data()

        # Сообщение об успехе
        success_label = ctk.CTkLabel(
            self.main_frame,
            text="Команды сохранены!",
            text_color=self.custom_theme["success_color"]
        )
        success_label.pack(pady=5)
        self.after(2000, success_label.destroy)

        # Обновляем счетчик
        self._update_counter()
    # Добавление новой команды
    def _add_command_row(self, parent_frame):
        self._create_command_row(parent_frame)
        self._update_counter()

    def _update_counter(self):
        if hasattr(self, 'commands_counter'):
            self.commands_counter.configure(text=f"Всего команд: {len(self.command_widgets)}")


if __name__ == "__main__":
    try:
        app = VoiceAssistantApp()
        try:
            app.iconbitmap("LOGO.ico")
        except:
            pass
        app.mainloop()
    except KeyboardInterrupt:

        print("Приложение завершено")
    except Exception as errorx:
        with open("er.txt", "w", encoding="utf-8") as f:
            f.write(str(errorx))
