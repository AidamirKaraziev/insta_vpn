# TODO создать файл back_ground tasks в папке utils разместить там все функции utils

from fastapi import FastAPI, BackgroundTasks
from time import sleep

app = FastAPI()


def test_print():
    sleep(5)
    print("Тестовая писанина")
