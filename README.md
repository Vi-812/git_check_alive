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
<ul>
<li><b>server.py</b> - запускает приложение на сервере</li>
<li><b>cli.py</b> - запускает приложение из командной строки</li>
<li><b><u>frontend</u></b></li>
<ul>
<li><b>views.py</b> - содержит маршруты, принимает запросы пользователей</li>
<li><b>models.py</b> - содержит представления базы данных (sqlalchemy)</li>
<li><b>forms.py</b> - содержит представления формы для WebUI (wtforms)</li>
<li><b>__init__.py</b> - содержит информацию модуля</li>
<li><b><u>templates</u></b></li>
<ul>
<li><b>base.html</b> - содержит шаблон всех страниц (jinja2)</li>
<li><b>index.html</b> - главная страница с формой для запроса</li>
<li><b>values.html</b> - содержит описания значений ответа (resp_json)</li>
<li><b>api_help.html</b> - синтаксис запросов к REST API</li>
<li><b>contact.html</b> - контакты</li>
</ul>
</ul>
<li><b><u>dto</u></b></li>
<ul>
<li><b>received_request.py</b> - DTO входящего запроса</li>
<li><b>request_response.py</b> - DTO ответа на запрос</li>
</ul>
<li><b><u>backend</u></b></li>
<ul>
<li><b>database.py</b> - осуществляет работу с базой данных</li>
<li><b>json_preparation.py</b> - формирует конечное представление resp_json, сохраняет redis</li>
<li><b><u>analytic</u></b></li>
<ul>
<li><b>github_api_client.py</b> - принимает запрос и руководит его обработкиой</li>
<li><b>use_graphql.py</b> - отвечает за отправку запросов к GraphQL GitHub</li>
<li><b>bug_issues.py</b> - отвечает за обработку bug-вопросов (полученных от GitHub)</li>
<li><b>functions.py</b> - содержит вспомогательные функции</li>
<li><b>errors_handler.py</b> - содержит обработчики ошибок</li>
</ul>
</ul>
<li><b><u>tests</u></b></li>
<ul>
<li><b>cli_test.py</b> - тестирует использование программы через CLI</li>
<li><b>working_test.py</b> - для оперативного тестирования при разработке, тестирование ошибок</li>
<li><b>scraping.py</b> - собирает репозитории для тестирования с "habr.com/ru/post/453444/", сохраняет в файл "testing_list.txt"</li>
<li><b>testing_list.txt</b> - содержит репозитории для тестирования с помощью server_api_test.py</li>
<li><b>server_api_test.py</b> - отвечает за нагрузочное тестирование через REST API</li>
</ul>
<li><b><u>other</u></b></li>
<ul>
<li><b>update.sh</b> - набор bash команд для обновления на сервере</li>
<li><b>program_structure</b> - схема программы для README.md</li>
</ul>
</ul>
<br>
