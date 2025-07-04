# Сравниваем вакансии программистов

Эта программа собирает и выводит статистику по вакансиям для различных языков программирования в Москве с двух популярных сайтов: SuperJob и HeadHunter (HH).

Статистика выводится  в  виде  таблиц.

![](https://github.com/IrinaQA423/gists1/blob/main/Screenshot_25.png?raw=true)

## Как установить

1. Установите на компьютер `Python3`.

2. Скачайте все файлы проекта на свой компьютер.

```
https://github.com/IrinaQA423/vacancy_stats.git
```

3. Установите зависимости.

```sh
pip install -r requirements.txt
```

### Как получить токен с сайта https://api.superjob.ru/?

1. Получите `SJ_SECRET_KEY`, зарегистрировав свое  приложение.

### Где  хранить чувствительные данные?

В корне проекта создайте файл `.env` и поместите в него `SJ_SECRET_KEY`.

![](https://github.com/IrinaQA423/gists1/blob/main/Screenshot_24.png?raw=true)

## Как запустить  программу?

1. Запустите файл `vacancy_stats.py`.

```sh
python vacancy_stats.py 
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org).
