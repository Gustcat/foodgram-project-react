# Foodgram
Веб-сервер, который даст возможность поделиться своими рецептами, подписаться на других авторов, выбирать отдельные рецепты в избранное. Также можно добавить рецепты в список покупок и скачать файл с ингредиентами и их количеством, необходимых для приготовления рецептов из списка покупок.
## Как запустить проект
Клонировать репозиторий
```
git clone git@github.com:Gustcat/foodgram-project-react.git
```
Если Nginx ещё не установлен на сервере, установите его:
```
sudo apt install nginx -y
```
Запустите Nginx командой:
```
sudo systemctl start nginx
```
Откройте конфигурацию nginx и добавьте туда следующие параметры(вместо foodgram-antgust.hopto.org укажите ip или домен своего сервера):
```
$ sudo nano /etc/nginx/sites-enabled/default
server {
    server_name foodgram-antgust.hopto.org;
    server_tokens off;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:10000;
        client_max_body_size 20M;
    }
}
```
Также можно получить SSL-сертфикат с помощью Certbot.
В корневой директории необходимо создать файл .env со следущими переменными:
```
DEBUG=False
POSTGRES_DB=<имя базы данных>
POSTGRES_USER=<имя пользователя базы данных>
POSTGRES_PASSWORD=<пароль пользователя базы данных>
DB_HOST=db (указать это значение)
DB_PORT=5432 (указать это значение)
ALLOWED_HOSTS=127.0.0.1, localhost, <ip сервера или домен>
```
В корневой директории проекта запустите сборку сети контейнеров(в режиме демона):
```
sudo docker compose -f docker-compose.production.yml up -d
```
Сделайте миграции в контейнере backend:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
Соберите статику в контейнере backend:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
Скопируйте статику в том static:
```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```
Заполните таблицы Ingredient и Tag готовыми данными
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_tags
```
## Список используемых библиотек
Необходимые зависимости для приложения backend находятся в файле /backend/requirements.txt. Также используется gunicorn==20.1.0, который устанавливается в контейнер backend при его создании.

Необходимые зависимости для приложения backend находятся в файле /frontend/package.json. Также используется акет http-server, который устанавливается в контейнер frontend при его создании.
## Автор
https://github.com/Gustcat

сайт: foodgram-antgust.hopto.org
username: admin
password: admin1234