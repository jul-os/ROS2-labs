# PR04 — Параметры ноды patrol

## Объявленные параметры

| Параметр | По умолчанию | Допустимый диапазон | Описание |
|----------|-------------|---------------------|----------|
| `linear_speed` | 0.5 | 0.0–1.0 | Линейная скорость (м/с) |
| `turn_rate` | 0.3 | -1.0–1.0 | Угловая скорость (рад/с) |
| `publish_hz` | 10.0 | 1.0–30.0 | Частота публикации (Гц) |

## Команды

```bash
# Просмотр текущих параметров
ros2 param list /patrol

# Изменение частоты (допустимое значение)
ros2 param set /patrol publish_hz 5.0

# Изменение скорости
ros2 param set /patrol linear_speed 0.8

# Изменение поворота
ros2 param set /patrol turn_rate -0.5

# Попытка установить ноль (недопустимо)
ros2 param set /patrol publish_hz 0.0
```

## Проверка частоты

```bash
# Запуск ноды
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel

# В отдельном терминале — измерение частоты
ros2 topic hz /turtle1/cmd_vel
```

## Проверка типа позы

```bash
ros2 topic type /turtle1/pose
# В Jazzy: turtlesim/msg/Pose (в некоторых версиях turtlesim — turtlesim_msgs/msg/Pose)
```

## Действие /clear (сервис turtlesim)

```bash
# Очистка холста turtlesim (/clear — это сервис, не action)
ros2 service call /clear std_srvs/srv/Empty
```

## Действие /turtle1/rotate_absolute

```bash
# Список действий
ros2 action list -t

# Поворот черепахи на заданный угол
ros2 action send_goal /turtle1/rotate_absolute turtlesim/action/RotateAbsolute "{theta: 1.57}"
```

## Запрос vs Цель

1. **Запрос (request)** — часть сообщения клиента → сервера внутри одного вызова: для сервиса на каждый вызов приходится единственный запрос и мгновенный ответ.
2. **Цель (goal)** — долгоживущая задача action-сервера: `/turtle1/rotate_absolute` принимает цель, шлёт feedback во время поворота, возвращает в конце result и цель можно отменить.

## Различия

1. **Запрос (srv)**: клиент → сервер, сервер отвечает. Мгновенно.
2. **Цель (action)**: клиент отправляет цель, сервер выполняет, отправляет feedback, затем result. Можно отменить.
