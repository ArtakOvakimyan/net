import os
import time
import json


class Cacher:
    def __init__(self):
        """Инициализация данных"""
        self.file_name = 'cache.json'
        self.data = self.load_cache()

    def add_record(self, name, record_type, value):
        """Запись данных в кэш"""

        self.data[str((name, record_type))] = [value, time.time()]

    def get_record(self, key):
        """Извлечение данных из кэша"""
        if str(key) in self.data:
            return self.data[str(key)]
        return None

    def dump_cache(self):
        """Сериализация кэша"""
        with open(self.file_name, 'w') as file:
            json.dump(self.data, file)

    def load_cache(self):
        """Десериализация кэша"""
        with open(self.file_name, 'r') as file:
            if os.stat(self.file_name).st_size != 0:
                data = self.refresh(json.load(file))
            else:
                data = {}
        print('Кэш загружен')
        return data

    @staticmethod
    def refresh(records: dict):
        """Удаление устаревших записей"""
        for k, v in list(records.items()):
            creation_time = v[0][0][2]
            ttl = v[1]
            if time.time() - creation_time > ttl:
                records.pop(k)
        return records
