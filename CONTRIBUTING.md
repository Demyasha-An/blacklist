# Как устроен репозиторий

Всё, что нужно мейнтейнеру: где лежат данные, как они превращаются в csv, что проверяет CI.

## Файлы

| файл | роль | правится руками |
|:--|:--|:--:|
| [`blacklist.txt`](blacklist.txt) | реестр: ID или email, причина, пруф | да, единственный источник правды |
| [`blacklist.csv`](blacklist.csv) | тот же список без комментариев, колонка `entry` | нет, генерируется |
| [`scripts/add_ban.py`](scripts/add_ban.py) | вставка записи на нужное место, `--check`, `--sync`, `--selftest` | — |
| [`scripts/export_csv.py`](scripts/export_csv.py) | сборка csv из txt | — |
| [`scripts/entries_badge.py`](scripts/entries_badge.py) | счётчик для бейджа в README | — |
| [`scripts/check_issue.py`](scripts/check_issue.py) | проверка заявки: закрыть, если адрес уже в списке | — |
| [`scripts/sources.txt`](scripts/sources.txt) | внешние списки для `--sync` | да |
| [`badges/entries.json`](badges/entries.json) | цифра для endpoint-бейджа shields | нет, генерируется |
| [`.github/workflows/`](.github/workflows) | `check`, `export`, `sync` | да |
| [`.github/ISSUE_TEMPLATE/blacklist.yml`](.github/ISSUE_TEMPLATE/blacklist.yml) | форма заявки | да |

## Формат `blacklist.txt`

По одной записи на строку: сначала Telegram ID по возрастанию, затем email по алфавиту (в нижнем регистре). Через `#` — причина и, если есть, ссылка на доказательство.

```
2593769 # Шаринг
143114631 # Скам
abuser@example.com # Абуз триалки
```

- Один адрес на одну сущность: регистр и алиасы почтовых сервисов (`+тег`, точки в Gmail, домены-синонимы Gmail, Яндекса и iCloud) remnashop сводит к одному ящику сам.
- Служебные аккаунты Telegram (`777000`, `GroupAnonymousBot` и подобные) в список не попадают: это не нарушители, а платформа.
- Мусор и дубликаты не проходят молча: обе сборки падают с номером строки.

## Скрипты

### `add_ban.py` — внести запись

Ставит запись на нужное место по сортировке и отказывается дублировать существующую:

```console
$ python3 scripts/add_ban.py 123456789 "абуз триалки"
$ python3 scripts/add_ban.py someone@example.com "скам"
```

ID нормализуются (`0008999999999` = `8999999999`), email приводится к нижнему регистру — повтор в другом написании тоже отклоняется: `8999999999 is already in the list`.

Проверка файла целиком:

```console
$ python3 scripts/add_ban.py --check
ok: 14843 entries, sorted, no duplicates
```

На нарушение порядка — `out of order: N`, на повтор — `duplicates: N` и список адресов.

Массовый импорт: `--sync <url|file>` добавляет только отсутствующие записи, повторный прогон даёт `added 0 entries`. Служебные аккаунты Telegram и ID больше 10^10 отбрасываются при разборе источника и попадают в вывод отдельной строкой:

```console
$ python3 scripts/add_ban.py --sync https://raw.githubusercontent.com/BEDOLAGA-DEV/VPN-BLACKLIST/main/blacklist.txt
added 0 entries from 1213 in source
skipped 2 not bannable: 55610547115, 777000
```

Те же значения не пройдут и через одиночное добавление — `777000 is not a bannable Telegram ID`.

Самопроверка скрипта: `--selftest`.

### `export_csv.py` — собрать csv

```console
$ python3 scripts/export_csv.py
blacklist.txt: 14843 entries (ids: 14843, emails: 0)
blacklist.csv: written, 14843 rows
```

`--check` ничего не пишет и возвращает 1, если csv разъехался с txt:

```console
$ python3 scripts/export_csv.py --check
ok: blacklist.csv is up to date
```

Строка, которая не ID и не email, и повтор записи валят сборку с номером строки:

```
blacklist.txt:14846: not a Telegram ID or email: 'not-an-id'
blacklist.txt:3: duplicate of line 2: 2593769
```

### `entries_badge.py` — обновить счётчик

Считает строки в `blacklist.csv` и переписывает `badges/entries.json` (endpoint-бейдж shields). Запускается workflow `export` после сборки csv, руками не нужен.

### `check_issue.py` — закрыть дубль заявки

Берёт из заявки поле «Telegram ID или email», нормализует так же, как список (`0002593769` = `2593769`, email в нижнем регистре), и если адрес уже есть — комментирует причиной из `blacklist.txt` и закрывает issue как `not planned`. Обработчик — workflow `issue check`, прав на запись к содержимому у него нет.

Не трогает:

- issue без заголовка `[BAN]` и без метки `blacklist` — то есть всё, что открыто не через форму;
- обращения со словами «апелляция», «ошибочно», «разбан», «неверно» — их разбирает человек;
- заявки без распознанного ID или email.

Ручной перезапуск: `gh workflow run issue-check.yml -f issue_number=42`. Локально — `python3 scripts/check_issue.py 42 --dry-run` (ничего не пишет) или `--body-file body.md --title "[BAN] …"` для офлайн-проверки.

### `sources.txt` и `sync`

В `scripts/sources.txt` — URL внешних списков, по одному на строку. Workflow `Sync` раз в неделю (понедельник, 05:00 UTC) и по кнопке прогоняет `add_ban.py --sync` по каждому адресу, пересобирает `blacklist.csv` и `badges/entries.json` и открывает PR из ветки `sync/upstream`. Причины у таких записей — от источника, перед мержем их стоит просмотреть.

В PR приезжают все четыре файла, поэтому проверка `export` на нём зелёная. Ветку `sync/upstream` workflow перезаписывает принудительно: если в открытом PR что-то не так, следующий прогон соберёт его заново из свежего `main`.

PR создаёт `github-actions[bot]`, поэтому GitHub не запускает на нём проверки сам — прогоны висят в статусе `action_required`, пока мейнтейнер не нажмёт «Approve and run» на странице Actions или не одобрит через API:

```console
$ gh api -X POST repos/remnashop/blacklist/actions/runs/<run_id>/approve
```

Чтобы этого не делать, нужен PAT мейнтейнера в секрете и `token:` в `actions/checkout` — тогда PR создаётся от живого пользователя и проверки идут сразу.

## CI

| workflow | когда | что делает |
|:--|:--|:--|
| `Check` | каждый push и PR | `add_ban.py --selftest`, затем `--check`: порядок, дубликаты, формат |
| `export` | push в `main` (txt или скрипты) | пересобирает `blacklist.csv` и `badges/entries.json`, коммитит ботом, если что-то изменилось |
| `export` | PR (txt, csv, скрипты) | только `export_csv.py --check`, файлы не пишет |
| `Sync` | по расписанию и вручную | импорт из внешних списков, пересборка csv и бейджа, PR из `sync/upstream` |
| `issue check` | открытие, правка, переоткрытие issue | закрывает заявку, если адрес уже в списке |

Схема:

```
blacklist.txt  ──push в main──►  workflow export
      ▲                                 │
      │                                 ├──► blacklist.csv         коммит github-actions[bot]
      │                                 └──► badges/entries.json   счётчик для бейджа
      │
      └── правка: scripts/add_ban.py, PR или форма заявки
```

## Локально перед PR

```console
$ python3 scripts/add_ban.py --check
ok: 14843 entries, sorted, no duplicates
$ python3 scripts/export_csv.py --check
ok: blacklist.csv is up to date
```

Если правили txt, а csv не пересобирали — CI на PR упадёт: сначала `python3 scripts/export_csv.py`, потом коммит обоих файлов.

## Данные и лицензия

Записи вносятся только по подтверждённым заявкам с доказательствами. Репозиторий распространяется по лицензии [MIT](LICENSE); изначальный список — из проекта [ban-vpn](https://github.com/Blin4ickUSE/ban-vpn).
