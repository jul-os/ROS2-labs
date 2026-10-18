# PR06 — дерево систем координат

REP-103: метры, радианы; `x` вперёд, `y` влево, `z` вверх. В `robot_state_publisher` запускается один владелец публикации преобразований. Таблица описывает ожидаемое исправленное дерево.

| Родитель | Ребёнок | Ожидаемое преобразование | Тип и владелец |
|---|---|---|---|
| `base_link` | `camera_link` | `(0.28, 0, 0.38) m`, `(0, 0, 0) rad` | fixed; `robot_state_publisher` → `/tf_static` |
| `base_link` | `lidar_link` | `(0.28, 0, 0.38) m`, `(0, 0, 0) rad` | fixed; `robot_state_publisher` → `/tf_static` |
| `base_link` | `imu_link` | `(0.28, 0, 0.38) m`, `(0, 0, 0) rad` | fixed; `robot_state_publisher` → `/tf_static` |
| `base_link` | `front_left_wheel` | `(+wheelbase/2, +track/2, 0)`, ось вращения `+y` | continuous; `robot_state_publisher` публикует `/tf` при наличии `joint_states` |
| `base_link` | `front_right_wheel` | `(+wheelbase/2, -track/2, 0)`, ось вращения `+y` | continuous; `robot_state_publisher` публикует `/tf` при наличии `joint_states` |
| `base_link` | `rear_left_wheel` | `(-wheelbase/2, +track/2, 0)`, ось вращения `+y` | continuous; `robot_state_publisher` публикует `/tf` при наличии `joint_states` |
| `base_link` | `rear_right_wheel` | `(-wheelbase/2, -track/2, 0)`, ось вращения `+y` | continuous; `robot_state_publisher` публикует `/tf` при наличии `joint_states` |

Размеры базы, колея, база колёс и радиус колеса параметризованы Xacro-аргументами. Каждый сенсор имеет собственные `visual`, `collision` и допустимый `inertial`. Для визуализации в RViz задан `Fixed Frame: base_link`; `map`/`odom` не публикуются.

## Проверка в ROS 2 Jazzy

Команда `ros2 run tf2_ros tf2_echo base_link lidar_link` показала при времени `0.0`:

```text
Translation: [0.280, 0.000, 0.380]
Rotation (xyzw): [0.000, 0.000, 0.000, 1.000]
```

`ros2 run tf2_tools view_frames` подтвердил три фиксированные связи: `base_link → camera_link`, `base_link → imu_link` и `base_link → lidar_link`. Сгенерированные схема Graphviz и PDF сохранены рядом: `frames_2026-10-18_17.41.25.gv` и `frames_2026-10-18_17.41.25.pdf`.
