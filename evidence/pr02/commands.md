# PR02 — Команды Linux и ROS

## Подготовка окружения

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtlesim
```

**Назначение:** Подключить среду ROS 2 Jazzy, задать домен DDS и проверить установленный пакет turtlesim.

**Результат:** `ros2 pkg prefix turtlesim` выводит `/opt/ros/jazzy` — путь к установленному пакету.

---

## Создание пакета

```bash
cd src
ros2 pkg create --build-type ament_python --license Apache-2.0 \
  turtle_bringup --dependencies launch launch_ros turtlesim
```

**Назначение:** Создать каркас Python-пакета с зависимостями для launch и turtlesim.

**Результат:** Созданы `package.xml`, `setup.py`, `setup.cfg`, `resource/turtle_bringup`, `turtle_bringup/__init__.py`.

---

## Сборка пакета

```bash
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build.txt
```

**Назначение:** Собрать пакет и записать лог в файл.

**Результат:** Сборка успешна, пакет установлен в `install/`.

---

## Проверка установки

```bash
source install/setup.bash
ros2 pkg prefix turtle_bringup
```

**Назначение:** Подключить собранный пакет и проверить его префикс.

**Результат:** Путь указывает на `install/turtle_bringup` в workspace.

---

## Запуск turtlesim

```bash
ros2 launch turtle_bringup sim.launch.py
```

**Назначение:** Запустить ноду turtlesim через launch-файл.

**Результат:** Открывается окно симуляции с черепахой. Лог:
```
[INFO] [launch]: All log files can be found below /home/ubuntu/.ros/log/...
[INFO] [turtlesim_node-1]: process started with pid [191]
[turtlesim_node-1] [INFO] [...]: Starting turtlesim with node name /turtlesim
[turtlesim_node-1] [INFO] [...]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
```

---

## Проверка графа

```bash
ros2 node list --no-daemon --spin-time 2
```

**Назначение:** Просмотреть активные ноды.

**Результат:**
```
/turtlesim
```

---

## Публикация команда движения (правильный топик)

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**Назначение:** Отправить команду движения черепахе.

**Результат:** Черепаха движется по кругу.

### Позиция ДО движения:
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

### Позиция ПОСЛЕ движения:
```
x: 6.720535755157471
y: 9.15625
theta: 2.503999948501587
linear_velocity: 0.0
angular_velocity: 0.0
```

---

## Ошибка: неправильное имя топика

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

**Назначение:** Публиковать в топик `/cmd_vel` вместо `/turtle1/cmd_vel`.

**Результат:** Черепаха **не двигается**, хотя издатель работает и публикует сообщения.

---

## Сравнение топиков

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

### /cmd_vel (неправильный):
```
Unknown topic '/cmd_vel'
```

### /turtle1/cmd_vel (правильный):
```
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1
Node name: turtlesim
Node namespace: /
Endpoint type: SUBSCRIPTION
```

**Вывод:** У `/cmd_vel` нет подписчика, поэтому сообщения не доставляются. У `/turtle1/cmd_vel` есть подписчик (нода turtlesim).

---

## Операторы `>` и `|`

- `>` — перенаправляет stdout в файл, заменяя содержимое. Пример: `command > log.txt`
- `|` — передаёт stdout одной команды на вход другой. Пример: `command | grep error`
- `2>&1` — перенаправляет stderr туда же, куда и stdout
- `tee` — одновременно показывает вывод и записывает в файл: `command | tee log.txt`

---

## `source` и запуск программы

- `source` (или `.`) — выполняет скрипт в текущем процессе shell, позволяя изменять переменные окружения. Пример: `source install/setup.bash`
- Запуск программы (например, `./script.sh`) — создаёт новый процесс, изменения окружения не сохраняются в родителе
