<div align="center">

<h1>Чёрный список</h1>

<p>Публичный реестр Telegram ID и email, заблокированных за нарушения:<br>
шаринг подписок, накрутка рефералов, абуз триалок, скам, слив ключей и прочие злоупотребления сервисом.</p>

<p>
  <a href="https://github.com/remnashop/blacklist/actions/workflows/check.yml"><img src="https://img.shields.io/github/actions/workflow/status/remnashop/blacklist/check.yml?branch=main&label=check&logo=github&logoColor=white" alt="check"></a>
  <a href="https://github.com/remnashop/blacklist/actions/workflows/export.yml"><img src="https://img.shields.io/github/actions/workflow/status/remnashop/blacklist/export.yml?branch=main&label=csv%20export&logo=github&logoColor=white" alt="csv export"></a>
  <a href="blacklist.txt"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fremnashop%2Fblacklist%2Fmain%2Fbadges%2Fentries.json" alt="entries"></a>
  <a href="https://github.com/remnashop/blacklist/commits/main"><img src="https://img.shields.io/github/last-commit/remnashop/blacklist?label=last%20commit" alt="last commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/remnashop/blacklist?label=license" alt="license"></a>
</p>

<p>
  <a href="blacklist.txt"><code>blacklist.txt</code></a> ·
  <a href="blacklist.csv"><code>blacklist.csv</code></a> ·
  <a href="../../issues/new?template=blacklist.yml">подать заявку</a>
</p>

</div>

## Файлы

| файл | роль | правится руками |
|:--|:--|:--:|
| [`blacklist.txt`](blacklist.txt) | реестр: ID или email, причина, пруф | да |
| [`blacklist.csv`](blacklist.csv) | тот же список без комментариев, колонка `entry` | нет, генерируется |
| [`scripts/add_ban.py`](scripts/add_ban.py) | вставка записи на нужное место, `--check`, `--sync` | — |
| [`scripts/export_csv.py`](scripts/export_csv.py) | сборка csv из txt | — |
| [`scripts/entries_badge.py`](scripts/entries_badge.py) | счётчик для бейджа в шапке | — |
| [`scripts/sources.txt`](scripts/sources.txt) | внешние списки для `--sync` | да |

## Формат записи

По одной записи на строку: сначала Telegram ID по возрастанию, затем email по алфавиту (в нижнем регистре). Через `#` — причина и, если есть, ссылка на доказательство.

```
2593769 # Шаринг
143114631 # Скам
abuser@example.com # Абуз триалки
```

- Один адрес на одну сущность: регистр и алиасы почтовых сервисов (`+тег`, точки в Gmail, домены-синонимы Gmail, Яндекса и iCloud) remnashop сводит к одному ящику сам.
- Служебные аккаунты Telegram (`777000`, `GroupAnonymousBot` и подобные) в список не попадают: это не нарушители, а платформа.
- Строка, которая не ID и не email, и дубликат записи валят сборку с номером строки — мусор не теряется молча.
- Порядок проверяется автоматически: `add_ban.py --check` в CI падает на нарушенной сортировке.

## Интеграция

Список с причинами:

```
https://raw.githubusercontent.com/remnashop/blacklist/main/blacklist.txt
```

Тот же список без комментариев — одна колонка `entry`, без `#`, без BOM, LF:

```
https://raw.githubusercontent.com/remnashop/blacklist/main/blacklist.csv
```

Для панелей и скриптов, которые не умеют разбирать комментарии, берите csv: он собирается из txt автоматически и руками не правится.

## Как это работает

```
blacklist.txt  ──push в main──►  workflow export
      ▲                                 │
      │                                 ├──► blacklist.csv         коммит github-actions[bot]
      │                                 └──► badges/entries.json   счётчик для бейджа
      │
      └── правка: scripts/add_ban.py, PR или форма заявки
```

На pull request тот же workflow ничего не пишет: он запускает `export_csv.py --check` и падает, если csv разъехался с txt или в txt продублирована запись. Устаревший csv не может попасть в `main` незаметно.

## Как добавить нарушителя

Через [форму заявки](../../issues/new?template=blacklist.yml): числовой Telegram ID или email, причина и доказательства. Без пруфов заявку не рассматриваем.

Мейнтейнер вносит одобренную заявку скриптом — тот сам ставит запись на нужное место и отказывается дублировать существующую:

```console
$ python3 scripts/add_ban.py 123456789 "абуз триалки"
```

Массовый импорт из внешнего списка или по расписанию:

```console
$ python3 scripts/add_ban.py --sync https://example.com/ids.txt
```

## Проверки

| команда | что ловит | где запускается |
|:--|:--|:--|
| `add_ban.py --selftest` | поломку самого скрипта вставки | `Check`, каждый push и PR |
| `add_ban.py --check` | дубликаты, нарушение порядка, невалидную запись | `Check`, каждый push и PR |
| `export_csv.py --check` | расхождение csv с txt, дубликат или мусор в записи | `export`, каждый PR |

Перед PR прогоните оба `--check` локально:

```console
$ python3 scripts/add_ban.py --check
ok: 14843 entries, sorted, no duplicates
$ python3 scripts/export_csv.py --check
ok: blacklist.csv is up to date
```

Если csv отстал от txt — `python3 scripts/export_csv.py` пересоберёт его.

## Авторство

Изначальный список позаимствован из проекта [ban-vpn](https://github.com/Blin4ickUSE/ban-vpn). Репозиторий распространяется по лицензии [MIT](LICENSE).
