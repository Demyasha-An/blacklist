<div align="center">

<h1>Чёрный список</h1>

<p>Telegram ID и email, заблокированные в remnashop за нарушения:<br>
шаринг подписок, накрутка рефералов, абуз триалок, скам, слив ключей.</p>

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
  <a href="../../issues/new?template=blacklist.yml"><b>подать заявку</b></a>
</p>

</div>

## Подключение

Список доступен в двух видах — один и тот же набор записей, обновляются одновременно.

**С причинами** — для чтения и разбора:

```
https://raw.githubusercontent.com/remnashop/blacklist/main/blacklist.txt
```

```
2593769 # Шаринг
abuser@example.com # Абуз триалки
```

**Без комментариев** — для панелей, ботов и скриптов:

```
https://raw.githubusercontent.com/remnashop/blacklist/main/blacklist.csv
```

```
entry
2593769
13289882
```

Одна колонка `entry`, по одной записи на строку: сначала Telegram ID по возрастанию, затем email по алфавиту. Без `#`, без BOM, LF.

Оба файла живые: запись появляется сразу после проверки заявки, csv пересобирается за txt автоматически. Число в бейдже `entries` — реальный размер списка.

## Как подать заявку

[**Открыть форму заявки →**](../../issues/new?template=blacklist.yml)

Форма спросит четыре вещи:

| поле | что указать |
|:--|:--|
| Telegram ID или email | числовой ID (не `@username`) или почта нарушителя |
| Причина | шаринг подписки, накрутка рефералов, абуз триалки, скам, слив ключей или другое |
| Детали | что именно произошло |
| Доказательства | переписка, скриншоты, логи — без них заявку не рассматриваем |

Дальше мейнтейнер проверяет заявку и, если нарушение подтвердилось, вносит запись в список. Статус видно в самой заявке: она остаётся открытой до решения.

Что не принимаем:

- служебные аккаунты Telegram (`777000`, `GroupAnonymousBot` и подобные) — это платформа, а не нарушитель;
- заявки без доказательств;
- адреса, которые уже есть в списке — такую заявку бот закроет автоматически и напишет причину из списка.

## Меня добавили ошибочно

[Откройте issue](../../issues/new) и приложите свой ID или email с объяснением, почему запись неверна. Мейнтейнеры перепроверят и уберут запись, если она попала в список по ошибке.

## Для мейнтейнеров

Как устроены скрипты, как собирается csv, что проверяет CI и как вносить записи — в [CONTRIBUTING.md](CONTRIBUTING.md).

## Авторство

Изначальный список позаимствован из проекта [ban-vpn](https://github.com/Blin4ickUSE/ban-vpn). Репозиторий распространяется по лицензии [MIT](LICENSE).
