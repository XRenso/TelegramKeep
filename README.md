# TelegramKeep - улучшенное сохранение сообщений
Данный телеграм бот поможет вам не просто сохранить ваши данные в телеграм, но и упорядочить их по папкам, а также выводить определенные сообщения, которые вам нужны.

## Установка
Для установки нужно будеть скачать репозитироий и создать файл в корне с расширением `.env`. В нем должны находится 2 переменные:
<ul>
<li>TOKEN - токен бота, что получается у <i>BotFather</i></li> 
<li>MONGO - URI адрес Mongodb</li> </ul>

После этого нужно установить все зависимости из файла `requirements.txt` при помощи команды при помощи команды `pip install`.

## Функционал
Что же позволяет данный бот?
<ol>
  <li>Сохранение всех типов сообщений в телеграм</li>
  <li>Упорядочивание информации по папкам</li>
  <li>Несколько фильтров возвращение сообщений - все, последние(<i>число указываете сами</i>), определенное</li>
</ol>

## Подерживаемые форматы в боте
<ol>
  <li>Видео</li>
  <li>Аудио</li>
  <li>Текст</li>
  <li>GIF</li>
  <li>Стикеры</li>
  <li>Голосовые сообщения и видеокружки</li>
  <li>Документы</li>
</ol>

## Примеры работы
#### Добавление заметок в папку

![Adding to folder](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2l4djMxOW1rOWRlMTA1MXl0djUzZGhtaWI5Y3lmdDNscXIybHIwcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aOL8KCUQKAUDRtZ6vS/giphy-downsized.gif)

#### Создание папок
![Create folder](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHpqN25zeHRlbjUyMTY0aGg2MmZpejFncjFhMXo5ZzF1djBhcHI3ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Rp8piXPnLBqcDEVeKW/giphy.gif)

