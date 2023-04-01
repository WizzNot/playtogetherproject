from flask import Flask, request
import json
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
from PIL import Image
import os

sessionStorage = {}
games = {}
profiles = {}
listofgames = ["шахматы"]
aiboards = {}


class YandexImages(object):
    def __init__(self):
        self.SESSION = requests.Session()
        # self.SESSION.headers.update(AUTH_HEADER)

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

    def log(self, error_text, response):
        log_file = open('YandexApi.log', 'a')
        log_file.write(error_text + '\n')  # +response)
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
        result = self.SESSION.get(self.API_URL + 'status')
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
        result = self.SESSION.post(url=self.API_URL + path, files={'file': (img, open(img, 'rb'))})
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
        result = self.SESSION.get(url=self.API_URL + path)
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
        path = 'skills/{skills_id}/images/{img_id}'.format(skills_id=self.skills, img_id=img_id)
        result = self.SESSION.delete(url=self.API_URL + path)
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
                    success += 1
                else:
                    fail += 1
            else:
                fail += 1

        return {'success': success, 'fail': fail}


def rustochess(qq):
    otv = ''
    ruseng = {"джи": "g", "ф": "f", "а": "a", "б": "b", "ц": "c", "си": "c", "д": "d", "ди": "d", "е": "e", "и": "e",
              "эф": "f", "г": "g", "аш": "h", "х": "h", "далее": "d", "быть": "e"}
    wordnum = {"один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "семь": "7",
               "восемь": "8"}
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
    yandex.set_auth_token(token='y0_AgAAAABVMSWEAAT7owAAAADfiH7Swo8jDnWDRlCVLPMC_o3zj8Pozkg')
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
    qq = " ".join(
        [morph.parse(i)[0].normal_form for i in event['request']['original_utterance'].lower().rstrip(".").split()])
    if any([i in ("помощь", "что ты уметь", "подсказать") for i in qq.split()]):
        otv = random.choice([
                                "Вы можете начать игру с другом, компьютером, или случайным человеком. Либо вы можете посмотреть свой рейтинг по команде профиль",
                                "В данном навыке вы можете играть в шахматы с другом, компьютером, или случайным человеком. Также вы можете зайти в свой профиль и увидеть статистику",
                                "Я умею запускать с другом, компьютером, или случайным человеком. Либо показать ваш рейтинг по команде профиль"])
        response["response"]["text"] = otv
        response['response']['buttons'] = [{"title": "Играть", "hide": True}, {"title": "Профиль", "hide": True}]
        return response
    elif qq == 'чистка':
        if event['session']['user_id'] in games:
            games.pop(event['session']['user_id'])
            response["response"]["text"] = "Ваш id был удалён"
        else:
            response["response"]["text"] = "Вашего id итак нет в базе данных"
        profiles[event['session']['user_id']] = 0
        return response
    if event['session']['new']:
        response["response"][
            "text"] = "Приветствую в навыке 'Играй вместе'. Вы можете попросить помощь, посмотреть свой рейтинг, либо начать играть."
        response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True},
                                           {"title": "Профиль", "hide": True}]
        if event['session']['user_id'] not in profiles:
            profiles[event['session']['user_id']] = 0
    elif event['session']['user_id'] in games:
        if any([i in ('выход', 'закончить', 'выйти', 'назад') for i in qq.split()]):
            games.pop(event['session']['user_id'])
            response["response"][
                "text"] = "Вы вернулись в главное меню. Можете попросить помощи, посмотреть профиль, или начать игру."
            response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True},
                                               {"title": "Профиль", "hide": True}]
        elif games[event['session']['user_id']][1] == "none":
            if any([i == "друг" for i in qq.split()]):
                # games[event['session']['user_id']][1] = "friend"
                response["response"][
                    "text"] = "Эта ветка навыка ещё не закончена! Совсем скоро вы сможете поиграть с другом"
                response['response']['buttons'] = [{'title': "Друг", 'hide': True},
                                                   {'title': "Компьютер", 'hide': True},
                                                   {'title': "Случайный игрок", 'hide': True}]
            elif any([i == "компьютер" for i in qq.split()]):
                games[event['session']['user_id']][1] = "ai"
                sessionStorage[event['session']['user_id']] = chess.Board()
                aiboards[event['session']['user_id']] = bd.new()
                board_svg = chess.svg.board(board=sessionStorage[event['session']['user_id']]).encode('utf-8')
                with open("/tmp/board.svg", "wb") as f:
                    f.write(board_svg)
                drawing = svg2rlg('/tmp/board.svg')
                renderPM.drawToFile(drawing, '/tmp/board.png', fmt='PNG')
                image_path = "/tmp/board.png"
                img = Image.open(image_path)
                new_image = img.resize((172, 172))
                third_image = new_image.crop((-108, 0, 172 + 108, 172))
                third_image.save('/tmp/answer.png')
                image = yandex.downloadImageFile('/tmp/answer.png')
                response['response']['card'] = {}
                response['response']['card']['image_id'] = image["id"]
                response['response']['card']['type'] = "BigImage"
                response['response']['card']['title'] = "Шахматы"
                response['response']['card']['description'] = random.choice(["Да начнётся игра!", "Удачной игры!"])
                response["response"]["text"] = random.choice(["Да начнётся игра!", "Удачной игры!"])
            elif any([i == "случайный" for i in qq.split()]):
                # games[event['session']['user_id']][1] = "random"
                response['response'][
                    'text'] = 'Эта ветка навыка ещё не закончена! Совсем скоро вы сможете поиграть с человеком'
                response['response']['buttons'] = [{'title': "Друг", 'hide': True},
                                                   {'title': "Компьютер", 'hide': True},
                                                   {'title': "Случайный игрок", 'hide': True}]
            else:
                response['response']['text'] = "Такого варианта у меня ещё нет. Выберите что то другое"
                response['response']['buttons'] = [{'title': "Друг", 'hide': True},
                                                   {'title': "Компьютер", 'hide': True},
                                                   {'title': "Случайный игрок", 'hide': True}]

        elif games[event['session']['user_id']][0] == 'chess' and games[event['session']['user_id']][1] == 'ai':
            qq = rustochess(qq)
            if qq not in [str(i) for i in sessionStorage[event['session']['user_id']].legal_moves]:
                response['response']['text'] = random.choice(
                    ["Неправильный ход. Говорите в формате А 2 на А4, либо вводите a2a4",
                     "Неправильно! Вводите в формате b2b4, либо говорите Б 2 на Б 4"]) + qq
                return response
            lst = amove(qq, aiboards[event['session']['user_id']])
            sessionStorage[event['session']['user_id']].push_uci(qq)
            sessionStorage[event['session']['user_id']].push_uci(lst[0])
            aiboards[event['session']['user_id']] = lst[1]
            response["response"]["text"] = "Противник сходил " + lst[0] + ". Ваш ход"
            board_svg = chess.svg.board(board=sessionStorage[event['session']['user_id']]).encode('utf-8')
            with open("/tmp/board.svg", "wb") as f:
                f.write(board_svg)
            drawing = svg2rlg('/tmp/board.svg')
            renderPM.drawToFile(drawing, '/tmp/board.png', fmt='PNG')
            image_path = "/tmp/board.png"
            img = Image.open(image_path)
            new_image = img.resize((172, 172))
            third_image = new_image.crop((-108, 0, 172 + 108, 172))
            third_image.save('/tmp/answer.png')
            image = yandex.downloadImageFile('/tmp/answer.png')
            response['response']['card'] = {}
            response['response']['card']['image_id'] = image["id"]
            response['response']['card']['type'] = "BigImage"
            response['response']['card']['title'] = "Шахматы"
            response['response']['card']['description'] = random.choice(["Отличный ход!", "Следующий ход!"])
            # response["response"]["text"] = printchessboard(str(sessionStorage[event['session']['user_id']]))
        else:
            response['response']['text'] = "Такого варианта у меня ещё нет. Выберите что то другое"
            response['response']['buttons'] = [{'title': "Друг", 'hide': True}, {'title': "Компьютер", 'hide': True},
                                               {'title': "Случайный игрок", 'hide': True}]
    else:
        if any([i in ("помощь", "что ты уметь", "подсказать") for i in qq.split()]):
            otv = random.choice([
                                    "Вы можете начать игру с другом, компьютером, или случайным человеком. Либо вы можете посмотреть свой рейтинг по команде профиль",
                                    "В данном навыке вы можете играть в шахматы с другом, компьютером, или случайным человеком. Также вы можете зайти в свой профиль и увидеть статистику",
                                    "Я умею запускать с другом, компьютером, или случайным человеком. Либо показать ваш рейтинг по команде профиль"])
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
            response['response']['card']['description'] = random.choice(
                ["Выберите соперника: друг, компьютер, или случайный игрок",
                 "C кем хотите играть? С другом, компьютером, или случайным игроком"])
            response['response']['buttons'] = [{'title': "Друг", 'hide': True}, {'title': "Компьютер", 'hide': True},
                                               {'title': "Случайный игрок", 'hide': True}]
            response['response']['text'] = "Выберите соперника: друг, компьютер, или случайный игрок"
        elif any([i in ('выход', 'завершить', 'выйти') for i in qq.split()]):
            response['response']['text'] = "Буду ждать вас снова!"
            response['response']["end_session"] = True
        else:
            response["response"]["text"] = random.choice(["Извините, я вас не понимаю. Попробуйте попросить помощь",
                                                          "Я не знаю таких команд. Попробуйте спросить что я умею",
                                                          "Увы, на такое меня не программировали. Попросите помощи"])
            response['response']['buttons'] = [{"title": "Помощь", "hide": True}, {"title": "Играть", "hide": True},
                                               {"title": "Профиль", "hide": True}]
    return json.dumps(response)


port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)