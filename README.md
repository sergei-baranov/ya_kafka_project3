# Учебное приложение "упрощённый сервиса обмена сообщениями"

- Создайте систему обработки потоков сообщений с функциями блокировки пользователей и цензуры сообщений.
- Разверните систему с использованием Docker-сompose и настройте необходимые топики Kafka.

Реализация:
- сборка `Kafka` от `Confluent`,
- `python` (фреймворк `Faust` (`faust-streaming`)).

Содержание:
- [Как развернуть](#compose_up)
- [Как погасить ансамбль](#compose_down)
- [Запуск приложения](#start_app)
- [Отладка приложения](#debug_app)
- [Быстрый тест Happy Way](#happy_way_test)
- [Теперь передадим сообщение в неверной схеме](#test_bad_schema)
- [Работа с приложением через cli-команды](#cli_commands)
  - [Посмотреть список команд](#cli_commands_list)
  - [Давайте заблокируем слово "миска"](#cli_commands_block_word)
  - [Давайте посмотрим список заблокированных слов](#cli_commands_list_block_words)
- [Работа с приложением через http-api](#http_api)
  - [Спросим, заблокирована ли "миска"](#http_api_get_block_wordhttp_api_get_block_word)
  - [Спросим весь список заблокированных слов](#http_api_get_block_words)

## <a name="compose_up">Как развернуть</a>

Запустить ансамбль контейнеров:

```bash
sudo docker compose --env-file .env.793 up -d
```

Если что-то правили в приложении и надо пересобрать его:

```bash
sudo docker compose --env-file .env.793 up -d --build
```

Если хочется поиграться с другими версиями Кафки/Конфлюента - меняем значение `--env-file`
(но 4-ю Кафку не поддерживает либа `aiokafka`, которую использует `Faust`).

## <a name="compose_down">Как погасить ансамбль</a>

```bash
sudo docker compose --env-file .env.793 down
```

если надо при этом потереть volume-ы

```bash
sudo docker compose --env-file .env.793 down -v
```

## <a name="start_app">Запуск приложения</a>

Приложение уже запущено в контейнере.

Там прописана работа приложения в фоне через `supervisord`.
См. `DockerfilePython` и `supervisord.conf`.

См. тж. .

Убедимся, что приложение запустилось и работает:
- можно проверить логи контейнера,
- можно Web UI от `provectuslabs/kafka-ui`,
- можно web ui от Faust.

1. **Логи контейнера**:

```bash
...$ sudo docker logs ya_kafka_project3-python-app-1
```

тут Faust подробно всё расписывает, т.к. мы прописали запускаться как `-l INFO`.

2. **Web UI**:

**NB:** порт для http-ui - **8070** (если ничего не менять в `docker-compose.yml`).

если разворачивались на локалхосте:

```bash
http://localhost:8070/ui/clusters/kraft/all-topics
```

Тут должны быть видны несколько топиков, которые приложение создаёт при запуске
(релизация - через `signal` `app.on_after_configured.connect`, см. `app/messenger/messenger_core/signals.py`).

3. **Faust web ui**:

**NB:** порт для фонового приложения прописан **6077** (если ничего не менять в `supervisord.conf`).

См. например тут: [Спросим, заблокирована ли "миска"](#http_api_get_block_wordhttp_api_get_block_word)

## <a name="debug_app">Отладка приложения</a>

Весь выход приложения перенаправлен в выход supervisor-а
(`stdout_logfile=/dev/stdout`, см. `supervisord.conf`)
и доступен через `docker logs`.

```bash
...$ sudo docker logs ya_kafka_project3-python-app-1
2025-10-12 01:34:49,188 CRIT Supervisor is running as root.
...
...
2025-10-12 01:35:03,273 DEBG 'faust-worker' stderr output:
[2025-10-12 01:35:03,273] [7] [INFO] [^Worker]: Ready 
```

Есть `volume`, при необходимости - ищем путь к нему
через `dicker inspect` контейнера,
правим `py`-файлы приложения, рестартуем контейнер...

## <a name="happy_way_test">Быстрый тест Happy Way</a>

Сделаем сначала всё руками через web-UI.

Допустим, мы развернули всё на хосте `localhost`,
тогда web-UI нам будет доступен как `http://localhost:8070/`
(ну или какой порт мы заэкспоузили для сервиса `kafka-ui`).

1. **Напишем сообщения от Васи к Пете и к Юре**

- модель: User2UserMessage
- топик: `messages`

```json
{
    "user_id": "Вася",
    "recipient_id": "Петя",
    "timestamp": "2024-03-20T15:30:45.123456",
    "message": "Привет, муха"
}
```

```json
{
    "user_id": "Вася",
    "recipient_id": "Юра",
    "timestamp": "2024-03-20T15:30:45.123456",
    "message": "Привет, муха"
}
```

2. **Потом Юра блокирует Васю**:

- модель: BlockUserMessage
- топик: `blocked_users`

```json
{
    "recipient_id": "Вася",
    "donor_id": "Юра",
    "timestamp": "2024-03-20T15:30:45.123456",
    "block": true
}
```

3. **И админ блокирует слово "муха"**:

- модель: BlockWordMessage
- топик: `blocked_words`

```json
{
    "word": "муха",
    "timestamp": "2024-03-20T15:30:45.123456",
    "block": true
}
```

4. **Напишем те же сообщения от Васи к Пете и к Юре**:

- модель: User2UserMessage
- топик: `messages`

```json
{
    "user_id": "Вася",
    "recipient_id": "Петя",
    "timestamp": "2024-03-20T15:30:45.123456",
    "message": "Привет, муха"
}
```

```json
{
    "user_id": "Вася",
    "recipient_id": "Юра",
    "timestamp": "2024-03-20T15:30:45.123456",
    "message": "Привет, муха"
}
```

5. **И пойдём в топик `filtered_messages`**:

там должно быть только одно сообщение от Васи к Юре,
а к Пете два, и во втором слово "муха" уже закрыто астерисками:

```json
{
	"user_id": "Вася",
	"recipient_id": "Петя",
	"timestamp": "2024-03-20T15:30:45.123456",
	"message": "Привет, муха",
	"__faust": {
		"ns": "messenger.messenger_core.models.User2UserMessage"
	}
}
```

```json
{
	"user_id": "Вася",
	"recipient_id": "Юра",
	"timestamp": "2024-03-20T15:30:45.123456",
	"message": "Привет, муха",
	"__faust": {
		"ns": "messenger.messenger_core.models.User2UserMessage"
	}
}
```

```json
{
	"user_id": "Вася",
	"recipient_id": "Петя",
	"timestamp": "2024-03-20T15:30:45.123456",
	"message": "Привет, ***",
	"__faust": {
		"ns": "messenger.messenger_core.models.User2UserMessage"
	}
}
```

## <a name="test_bad_schema">Теперь передадим сообщение в неверной схеме</a>

*(тут расписано ниже, как это решал, тут наверное возможны варианты)*

, например ошибёмся в названии поля `recipient_id`:

- модель: User2UserMessage
- топик: `messages`

```json
{
	"user_id": "Вася",
	"recepient_id": "Петя",
	"timestamp": "2024-03-20T15:30:45.123456",
	"message": "Привет, шершень"
}
```

**NB: это пофиксили через supervisor_strategy**: И всё, там что-то падает,
и больше уже не работает:

```bash
...$ sudo docker logs ya_kafka_project3-python-app-1
...
2025-10-12 02:00:25,010 DEBG 'faust-worker' stderr output:
[2025-10-12 02:00:25,010] [7] [INFO] [^----OneForOneSupervisor: (1@0x7ba71c15fa70)]: Restarting dead <Agent*: messenger.mess[.]filter_messages>! Last crash reason: ValueDecodeError("__outer__.<locals>.__init__() missing 1 required positional argument: 'recipient_id'") 
NoneType: None
```

Нормальные сообщения далее не проходят тоже, и в логах никак не отражается никакая ошибка...

Попробуем поменять `supervisor_strategy` с `OneForOneSupervisor` на `CrashingSupervisor`,
чтобы рестартовало всё приложение.

Ещё у агента есть невнятный аргумент `on_error: Callable[[Agent, BaseException], None]`,
но думаю он тоже вызывается вовне циклаобработки сообщений.

Если нет... ну тогда останется только убрать модель из описания топика,
сделать `value_type=bytes`, десериализовать каждое сообщение руками...

Сделать что ли для этого промежуточный топик, на него агента с ручной десериализацией,
а текущего агента посадить читать этот топик, с гарантированно валидными сообщениями,
хотя кто мешает руками опять же в него отправить что угодно.

Вот этот вот момент непонятен: почему падает всё приложение?

Faust вообще никак не даёт перехавтить ошибку
десереализации одного сообщения в потоке внутри цикла и продолжить цикл?

Я не нашёл...

---

**supervisor_strategy**:
После указания всем агентам аргумента `supervisor_strategy=mode.CrashingSupervisor` - всё хорошо:

- отправляем сообщение в невалидной схемой
- потом отправляем нормальное
- видим работающее приложение, а в результатах обработки только второе сообщение

В логах видим, что перезапускалось приложение целиком:

```bash
...
faust.exceptions.ValueDecodeError: __outer__.<locals>.__init__() missing 1 required positional argument: 'recipient_id'

2025-10-12 03:00:42,817 DEBG 'faust-worker' stderr output:
[2025-10-12 03:00:42,816] [7] [INFO] [^Worker]: Stopping... 

2025-10-12 03:00:42,817 DEBG 'faust-worker' stderr output:
[2025-10-12 03:00:42,817] [7] [INFO] [^-App]: Stopping... 
...
```

Видимо offset движок отправляет ещё до десериализации,
и после восстановления уже читает следующее сообщение.

Ну... допустим так и задумано разрабами движка...

## <a name="cli_commands">Работа с приложением через cli-команды</a>

Команды определены в модуле `app/messenger/messenger_core/commands.py`.

### <a name="cli_commands_list">Посмотреть список команд</a>

Вызвать help приложения

```bash
...$ sudo docker exec -it ya_kafka_project3-python-app-1 bash
root@...:/app# faust -A messenger.app --help
...
Commands:
  agents          List agents.
  block-word      Send well-formed world block message to the...
...

```

Наши команды:

- block-word
- list-block-words

**Посмотреть help по конкретной команде**:

```bash
root@...:/app# faust -A messenger.app block-word --help
...
Usage: faust block-word [OPTIONS]

  Send well-formed world block message to the corresponding agent (out of
  topic?).

Options:
  --word TEXT      Word to block|unblock.
  --block BOOLEAN  Block (True) or unblock (False) word.  [default: True]
  --help           Show this message and exit.
```

### <a name="cli_commands_block_word">Давайте заблокируем слово "миска"</a>

```bash
root@...:/app# faust -A messenger.app block-word --word миска --block True
```

*тут у меня проблема с выходом из команды, есть коммент в коде,
но тем не менее "миска" блокируется*:

Добавим руками в топик `messages` сообщение:

```json
{
    "user_id": "Вася",
    "recipient_id": "Петя",
    "timestamp": "2024-03-20T15:30:45.123456",
    "message": "Привет, миска"
}
```

и увидим в топике `filtered_messages` обработанное сообщение:

```json
{
	"user_id": "Вася",
	"recipient_id": "Петя",
	"timestamp": "2024-03-20T15:30:45.123456",
	"message": "Привет, ***",
	"__faust": {
		"ns": "messenger.messenger_core.models.User2UserMessage"
	}
}
```

### <a name="cli_commands_list_block_words">Давайте посмотрим список заблокированных слов</a>

Cli-команда творит странное:

```bash
root@...:/app# faust -A messenger.app list-block-words
```

Однако http-api работает норм:

## <a name="http_api">Работа с приложением через http-api</a>

### <a name="http_api_get_block_word">Спросим, заблокирована ли "миска"</a>

`http://localhost:6077/get-block-word/%D0%BC%D0%B8%D1%81%D0%BA%D0%B0`

```json
{"word":"миска","block":true}
```

### <a name="http_api_get_block_words">Спросим весь список заблокированных слов</a>

`http://localhost:6077/get-block-words/`

И тут фиаско: почему-то оно не отдаёт ключи таблицы через метод `keys()` (:

и вообще не хочет работать с таблицей как со словарём в этом аспекте...

---

Пока что всё. Есть траблы :)