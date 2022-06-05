import sys
import requests
import time
import urllib
from config import *


request = 'https://api.vk.com/method/{0}?v=5.131&{1}&access_token={2}'


def get_main_info():
    user_info = requests.get(request.format("users.get", f"user_id={user_id}&fields=city, bdate, counters", access_token))
    time.sleep(2)
    user_info = user_info.json()['response'][0]
    try:
        return "Информация о странице: \n" + "\n" \
           + "Имя: " + str(user_info["first_name"]) + "\n" \
           + "Фамилия: " + str(user_info["last_name"]) + "\n" \
           + "Дата рождения: " + user_info["bdate"] + "\n" \
           + "Город: " + user_info["city"]["title"] + "\n" \
           + "Подписчики : " + str(user_info["counters"]["followers"]) + "\n" \
           + "\n"

    except requests.exceptions.ConnectionError:
        print("Connection error")
    except:
        print("Wrong access data")


def get_list_user_friends():
    main_request = requests.get(request.format("friends.get", f"user_id={user_id}", access_token))
    time.sleep(2)
    main_request = main_request.json()['response']['items']

    friends_request = requests.get(
        request.format("users.get", f"user_id={main_request}", access_token))

    friends_info = ""
    for friend in friends_request.json()['response']:
        friends_info += f"* {friend['first_name']} {friend['last_name']}\n"
    return friends_info


def download_photos() -> None:
    result = []
    photos_info = requests.get(request.format("photos.get", f"user_id={user_id}&album_id=profile", access_token))
    time.sleep(2)
    photos_info = photos_info.json()['response']['items']
    time.sleep(2)
    for i in photos_info:
        result.append(i['sizes'][-1]['url'])
        time.sleep(1)
    for i, v in enumerate(result):
        urllib.request.urlretrieve(f"{v}", f"./images/{i}.jpg")
        time.sleep(1)


def main():
    print(get_main_info())
    print(f"Список друзей:\n{get_list_user_friends()}")
    download_photos()


if __name__ == '__main__':
    main()

