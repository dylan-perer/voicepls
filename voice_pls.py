from multiprocessing import Process
import cv2
import pytesseract
import pyscreenshot as ImageGrab
import numpy as np
import re
from text_to_speech import speak
import keyboard
import pyttsx3
import mouse

# TTS config
engine = pyttsx3.init()
voices = engine.getProperty('voices')

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
tess_data = '--tessdata-dir "C:/Program Files/Tesseract-OCR/tessdata"'


# pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

def tts_engine(phrase):
    engine.setProperty('rate', 195)
    engine.setProperty('voice', voices[1].id)
    engine.say(phrase)
    engine.runAndWait()


def contains_number(value):
    for character in value:
        if character.isdigit():
            return True
    return False


# screenshotting game screen to extract text from
def get_screenshot(debug=False, storybook=False):
    # bbox (x, y, x, y) screen space, turn debug flag to view the screenshot
    if storybook is False:
        screenshot = ImageGrab.grab(bbox=(460, 759, 1450, 1000))
    else:
        screenshot = ImageGrab.grab(bbox=(400, 75, 1450, 650))

    if debug:
        screenshot.show()
    img = np.array(screenshot)
    return img


# run OCR through the image to get text. play with resize values, fx & fy to improve accuracy
def ocr(img, debug=False):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = 127
    # img = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
    if debug:
        cv2.imshow('image', img)
        cv2.waitKey(0)
    return pytesseract.image_to_string(img, config=tess_data)


def sub_str_rm(text, sub_to_rm_after, before=False):
    if sub_to_rm_after in text:
        if before:
            return text[text.find(sub_to_rm_after)+1:]
        return text[:text.find(sub_to_rm_after)]
    return text


# formatting to be readable
def format_text(text, storybook_mode=False, debug=False):
    if text is not None:
        # Remove : if exists
        if storybook_mode is False:
            print("before {}".format(text))
            text = sub_str_rm(text, ':', before=True)
            print("after {}".format(text))

        # Remove Items received
        text = sub_str_rm(text, 'Items received:')
        text = sub_str_rm(text, 'Gained')
        text = sub_str_rm(text, "You've performed")

        # Remove user reply choices
        text = sub_str_rm(text, "1")

        # Fail if unwanted characters exists
        if storybook_mode is False:
            if text.find('_') != -1 or text.find('/') != -1 or text.find('\\') != -1:
                print("> Found unwanted character! : " + text)
                return -1

        # Remove unwanted spaces
        text = re.sub("\s\s+", " ", text)
        text = re.sub("\n+", " ", text)
        if storybook_mode:
            text = re.sub("_+", "", text)

        # Add voice pitch settings
        text = '<pitch absmiddle="-5">' + text + '</pitch>'
        text = text.replace('-5"> ', '-5">')

        if debug:
            print(text)
    return text


def speak(text):
    p = Process(target=tts_engine, args=[text])
    p.start()
    while p.is_alive():
        if keyboard.is_pressed('ctrl'):
            p.terminate()
        else:
            continue
    p.join()


def run_voice(storybook_mode=False):
    print('running {}voice...'.format('storybook ' if storybook_mode else ''))
    text = format_text(ocr(get_screenshot(debug=False, storybook=storybook_mode), debug=False), debug=True,
                       storybook_mode=storybook_mode)
    speak(text)


def on_click(x, y, button, pressed):
    if 220 <= x <= 1720 and 750 <= y <= 1800 and pressed:
        print("ok")
        p = Process(target=run_voice)
        p.start()
        p.join()


def add_key_detection():
    keyboard.add_hotkey('ctrl', lambda: run_voice())
    keyboard.add_hotkey('t', lambda: run_voice(storybook_mode=True))
    keyboard.wait()


if __name__ == '__main__':
    add_key_detection_process = Process(target=add_key_detection)
    add_key_detection_process.start()
    add_key_detection_process.join()
