# grouper

**_Сервис группировки похожих текстов_**

**Для запуска приложения в docker контейнере:**

`docker-compose -f _CI/docker-compose.yml build`

`docker-compose -f _CI/docker-compose.yml up`

**Для запуска приложения локально:**

_1. установить зависимости_

    pip install -r requirements.txt

_2. запустить сервер redis_

    redis-server

_1. запустить проект_

    uvicorn app.grouper.main:application --host 0.0.0.0 --port 8080 --workers 4

**Для запуска unit-тестов:**

_1. установить pytest_
    
    pip install pytest

_2. запустить прохождение тестов_

    pytest


**URL:**

    /docs - документация API


