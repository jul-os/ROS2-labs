# Граф ROS 2: turtlesim + teleop

## Дата и время выполнения
2026-09-27, ~21:30

## Среда
- ROS 2 Jazzy
- Docker-контейнер на Fedora (Wayland)
- ROS_DOMAIN_ID=16

## Запущенные ноды

### /turtlesim
- **Роль:** Симулятор черепахи, публикует состояние и принимает команды движения
- **Подписчики:**
  - `/turtle1/cmd_vel` (geometry_msgs/msg/Twist) — команды линейной и угловой скорости
- **Публикации:**
  - `/turtle1/pose` (turtlesim/msg/Pose) — текущее положение и скорость
  - `/turtle1/color_sensor` (turtlesim/msg/Color) — цвет под черепахой
- **Сервисы:**
  - `/clear` — очистить экран
  - `/spawn` — создать новую черепаху
  - `/turtle1/set_pen` — настроить перо
  - `/turtle1/teleport_absolute` — телепорт в абсолютные координаты
  - `/turtle1/teleport_relative` — телепорт относительно текущего положения

### /teleop_turtle
- **Роль:** Управление черепахой с клавиатуры
- **Публикации:**
  - `/turtle1/cmd_vel` (geometry_msgs/msg/Twist) — команды движения

## Топики графа

| Топик | Тип | Описание |
|-------|-----|----------|
| `/turtle1/cmd_vel` | geometry_msgs/msg/Twist | Команды скорости от teleop к turtlesim |
| `/turtle1/pose` | turtlesim/msg/Pose | Текущее положение черепахи |
| `/turtle1/color_sensor` | turtlesim/msg/Color | Цвет под черепахой |

## Пример сообщения /turtle1/pose
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0


## Замер частоты публикации /turtle1/pose

Команда: `ros2 topic hz /turtle1/pose`
Длительность замера: ~15 секунд

Результаты:
average rate: 62.516
        min: 0.015s max: 0.017s std dev: 0.00045s window: 64
average rate: 62.500
        min: 0.015s max: 0.017s std dev: 0.00044s window: 127
average rate: 62.503
        min: 0.015s max: 0.017s std dev: 0.00042s window: 190
average rate: 62.505
        min: 0.015s max: 0.017s std dev: 0.00043s window: 253
average rate: 62.503
        min: 0.015s max: 0.017s std dev: 0.00044s window: 316
average rate: 62.498
        min: 0.015s max: 0.017s std dev: 0.00044s window: 379
average rate: 62.503
        min: 0.015s max: 0.017s std dev: 0.00043s window: 442
average rate: 62.501
        min: 0.015s max: 0.017s std dev: 0.00044s window: 505
average rate: 62.503
        min: 0.015s max: 0.017s std dev: 0.00044s window: 568


**Средняя частота:** ~62.5 Гц  
**Ожидаемая частота:** 60-62.5 Гц (таймер turtlesim 16 мс)  
**Вывод:** Частота соответствует ожидаемой, turtlesim публикует позу с стабильной частотой.

## Предупреждения FastDDS

В выводе команд присутствуют предупреждения:
[RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7004: open_and_lock_file failed -> Function open_port_internal

Это предупреждения от FastDDS при попытке использовать shared memory transport в Docker. Они не влияют на работу графа, так как FastDDS автоматически переключается на UDP transport. Все сообщения доставляются корректно.

## Вывод

Граф работает корректно:
- Ноды `/turtlesim` и `/teleop_turtle` видят друг друга
- Топик `/turtle1/cmd_vel` связывает teleop с turtlesim
- Топик `/turtle1/pose` публикуется с частотой ~62.5 Гц
- Discovery работает в домене 16


## Разрыв связи: ROS_DOMAIN_ID=17

### Изменения конфигурации
- Терминал B (teleop): `export ROS_DOMAIN_ID=17`
- Терминал C (наблюдение): `export ROS_DOMAIN_ID=17`
- Терминал A (turtlesim): остался в домене 16

### Проверка списка нод (домен 17)
ros2 node list --no-daemon --spin-time 2
Вывод:
/teleop_turtle
Наблюдение: Нода /turtlesim отсутствует, так как она в домене 16.

### Попытка получить позу (домен 17)
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
Результат:
exit=124
Содержимое файла:
2026-09-27 21:46:02.615 [RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7004: open_and_lock_file failed -> Function open_port_internal

Анализ

    exit=124 означает, что команда timeout убила процесс по истечении 5 секунд
    Файл pose-broken.txt не содержит данных позы — только предупреждение FastDDS
    Это доказывает, что ноды в разных доменах не обмениваются сообщениями
    Discovery-протокол ROS 2 ищет издателей только внутри своего домена

Вывод
Связь разорвана: /teleop_turtle в домене 17 не видит /turtlesim в домене 16. Сообщения не доставляются.

## Восстановление связи: возврат в ROS_DOMAIN_ID=16

### Изменения конфигурации
- Терминал B (teleop): `export ROS_DOMAIN_ID=16` (перезапуск ноды)
- Терминал C (наблюдение): `export ROS_DOMAIN_ID=16`
- Терминал A (turtlesim): продолжал работать в домене 16

### Проверка списка нод (домен 16)
ros2 node list --no-daemon --spin-time 2
Вывод:
/teleop_turtle
/turtlesim
Наблюдение: Обе ноды снова видны друг другу. Discovery сработал.

### Получение позы (домен 16)
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
Результат:
exit=0
Содержимое evidence/pr01/pose-fixed.txt:
2026-09-27 21:51:28.618 [RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7004: open_and_lock_file failed -> Function open_port_internal
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---

Анализ

    exit=0 означает успешное выполнение команды (сообщение получено до истечения таймаута).
    Файл содержит актуальные данные позы, в отличие от pose-broken.txt.
    Это доказывает, что возврат в исходный домен мгновенно восстанавливает связь, так как настройки самой ноды /turtlesim не менялись, изменился только параметр окружения (ROS_DOMAIN_ID) у клиента.

### Итоговый вывод по лабораторной работе
Цель достигнута. Экспериментально подтверждено, что:

    В исправном состоянии (один домен) ноды обнаруживают друг друга и обмениваются сообщениями.
    Изменение ROS_DOMAIN_ID изолирует ноды: discovery не находит издателя, сообщения не доставляются (подтверждено таймаутом и отсутствием данных).
    Возврат к исходному ROS_DOMAIN_ID восстанавливает связь без необходимости перезапуска издателя (/turtlesim), так как он продолжает публиковать данные в своем домене.


