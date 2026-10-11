# PR03 — Демонстрация работы ноды patrol

## Роли компонентов

### init
`rclpy.init(args=args)` инициализирует ROS 2 клиентскую библиотеку. Должен быть вызван перед созданием любых нод.

### spin
`rclpy.spin(node)` запускает основной цикл обработки событий. Блокирует выполнение до получения сигнала завершения (Ctrl+C). Обрабатывает входящие сообщения и таймеры.

### callback
Функции, вызываемые при получении сообщения (pose_callback) или срабатывании таймера (timer_callback). Не должны блокировать выполнение долго.

### Ctrl+C
Сигнал SIGINT прерывает spin, вызывает KeyboardInterrupt. В блоке finally корректно уничтожаем ноду и завершаем rclpy.

## Запуск

```bash
# Сборка
colcon build --symlink-install --packages-select patrol
source install/setup.bash

# Запуск turtlesim (в отдельном терминале)
ros2 launch turtle_bringup sim.launch.py

# Запуск patrol с remap
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

## Проверка

```bash
# Частота публикации
ros2 topic hz /turtle1/cmd_vel

# Топики
ros2 topic list

# Ноды
ros2 node list
```
