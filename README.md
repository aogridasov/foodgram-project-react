# PROD SERVER_ADRESS: https://ag-foodgram.sytes.net/

# Foodgram
Foodgram это сайт для любителей готовить. 
Делитесь своими рецептами, подписывайтесь на понравившихся авторов, добавляйте рецепты в список покупок, который можно удобно вывести в отдельный PDF файл.  
  
Реализованы: регистрация и аутентификация по токенам; добавление рецептов с картинками; филтрация по тегам; функции добавления в избранное и список покупок; подписки на авторов; автоматическая генерация PDF файла из списка покупок; модерация.  
  
Серверная часть работает на Ngnix, Gunicorn и PostgreSQL. Всё завернуто в контейнеры Docker, настроен SSL через letsencrypt.org  
  
Бэкенд к Foodgram был написан мной в рамках дипломного проекта Яндекс Практикума. Фронтенд, написанный на React, они любезно предоставили. Бэкенд взаимодействует с фронтендом через API (DRF).
  
**Технологии:** Django, Django REST Framework, Postgres, Nginx, Gunicorn, Docker
  
![foodgram_workflow](https://github.com/aogridasov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?event=push)
  
## Установка

### Версии стека
Подробнее в requirements.txt
```
Python 3.7.9
Django 3.2
Django REST Framework 3.12.4
Djoser 2.1.0
``` 

### Деплой
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:aogridasov/foodgram-project-react.git
``` 
Установить и активировать виртуальное окружение:
``` 
python3 -m venv env
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
``` 
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```

### Деплой на Docker
#### Стек: Nginx, Gunicorn, PostgreSQL

Необходимые библиотеки:
```
gunicorn==20.0.4
psycopg2-binary=2.8.6
```
Настроить проект для работы с PostgreSQL, gunicorn и Nginx.  
Корректно заполнить settings.py и .env  
Прописать тома для статики и медиа. Настроить это в settings.py и docker-compose.  

Шаблон наполнения .env файла для PostgreSQL:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

#### Запуск

Строим контейнеры:
```
docker-compose up -d build
```

Выполняем миграции, создаём админа и сохраняем статику в соответствующий том:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input

```

Отдельно прописываем команду для парсинга заготовленной CSV с ингредиентами из backend/foodgram/data/ :
```
docker-compose exec web python manage.py parseingredients
```


### Документация API
После запуска сервиса, подробную информацию о работе с API проекта со всеми эндпоинтами можно посмотреть в Redoc:
```
адрес-вашего-сервера/api/docs/
```
#### Пример запроса и ответа:
Запрос:
```
http://example/api/recipes/
```
Ответ:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
