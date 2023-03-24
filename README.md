# GIT CHECK ALIVE

Данный pet-проект предназначен для аналитики репозиториев на GitHub. Принимая имя (путь/ссылку) репозитория, собирает 
данные, проводит их аналитику и выдает отчет. В отчете вы можете увидеть - как давно происходило обновление репозитория, 
обновление кода, статистику PR, обширную аналитику по bug-вопросам и многое другое.
<a href="https://isgitalive.karo-dev.ru/values">Полный список можно посмотреть тут</a>. Список может быть расширен по 
вашим предложениям и пожеланиям.

(<a href="https://isgitalive.karo-dev.ru/">WebUI</a></li>
/
<a href="https://isgitalive.karo-dev.ru/rest-api">API</a></li>)
## Варианты использования
### CLI
<ol>
<li>Скопируйте проект себе на компьютер (папка "frontend" в этом случае не обязательна)</li>
<li>Перейдите в папку с программой</li>
<li>Установите зависимости

`python -m pip install -r requirements.txt`</li>
<li>Переименуйте файл ".env.example" в ".env"

`cp .env.example .env`</li>
<li>Вставьте в файл ".env" все необходимые данные</li>
<li>Запустите файл cli.py в формате

`python3 cli.py ссылка_на_репозиторий`</li>
</ol>

### WebUI
<ol>
<li>Перейдите на <a href="https://isgitalive.karo-dev.ru/">наш сайт</a></li>
<li>Вставьте ссылку на репозиторий</li>
<li>Нажмите кнопку "Анализ"</li>
</ol>

### REST API - GET и POST 
<ol>
<li>Сформируйте body запроса, headers при необходимости</li>
<li>Отправьте запрос на необходимый эндпоинт</li>
</ol>
<a href="https://isgitalive.karo-dev.ru/rest-api">Подробная информация о REST API запросах</a>

## Вводные данные
### name
Ссылка на репозиторий, либо "владелец/имя_репозитория". 
Примеры "https://github.com/Vi-812/git_check_alive" или "vi-812/git_check_alive"

### skipCache 
Позволяет игнорировать загрузку данных из базы и получить свежую аналитику (при значении true), 
по умолчанию имеет значение false

### token
Позволяет передать ваш Token<br>
<b>CLI</b> - автоматически передает токен из файла ".env"<br>
<b>WebUI</b> - не имеет возможности передачи токена<br>
<b>API GET</b> - токен возможно передать через headers запроса (необязательно)<br>
<b>API POST</b> - токен возможно передать через body запроса (необязательно)<br>

### Файл .env
<ul>
<li><b>TOKEN</b> - ваш GitHub токен, <a href="https://github.com/settings/tokens">сгенерировать токен можно тут</a> 
(read only достаточно)</li>
<li><b>SECRET_KEY</b> - произвольный секретный код, необходим для работы сервера в WebUI интерфейсе 
(можно не заполнять)</li>
<li><b>HASHER</b> - произвольный секретный код, необходим для хеширования токена в базе данных</li>
<li><b>REQUIREPASS</b> - пароль для доступа к Redis, при отсутствии пароля сохранение в Redis 
производиться не будет</li>
</ul>

## Структура проекта
<br>
<div align="left">

![Структура проекта](/other/program_structure.png)

</div>

### git_check_alive
* **server.py** - запускает приложение на сервере
* **cli.py** - запускает приложение из командной строки
* **FRONTEND**
  * **views.py** - содержит маршруты, принимает запросы пользователей
  * **models.py** - содержит представления базы данных (sqlalchemy)
  * **forms.py** - содержит представления формы для WebUI (wtforms)
  * **\_\_init__.py** - содержит информацию модуля
  * **TEMPLATES**
    * **base.html** - содержит шаблон всех страниц (jinja2)
    * **index.html** - главная страница с формой для запроса
    * **values.html** - содержит описания значений ответа (resp_json)
    * **api_help.html** - синтаксис запросов к REST API
    * **contact.html** - контакты
* **DTO**
  * **received_request.py** - DTO входящего запроса
  * **request_response.py** - DTO ответа на запрос
* **BACKEND**
  * **database.py** - осуществляет работу с базой данных
  * **json_preparation.py** - формирует конечное представление resp_json, сохраняет redis
  * **ANALYTIC**
    * **DB** - папка базы данных
    * **github_api_client.py** - принимает запрос и руководит его обработкиой
    * **use_graphql.py** - отвечает за отправку запросов к GraphQL GitHub
    * **bug_issues.py** - отвечает за обработку bug-вопросов (полученных от GitHub)
    * **functions.py** - содержит вспомогательные функции
    * **errors_handler.py** - содержит обработчики ошибок
* **TESTS**
  * **cli_test.py** - тестирует использование программы через CLI
  * **working_test.py** - для рабочего повседневного тестирования
  * **scraping.py** - собирает репозитории для тестирования с "habr.com/ru/post/453444/", сохраняет в файл "testing_list.txt"
  * **testing_list.txt** - содержит репозитории для тестирования с помощью server_api_test.py
  * **server_api_test.py** - отвечает за нагрузочное тестирование через REST API
  * **PYTEST**
    * **test_to_date.py** - тестирует функцию to_date с помощью PyTest
    * **test_scraping.py** - тестирует работу scraping.py с помощью PyTest
    * **conftest.py** - очищает файл testing_list.txt для работы test_scraping.py
* **OTHER**
  * **update.sh** - набор bash команд для обновления на сервере
  * **program_structure** - схема программы для README.md

<br>
