import chess
import chess.svg
from ai import amove
from ai import board as bd
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import random
import pymorphy2
import json
import time
import requests
from requests import HTTPError
from PIL import Image, ImageDraw
from random import randint, choice
from seawar import *
from flask import Flask, request, jsonify
import json
import os
from cairosvg import svg2png


app = Flask(__name__)
wordtonum = {"ноль": 0, "тридцати": 30, "сорока": 40, "пятидесяти": 50, "десяти": 10, "двадцати":20, 'один': 1, "шестидесяти": 60, "семидесяти": 70, "восьмидесяти": 80, "одна": 1, 'два': 2, "две": 2, 'три': 3, 'четыре': 4, 'пять': 5,
     'шесть': 6, 'семь' : 7, 'восемь': 8, 'девять': 9, 'десять': 10, 'двадцать': 20,
     'тридцать': 30, 'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семьдесят': 70,
     'восемьдесят': 80, 'девяносто': 90, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13,
     'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
     'девятнадцать': 19, "сто": 100, "двести": 200, "триста": 300, "четыреста": 400, "пятьсот": 500,
     'шестьсот': 600, "семьсот": 700,"восемьсот": 800, "девятьсот": 900, "тысяча": 1, "тысяч": 1, "тысячи": 1, "десятых": 1,
     "нуля": 0, "одного": 1, "двух": 2, "трех": 3, "четырех": 4, "пяти": 5, "шести": 6, "семи": 7, "восьми": 8, "девяти": 9}
sessionStorage = {}
games = {}
profiles = {}
listofgames = ["шахматы", 'морской бой']
aiboards = {}
friendsgames = {}


class YandexImages(object):
    def __init__(self):
        self.SESSION = requests.Session()
        #self.SESSION.headers.update(AUTH_HEADER)

        self.API_VERSION = 'v1'
        self.API_BASE_URL = 'https://dialogs.yandex.net/api/'
        self.API_URL = self.API_BASE_URL + self.API_VERSION + '/'
        self.skills = ''

    def set_auth_token(self, token):
        self.SESSION.headers.update(self.get_auth_header(token))

    def get_auth_header(self, token):
        return {
            'Authorization': 'OAuth %s' % token
        }

    def log(self, error_text,response):
        log_file = open('YandexApi.log','a')
        log_file.write(error_text+'\n')#+response)
        log_file.close()

    def validate_api_response(self, response, required_key_name=None):
        content_type = response.headers['Content-Type']
        content = json.loads(response.text) if 'application/json' in content_type else None

        if response.status_code == 200:
            if required_key_name and required_key_name not in content:
                self.log('Unexpected API response. Missing required key: %s' % required_key_name, response=response)
                return None
        elif content and 'error_message' in content:
            self.log('Error API response. Error message: %s' % content['error_message'], response=response)
            return None
        elif content and 'message' in content:
            self.log('Error API response. Error message: %s' % content['message'], response=response)
            return None
        else:
            response.raise_for_status()

        return content

    ################################################
    # Проверить занятое место                      #
    #                                              #
    # Вернет массив                                #
    # - total - Сколько всего места осталось       #
    # - used - Занятое место                       #
    ################################################
    def checkOutPlace(self):
        result = self.SESSION.get(self.API_URL+'status')
        content = self.validate_api_response(result)
        if content != None:
            return content['images']['quota']
        return None

    ################################################
    # Загрузка изображения из интернета            #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################


    ################################################
    # Загрузка изображения из файла                #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################
    def downloadImageFile(self, img):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url = self.API_URL+path,files={'file':(img,open(img,'rb'))})
        content = self.validate_api_response(result)
        if content != None:
            return content['image']
        return None

    ################################################
    # Просмотр всех загруженных изображений        #
    #                                              #
    # Вернет массив из изображений                 #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.	           #
    ################################################
    def getLoadedImages(self):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.get(url = self.API_URL+path)
        content = self.validate_api_response(result)
        if content != None:
            return content['images']
        return None

    ################################################
    # Удаление выбранной картинки                  #
    #                                              #
    # В случае успеха вернет 'ok'	               #
    ################################################
    def deleteImage(self, img_id):
        path = 'skills/{skills_id}/images/{img_id}'.format(skills_id=self.skills,img_id = img_id)
        result = self.SESSION.delete(url=self.API_URL+path)
        content = self.validate_api_response(result)
        if content != None:
            return content['result']
        return None

    def deleteAllImage(self):
        success = 0
        fail = 0
        images = self.getLoadedImages()
        for image in images:
            image_id = image['id']
            if image_id:
                if self.deleteImage(image_id):
                    success+=1
                else:
                    fail += 1
            else:
                fail += 1

        return {'success':success,'fail':fail}


def rustoseaWar(qq):
    otv = [0, 0]
    bukvi = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    ruseng = {"с": "c", "джи": "g", "ф": "f", "а": "a", "б": "b", "ц": "c", "си": "c", "д": "d", "ди": "d", "е": "e", "и": "e", "эф": "f", "г": "g", "аш": "h", "х": "h", "ай": "i", "и": "i", "джей": "j", "же": "j", "жэ": "j", "далее": "d", "быть": "e"}
    wordnum = {"один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "семь": "7", "восемь": "8", "девять": "9", "десять": "10"}
    if " " not in qq:
        qq = qq[0] + " " + qq[1:]
    for i in qq.split():
        if i in ruseng:
            otv[1] = bukvi.index(ruseng[i])
        elif i in bukvi:
            otv[1] = bukvi.index(i)
        elif i in wordnum:
            otv[0] = int(wordnum[i]) - 1
        else:
            print(i)
            try:
                otv[0] = int(i) - 1
            except:
                otv[0] = 100
    return otv



def rustochess(qq):
    otv = ''
    ruseng = {"джи": "g", "ф": "f", "а": "a", "б": "b", "ц": "c", "си": "c", "д": "d", "ди": "d", "е": "e", "и": "e", "эф": "f", "г": "g", "аш": "h", "х": "h", "далее": "d", "быть": "e"}
    wordnum = {"один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "семь": "7", "восемь": "8"}
    for i in qq.split():
        if i in ruseng:
            otv += ruseng[i]
        elif i in wordnum:
            otv += wordnum[i]
        elif i == "на":
            pass
        else:
            otv += i
    return otv


def printchessboard(s):
    otv = s.split('\n')
    for i in range(len(otv)):
        otv[i] = str(8 - i) + '\t' + "\t".join(otv[i].replace('.', '#').split())
    otv.append("\t".join(["0", "A", "B", "C", "D", "E", "F", "G", "H"]))
    return "\n".join(otv)


@app.route('/', methods=["POST"])
def main():
    event = request.json
    yandex = YandexImages()
    yandex.set_auth_token(token = 'y0_AgAAAABVMSWEAAT7owAAAADfiH7Swo8jDnWDRlCVLPMC_o3zj8Pozkg')
    yandex.skills = '60459c66-a701-463b-8f24-bada3d7cf736'
    response = {
        "version": event["version"],
        "session": event["session"],
        "id": event["session"]["message_id"],
        "response": {
            "end_session": False
        }
    }
    morph = pymorphy2.MorphAnalyzer()
    qq = " ".join([morph.parse(i)[0].normal_form for i in event['request']['original_utterance'].lower().rstrip(".").split()])
    if any([i in ("помощь", "подсказать", "помоги", "помогать") for i in qq.split()]):
        otv = random.choice(["Вы можете вывести список игр по команде играть, далее выбрать нужную игру и соперника, после чего начнется игра. Либо вы можете посмотреть свой рейтинг по команде профиль", "Вы можете вывести список игр по команде играть, посмотреть свой профиль по команде профиль, начать игру по названию желаемой игры."])
        response["response"]["text"] = otv
        response['response']['buttons'] = [{"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
        return response
    elif any([i == "уметь" for i in qq.split()]):
        otv = random.choice(["Я умею играть (морской бой и шахматы), вы можете посоревноваться со мной. Так же вы можете поиграть со своим человеком. Вы можете поднимать свой рейтинг", "В данном навыке вы можете поиграть в различные игры. Играть вы можете как против меня, так и против человека. За победы вам добавляется рейтинг"])
        response["response"]["text"] = otv
        response['response']['buttons'] = [{"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
        return response
    elif qq == 'чистка':
        if event['session']['user_id'] in games:
            games.pop(event['session']['user_id'])
            if event['session']['user_id'] in friendsgames:
                if friendsgames[event['session']['user_id']] in sessionStorage:
                    sessionStorage.pop(friendsgames[event['session']['user_id']])
                friendsgames.pop(friendsgames[event['session']['user_id']])
            response["response"]["text"] = "Ваш id был удалён"
        else:
            response["response"]["text"] = "Вашего id итак нет в базе данных"
        profiles[event['session']['user_id']] = 0
        return response
    if event['session']['new']:
        response["response"]["text"] = "Приветствую в навыке 'Играй вместе'. Вы можете попросить помощь, посмотреть свой рейтинг, либо начать играть."
        response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}, {"title": "что ты умеешь", "hide": True}]
        if event['session']['user_id'] not in profiles:
            profiles[event['session']['user_id']] = 0
    elif event['session']['user_id'] in games:
        if any([i in ('выход', 'закончить', 'выйти', 'назад') for i in qq.split()]):
            games.pop(event['session']['user_id'])
            response["response"]["text"] = "Вы вернулись в главное меню. Можете попросить помощи, посмотреть профиль, или начать игру."
            response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
        elif games[event['session']['user_id']][0] == "SeaWar":
            near_list = [(0, -1), (0, 1), (1, 0), (-1, 0)]
            all_near_list = [(0, -1), (0, 1), (1, 0), (-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            diag_near_list=[(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if games[event['session']['user_id']][1] == "none":
                if any([i == "компьютер" for i in qq.split()]):
                    games[event['session']['user_id']][1] = "ai"
                    bot_board = generate_board()
                    player_board = generate_board()
                    bot_board_shoot = generate_white_board()
                    player_board_shoot = generate_white_board()
                    bot_memory = []
                    display_board(player_board, player_board_shoot, bot_board, "kartinki_morskoy_boy_8_08082042.png", "kartin.png")
                    image = yandex.downloadImageFile('kartin.png')
                    response['response']['card'] = {}
                    response['response']['card']['image_id'] = image["id"]
                    response['response']['card']['type'] = "BigImage"
                    response['response']['card']['title'] = "Морской Бой"
                    response['response']['card']['description'] = random.choice(["Да начнётся игра!", "Удачной игры!", "Ваше поле"])
                    response['response']['text'] = response['response']['card']['description']
                    sessionStorage[event['session']['user_id']] = [player_board, player_board_shoot]
                    aiboards[event['session']['user_id']] = [bot_board, bot_board_shoot, bot_memory, near_list, all_near_list]
                if any([i == "человек" for i in qq.split()]):
                    games[event['session']['user_id']][1] = "friendchoice"
                    response["response"]["text"] = "Создать комнату или присоединиться? Если хотите создать, то введите код комнаты."
                    cd = str(random.randint(100, 999))
                    while cd in sessionStorage:
                        cd = str(random.randint(100, 999))
                    response['response']['buttons'] = [{'title': cd, 'hide': True}, {'title': "Присоединиться", 'hide': True}]
            elif games[event['session']['user_id']][1] == "ai":
                player_board = sessionStorage[event['session']['user_id']][0]
                player_board_shoot = sessionStorage[event['session']['user_id']][1]
                bot_board = aiboards[event['session']['user_id']][0]
                bot_board_shoot = aiboards[event['session']['user_id']][1]
                bot_memory = aiboards[event['session']['user_id']][2]
                qq = rustoseaWar(qq)
                print(qq)
                if qq not in create_legal_moves(bot_board_shoot):
                    response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А2, либо вводите", "Неправильно! Вводите в формате А2, либо говорите"])
                    return response
                x = qq[0]
                y = qq[1]
                res = shoot(x, y, bot_board, player_board_shoot)
                if res != 'Попал' and res != 'Уничтожил!':
                    mess = bot_shoot(player_board, bot_board_shoot)
                    display_board(player_board, player_board_shoot, bot_board, "kartinki_morskoy_boy_8_08082042.png", "kartin.png")
                    image = yandex.downloadImageFile('kartin.png')
                    response['response']['card'] = {}
                    response['response']['card']['image_id'] = image["id"]
                    response['response']['card']['type'] = "BigImage"
                    print(mess)
                    if mess[-1] == 'Мимо':
                       response['response']['card']['description'] = random.choice(["Не в этот раз(как и для бота)", "Не попал(", "Не повезло - не повезло", "С кем не бывает!", "компьютер тоже промахнулся", "компьютер"])
                       response['response']['text'] = response['response']['card']['description']
                    elif mess[-1] == 'Попал':    
                        response['response']['card']['description'] = random.choice(["Не в этот раз, а для бота именно в этот)", "Не попал(", "Не повезло - не повезло", "С кем не бывает!", "компьютер тоже промахнулся(нет)"])
                        response['response']['text'] = response['response']['card']['description']
                    elif mess[-1] == 'Уничтожил!' and 'Уничтожил!' in mess[0:len(mess)-1]:
                        response['response']['card']['description'] = random.choice(["Уничтожил!", "Твои корабали были потоплены(", "кажись минус караблики", "С кем не бывает! потерял - так потерял"])
                        response['response']['text'] = response['response']['card']['description']
                    elif mess[-1] == 'Уничтожил!':
                        response['response']['card']['description'] = random.choice(["Уничтожил!", "Твой корабаль был потоплен(", "кажись минус караблик", "С кем не бывает! потерял - так потерял"])
                        response['response']['text'] = response['response']['card']['description']
                else:
                    display_board(player_board, player_board_shoot, bot_board, "kartinki_morskoy_boy_8_08082042.png", "kartin.png")
                    image = yandex.downloadImageFile('kartin.png')
                    response['response']['card'] = {}
                    response['response']['card']['image_id'] = image["id"]
                    response['response']['card']['type'] = "BigImage"
                    response['response']['card']['description'] = random.choice(["ЙОУ, а ты снайпер", "Есть пробитие!", "Попадание!", "Да ты на лаки просто *_*"]) + " " + random.choice(["дерзай еще!", "но получится ли попасть в следующий раз?", "ходи следующим", "Твой ход следующий"])
                    response['response']['text'] = response['response']['card']['description']
                    if game_over(bot_board) and game_over(player_board):
                        response['response']['text'] = random.choice(["как же так... ничья", "НИЧЬЯ!", "ни кто не выйграл, но ни кто не проиграл", "ты проиграл... как и противник"])
                        games.pop(event['session']['user_id'])
                    elif game_over(bot_board):
                        response['response']['text'] = random.choice(["ТЫ ВЫЙГРАЛ!", "ПОБЕДА", "ВИКТОРИИ", "Да ты на лаки просто *_*"])
                        games.pop(event['session']['user_id'])
                    elif game_over(player_board):
                        response['response']['text'] = random.choice(["ТЫ ПРОИГРАЛ! УРАА", "ну проиграл и проиграл", "ПОРАЖАНИЕ!!!", "Нуб", "да лан"])
                        games.pop(event['session']['user_id'])
            elif games[event['session']['user_id']][1] == 'friendchoice':
                response['response']['buttons'] = [{'title': "Присоединиться", 'hide': True}]
                if any([i in ('зайти', "присоединиться", "найти") for i in qq.split()]):
                    games[event['session']['user_id']][1] = 'friendconnect'
                    response['response']['text'] = "Введите код комнаты. Спросите его у человека, который создал комнату. Список существующих комнат: " + " ".join(list(sessionStorage.keys()))
                elif all([i in wordtonum for i in qq.split()]) or all([i.isdigit() for i in qq.split()]):
                    code = "".join([str(wordtonum[i]) if i in wordtonum else i for i in qq.split()])
                    if code in sessionStorage:
                        response['response']['text'] = "Такой код уже есть в списке игр! Придумайте другой."
                        return response
                    games[event['session']['user_id']][1] = 'friendgame'
                    friendsgames[event['session']['user_id']] = code
                    guest_board = generate_board()
                    host_board = generate_board()
                    guest_board_shoot = generate_white_board()
                    host_board_shoot = generate_white_board()
                    storona = "guest"
                    sessionStorage[code] = [guest_board, host_board, guest_board_shoot, host_board_shoot, event['session']['user_id'], storona]
                    response['response']['text'] = "Комната создана! Скажите другу зайти по вашему коду и сделать ход. " + code
            elif games[event['session']['user_id']][1] == 'friendconnect':
                if all([i in wordtonum for i in qq.split()]) or all([i.isdigit() for i in qq.split()]):
                    code = "".join([str(wordtonum[i]) if i in wordtonum else i for i in qq.split()])
                    if code in sessionStorage:
                        friendsgames[event['session']['user_id']] = code
                        games[event['session']['user_id']][1] = "friendgame"
                        response['response']['text'] = "Игра началась! Сделайте ход."
                    else:
                        response['response']['text'] = "Такой комнаты нет! Убедитесь, что ваш друг её создал и перепроверьте код. " + code + " коды которые есть: " + " ".join(list(sessionStorage.keys()))
                else:
                    response['response']['text'] = "Некорректно введён код! Вводите код без лишних слов."
            elif games[event['session']['user_id']][1] == 'friendgame':
                code = friendsgames[event['session']['user_id']]
                if sessionStorage[code][-2] == event['session']['user_id']:
                    response['response']['text'] = "Ваш противник ещё не сходил! Ожидайте."
                    response['response']['buttons'] = [{'title': "Проверить", 'hide': True}]
                else:
                    storona = sessionStorage[code][-1]
                    guest_board = sessionStorage[code][0]
                    host_board = sessionStorage[code][1]
                    guest_board_shoot = sessionStorage[code][2]
                    host_board_shoot = sessionStorage[code][3]
                    print(qq)
                    if any([i in ("проверить", "проверка") for i in qq.split()]):
                        print(storona)
                        response['response']['text'] = "противник совершил ход"
                        if storona == "guest":
                            display_board(guest_board, guest_board_shoot, host_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_guest.png")
                            image = yandex.downloadImageFile('kartin_guest.png')
                            response['response']['card'] = {}
                            response['response']['card']['image_id'] = image["id"]
                            response['response']['card']['type'] = "BigImage"
                            response['response']['text'] = "ЛОЛ ГУЕСТ"
                            if game_over(guest_board):
                                response['response']['text'] = random.choice(["ТЫ ПРОИГРАЛ! УРАА", "ну проиграл и проиграл", "ПОРАЖАНИЕ!!!", "Нуб", "да лан"])   
                                response['response']['text'] = response['response']['card']['description']
                                games.pop(event['session']['user_id'])
                                sessionStorage.pop(friendsgames[event['session']['user_id']])
                                friendsgames.pop(event['session']['user_id'])
                        else:
                            display_board(host_board, host_board_shoot, guest_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_host.png")
                            image = yandex.downloadImageFile('kartin_host.png')
                            response['response']['card'] = {}
                            response['response']['card']['image_id'] = image["id"]
                            response['response']['card']['type'] = "BigImage"
                            response['response']['text'] = "ЛОЛ ХОСТ"
                            if game_over(host_board):
                                response['response']['text'] = random.choice(["ТЫ ПРОИГРАЛ! УРАА", "ну проиграл и проиграл", "ПОРАЖАНИЕ!!!", "Нуб", "да лан"])   
                                response['response']['text'] = response['response']['card']['description']
                                games.pop(event['session']['user_id'])
                                sessionStorage.pop(friendsgames[event['session']['user_id']])
                                friendsgames.pop(event['session']['user_id'])
                        return response
                    qq = rustoseaWar(qq)
                    if qq not in create_legal_moves(guest_board_shoot) and storona == "guest":
                        response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А2, либо вводите", "Неправильно! Вводите в формате А2, либо говорите"])
                        display_board(guest_board, guest_board_shoot, host_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_guest.png")
                        image = yandex.downloadImageFile('kartin_guest.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А2, либо вводите", "Неправильно! Вводите в формате А2, либо говорите"])
                        return response
                    elif qq not in create_legal_moves(host_board_shoot) and storona == "host":
                        display_board(host_board, host_board_shoot, guest_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_host.png")
                        image = yandex.downloadImageFile('kartin_host.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А2, либо вводите", "Неправильно! Вводите в формате А2, либо говорите"])
                        return response
                    if storona == "guest":
                        x = qq[0]
                        y = qq[1]
                        res = shoot(x, y, host_board, guest_board_shoot)
                        display_board(guest_board, guest_board_shoot, host_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_guest.png")
                        image = yandex.downloadImageFile('kartin_guest.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        response['response']['text'] = "вы сходили"
                        if res == "Мимо":
                            sessionStorage[code][-1] = "host"
                            sessionStorage[code][-2] = event['session']['user_id']
                        print(res, sessionStorage[code][-1], sessionStorage[code][-2])
                        if game_over(host_board):
                            response['response']['card']['description'] = random.choice(["ТЫ ВЫЙГРАЛ!", "ПОБЕДА", "ВИКТОРИИ", "Да ты на лаки просто *_*"])
                            response['response']['text'] = response['response']['card']['description']
                            sessionStorage[code][-2] = event['session']['user_id']
                            games.pop(event['session']['user_id'])
                            friendsgames.pop(event['session']['user_id'])
                            profiles[event['session']['user_id']] += 25
                    else:
                        x = qq[0]
                        y = qq[1]
                        res = shoot(x, y, guest_board, host_board_shoot)
                        display_board(host_board, host_board_shoot, guest_board, "kartinki_morskoy_boy_8_08082042.png", "kartin_host.png")
                        image = yandex.downloadImageFile('kartin_host.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        response['response']['text'] = "вы сходили"
                        if res == "Мимо":
                            sessionStorage[code][-1] = "guest"
                            sessionStorage[code][-2] = event['session']['user_id']
                        print(res, sessionStorage[code][-1], sessionStorage[code][-2])
                        if game_over(host_board):
                            response['response']['card']['description'] = random.choice(["ТЫ ВЫЙГРАЛ!", "ПОБЕДА", "ВИКТОРИИ", "Да ты на лаки просто *_*"])
                            response['response']['text'] = response['response']['card']['description']
                            games.pop(event['session']['user_id'])
                            sessionStorage[code][-2] = event['session']['user_id']
                            friendsgames.pop(event['session']['user_id'])
                            if event['session']['user_id'] in profiles:
                                profiles[event['session']['user_id']] += 25
                            else:
                                profiles[event['session']['user_id']] = 25
        elif games[event['session']['user_id']][0] == 'chess':
            if games[event['session']['user_id']][1] == "none":
                if any([i == "человек" for i in qq.split()]):
                    games[event['session']['user_id']][1] = "friendchoice"
                    response["response"]["text"] = "Создать комнату или присоединиться? Если хотите создать, то введите код комнаты."
                    cd = str(random.randint(100, 999))
                    while cd in sessionStorage:
                        cd = str(random.randint(100, 999))
                    response['response']['buttons'] = [{'title': cd, 'hide': True}, {'title': "Присоединиться", 'hide': True}]
    
                elif any([i == "компьютер" for i in qq.split()]):
                    games[event['session']['user_id']][1] = "ai"
                    sessionStorage[event['session']['user_id']] = chess.Board()
                    aiboards[event['session']['user_id']] = bd.new()
                    board_svg = chess.svg.board(board=sessionStorage[event['session']['user_id']]).encode('utf-8')
                    with open("/tmp/board.svg", "wb") as f:
                        f.write(board_svg)
                    svg2png(url='/tmp/board.svg', write_to='/tmp/board.png')
                    image_path="/tmp/board.png"
                    img = Image.open(image_path)
                    new_image = img.resize((258, 258))
                    third_image = new_image.crop((-162, 0, 258 + 162, 258))
                    third_image.save('/tmp/answer.png')
                    image = yandex.downloadImageFile('/tmp/answer.png')
                    response['response']['card'] = {}
                    response['response']['card']['image_id'] = image["id"]
                    response['response']['card']['type'] = "BigImage"
                    response["response"]["text"] = random.choice(["Да начнётся игра!", "Удачной игры!"])
                elif any([i == "случайный" for i in qq.split()]):
                    # games[event['session']['user_id']][1] = "random"
                    response['response']['text'] = 'Эта ветка навыка ещё не закончена! Совсем скоро вы сможете поиграть с человеком'
                    response['response']['buttons'] = [{'title': "человек", 'hide': True}, {'title': "Компьютер", 'hide': True}]
                else:
                    response['response']['text'] = "Такого варианта у меня ещё нет. Выберите что то человекое"
                    response['response']['buttons'] = [{'title': "человек", 'hide': True}, {'title': "Компьютер", 'hide': True}]
            elif games[event['session']['user_id']][1] == 'friendconnect':
                if all([i in wordtonum for i in qq.split()]) or all([i.isdigit() for i in qq.split()]):
                    code = "".join([str(wordtonum[i]) if i in wordtonum else i for i in qq.split()])
                    if code in sessionStorage:
                        friendsgames[event['session']['user_id']] = code
                        games[event['session']['user_id']][1] = "friendgame"
                        response['response']['text'] = "Игра началась! Сделайте ход."
                    else:
                        response['response']['text'] = "Такой комнаты нет! Убедитесь, что ваш человек её создал и перепроверьте код. " + code + " коды которые есть: " + " ".join(list(sessionStorage.keys()))
                else:
                    response['response']['text'] = "Некорректно введён код! Вводите код без лишних слов."
            elif games[event['session']['user_id']][1] == 'friendgame':
                code = friendsgames[event['session']['user_id']]
                if sessionStorage[code][1] == event['session']['user_id']:
                    response['response']['text'] = "Ваш противник ещё не сходил! Ожидайте."
                    response['response']['buttons'] = [{'title': "Проверить", 'hide': True}]
                else:
                    if len(list(sessionStorage[code][0].legal_moves)) == 0:
                        if sessionStorage[code][0].is_stalemate():
                            response['response']['text'] = "Ничья! Хорошая игра."
                            sessionStorage.pop(code)
                            response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                            friendsgames.pop(event['session']['user_id'])
                            return response
                        elif sessionStorage[code][0].is_checkmate():
                            response['response']['text'] = "Вы проиграли! Попробуйте ещё раз."
                            games.pop(event['session']['user_id'])
                            sessionStorage.pop(code)
                            friendsgames.pop(event['session']['user_id'])
                            response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                            return response
                    if any([i in ("проверить", "проверка") for i in qq.split()]):
                        response['response']['text'] = "противник совершил ход"
                        board_svg = chess.svg.board(board=sessionStorage[code][0]).encode('utf-8')
                        with open("/tmp/board.svg", "wb") as f:
                            f.write(board_svg)
                        svg2png(url='/tmp/board.svg', write_to='/tmp/board.png')
                        image_path="/tmp/board.png"
                        img = Image.open(image_path)
                        new_image = img.resize((258, 258))
                        third_image = new_image.crop((-162, 0, 258 + 162, 258))
                        third_image.save('/tmp/answer.png')
                        image = yandex.downloadImageFile('/tmp/answer.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        return response
                    qq = rustochess(qq)
                    if qq not in [str(i) for i in sessionStorage[code][0].legal_moves]:
                        response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А 2 на А4, либо вводите a2a4", "Неправильно! Вводите в формате b2b4, либо говорите Б 2 на Б 4"])
                        board_svg = chess.svg.board(board=sessionStorage[code][0]).encode('utf-8')
                        with open("/tmp/board.svg", "wb") as f:
                            f.write(board_svg)
                        svg2png(url='/tmp/board.svg', write_to='/tmp/board.png')
                        image_path="/tmp/board.png"
                        img = Image.open(image_path)
                        new_image = img.resize((258, 258))
                        third_image = new_image.crop((-162, 0, 258 + 162, 258))
                        third_image.save('/tmp/answer.png')
                        image = yandex.downloadImageFile('/tmp/answer.png')
                        response['response']['card'] = {}
                        response['response']['card']['image_id'] = image["id"]
                        response['response']['card']['type'] = "BigImage"
                        return response
                    sessionStorage[code][0].push_uci(qq)
                    sessionStorage[code][1] = event['session']['user_id']
                    if len(list(sessionStorage[code][0].legal_moves)) == 0:
                        if sessionStorage[code][0].is_stalemate():
                            response['response']['text'] = "Ничья! Хорошая игра."
                            friendsgames.pop(event['session']['user_id'])
                            response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                            return response
                        elif sessionStorage[code][0].is_checkmate():
                            response['response']['text'] = "Вы победили! Хорошая игра."
                            games.pop(event['session']['user_id'])
                            friendsgames.pop(event['session']['user_id'])
                            profiles[event['session']['user_id']] += 25
                            response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                            return response
                    response['response']['text'] = "Ожидайте хода соперника."
                    response['response']['buttons'] = [{'title': "Проверить", 'hide': True}]
                    board_svg = chess.svg.board(board=sessionStorage[code][0]).encode('utf-8')
                    with open("/tmp/board.svg", "wb") as f:
                        f.write(board_svg)
                    svg2png(url='/tmp/board.svg', write_to='/tmp/board.png')
                    image_path="/tmp/board.png"
                    img = Image.open(image_path)
                    new_image = img.resize((258, 258))
                    third_image = new_image.crop((-162, 0, 258 + 162, 258))
                    third_image.save('/tmp/answer.png')
                    image = yandex.downloadImageFile('/tmp/answer.png')
                    response['response']['card'] = {}
                    response['response']['card']['image_id'] = image["id"]
                    response['response']['card']['type'] = "BigImage"
            elif games[event['session']['user_id']][1] == 'friendchoice':
                response['response']['buttons'] = [{'title': "Присоединиться", 'hide': True}]
                if any([i in ('зайти', "присоединиться", "найти") for i in qq.split()]):
                    games[event['session']['user_id']][1] = 'friendconnect'
                    response['response']['text'] = "Введите код комнаты. Спросите его у человека, который создал комнату. Список существующих комнат: " + " ".join(list(sessionStorage.keys()))
                elif all([i in wordtonum for i in qq.split()]) or all([i.isdigit() for i in qq.split()]):
                    code = "".join([str(wordtonum[i]) if i in wordtonum else i for i in qq.split()])
                    if code in sessionStorage:
                        response['response']['text'] = "Такой код уже есть в списке игр! Придумайте человекой."
                        return response
                    games[event['session']['user_id']][1] = 'friendgame'
                    friendsgames[event['session']['user_id']] = code
                    sessionStorage[code] = [chess.Board(), event['session']['user_id']]
                    response['response']['text'] = "Комната создана! Скажите человеку зайти по вашему коду и сделать ход. " + code
            elif games[event['session']['user_id']][0] == 'chess' and games[event['session']['user_id']][1] == 'ai':
                qq = rustochess(qq)
                if qq not in [str(i) for i in sessionStorage[event['session']['user_id']].legal_moves]:
                    response['response']['text'] = random.choice(["Неправильный ход. Говорите в формате А 2 на А4, либо вводите a2a4", "Неправильно! Вводите в формате b2b4, либо говорите Б 2 на Б 4"]) + "Вы попытались сходить: " + qq
                    return response
                lst = amove(qq, aiboards[event['session']['user_id']])
                sessionStorage[event['session']['user_id']].push_uci(qq)
                if sessionStorage[event['session']['user_id']].is_stalemate():
                    response['response']['text'] = "Ничья! Хорошая игра."
                    games.pop(event['session']['user_id'])
                    response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                    sessionStorage.pop(event['session']['user_id'])
                    return response
                elif sessionStorage[event['session']['user_id']].is_checkmate():
                    response['response']['text'] = "Победа! Хорошая игра."
                    profiles[event['session']['user_id']] += 25
                    games.pop(event['session']['user_id'])
                    response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                    sessionStorage.pop(event['session']['user_id'])
                    return response
                sessionStorage[event['session']['user_id']].push_uci(lst[0])
                if sessionStorage[event['session']['user_id']].is_stalemate():
                    response['response']['text'] = "Ничья! Хорошая игра."
                    games.pop(event['session']['user_id'])
                    response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                    sessionStorage.pop(event['session']['user_id'])
                    return response
                elif sessionStorage[event['session']['user_id']].is_checkmate():
                    response['response']['text'] = "Вы проиграли! Попробуйте ещё раз."
                    games.pop(event['session']['user_id'])
                    sessionStorage.pop(event['session']['user_id'])
                    response['response']['buttons'] = [{'title': 'профиль', "hide": True}, {'title': 'помощь', "hide": True}, {'title': 'играть', "hide": True}]
                    return response
                aiboards[event['session']['user_id']] = lst[1]
                response["response"]["text"] = "Противник сходил " + lst[0] + ". Ваш ход"
                board_svg = chess.svg.board(board=sessionStorage[event['session']['user_id']]).encode('utf-8')
                with open("/tmp/board.svg", "wb") as f:
                    f.write(board_svg)
                svg2png(url='/tmp/board.svg', write_to='/tmp/board.png')
                image_path="/tmp/board.png"
                img = Image.open(image_path)
                new_image = img.resize((258, 258))
                third_image = new_image.crop((-162, 0, 258 + 162, 258))
                third_image.save('/tmp/answer.png')
                image = yandex.downloadImageFile('/tmp/answer.png')
                response['response']['card'] = {}
                response['response']['card']['image_id'] = image["id"]
                response['response']['card']['type'] = "BigImage"
                # response["response"]["text"] = printchessboard(str(sessionStorage[event['session']['user_id']]))
            else:
                response['response']['text'] = "Такого варианта у меня ещё нет. Выберите что то человекое"
                response['response']['buttons'] = [{'title': "человек", 'hide': True}, {'title': "Компьютер", 'hide': True}]
    else:
        if any([i in ("помощь", "что ты уметь", "подсказать") for i in qq.split()]):
            otv = random.choice(["Вы можете начать игру с человеком, компьютером. Либо вы можете посмотреть свой рейтинг по команде профиль", "В данном навыке вы можете играть в шахматы с человеком, компьютером. Также вы можете зайти в свой профиль и увидеть статистику", "Я умею запускать с человеком, компьютером, или случайным человеком. Либо показать ваш рейтинг по команде профиль"])
            response["response"]["text"] = otv
            response['response']['buttons'] = [{"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
        elif any([i in ("профиль", "статистика", "рейтинг") for i in qq.split()]):
            if event['session']['user_id'] not in profiles:
                profiles[event['session']['user_id']] = 0
            response["response"]["text"] = "Ваш рейтинг: " + str(profiles[event['session']['user_id']])
            response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True}]
        elif any([i in ("играть", "выбор игра", "поиграть") for i in qq.split()]):
            response["response"]["text"] = "Выберите игру: " + "\n".join(listofgames)
            response['response']['buttons'] = []
            for i in listofgames:
                c = {'title': i, 'hide': False}
                response['response']['buttons'].append(c)
        elif any([i == "шахматы" for i in qq.split()]):
            games[event['session']['user_id']] = ["chess", "none"]
            response['response']['card'] = {}
            response['response']['card']['image_id'] = '213044/25964e6c4a27e7818633'
            response['response']['card']['type'] = "BigImage"
            response['response']['card']['title'] = "Шахматы"
            response['response']['card']['description'] = random.choice(["Выберите соперника: человек, компьютер", "C кем хотите играть? С человеком или компьютером"])
            response['response']['buttons'] = [{'title': "человек", 'hide': True}, {'title': "Компьютер", 'hide': True}]
            response['response']['text'] = "Выберите соперника: человек, компьютер"
        elif any([i == "морской" for i in qq.split()]):
            games[event['session']['user_id']] = ["SeaWar", "none"]
            response['response']['card'] = {}
            response['response']['card']['image_id'] = '937455/232c2094012519c12d13'
            response['response']['card']['type'] = "BigImage"
            response['response']['card']['title'] = "Морской Бой"
            response['response']['card']['description'] = random.choice(["Выберите соперника: человек, компьютер", "C кем хотите играть? С человеком, компьютером"])
            response['response']['buttons'] = [{'title': "человек", 'hide': True}, {'title': "Компьютер", 'hide': True}]
            response['response']['text'] = "Выберите соперника: человек, компьютер"
        elif any([i in ('выход', 'завершить', 'выйти') for i in qq.split()]):
            response['response']['text'] = "Буду ждать вас снова!"
            response['response']["end_session"] = True
        else:
            response["response"]["text"] = random.choice(["Извините, я вас не понимаю. Попробуйте попросить помощь", "Я не знаю таких команд. Попробуйте спросить что я умею", "Увы, на такое меня не программировали. Попросите помощи"])
            response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
    return json.dumps(response)


@app.route('/', methods=["GET"])
def qwe():
    return "Это навык для алисы!"


port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)