# Test Case Specification — Моноколесо «Эдем»

**Источник:** `SPEC.md`, версия 1.0.

ID `TC-001`–`TC-054` и `TC-058`–`TC-075` закреплены за модульными тестами § 4.1; `TC-055`–`TC-057` — за сценариями § 4.2. При ссылке на тест из отчёта или другого артефакта используется именно этот ID.

**Базовая конфигурация**, если в предусловии не сказано иначе: `EdenMonowheel("Эдем", 4, 300, 100)`; гондола закрыта, помощник и оборудование выключены, позиция и пробег равны нулю. Подготовка специальных состояний выполняется до шага «Вход».

## Модульные тесты

| ID | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|
| TC-001 | SPEC § 3.2; `test_init_valid` | имя «Эдем», диаметр колеса 4 м, максимальная скорость 300 км/ч, энергия 80. | создаётся объект `EdenMonowheel("Эдем", 4, 300, 80)`. | объект успешно создан; `name == "Эдем"`; `wheel_diameter_m == 4`; `max_speed_kmh == 300`; `energy == 80`. | medium |
| TC-002 | SPEC § 3.2; `test_init_empty_name_raises` | корректные числовые параметры, но `name=""`. | создаётся моноколесо. | поднимается `ValueError`. | high |
| TC-003 | SPEC § 3.2; `test_init_invalid_diameter_raises` | `wheel_diameter_m=0`, остальные параметры корректны. | создаётся моноколесо. | поднимается `ValueError`. | high |
| TC-004 | SPEC § 3.2; `test_init_invalid_max_speed_raises` | `max_speed_kmh=-20`, остальные параметры корректны. | создаётся моноколесо. | поднимается `ValueError`. | high |
| TC-005 | SPEC § 3.2; `test_init_invalid_energy_raises` | `energy=120`, остальные параметры корректны. | создаётся моноколесо. | поднимается `ValueError`. | high |
| TC-006 | SPEC § 3.2; `test_init_default_state` | корректные параметры без явного указания энергии. | создаётся моноколесо. | `energy == 100`; `position_km == 0`; `mileage_km == 0`; `on_track == False`; `gondola_open == False`; `equipment_attached == False`; `equipment_active == False`; `helper_active == False`; `trench_remaining_t == 0`; `trench_filled == False`. | medium |
| TC-007 | SPEC § 3.3; `test_public_attributes` | созданное моноколесо с корректными характеристиками. | выполняется чтение публичных атрибутов объекта. | доступны все атрибуты, перечисленные в разделе 3.3, с соответствующими типами и значениями. ### Проверка движения | medium |
| TC-008 | SPEC § 3.4.1; `test_move_main_track` | моноколесо с энергией 100. | `move(300, 0.1, "track", main_track=True)`. | возвращается `30.0`; `position_km == 30`; `mileage_km == 30`; `energy == 100`; `on_track == True`. | medium |
| TC-009 | SPEC § 3.4.1; `test_move_side_track` | моноколесо с энергией 100. | `move(100, 0.1, "track", main_track=False)`. | возвращается `10.0`; `position_km == 0`; `mileage_km == 10`; `energy == 100`; `on_track == True`. | medium |
| TC-010 | SPEC § 3.4.1; `test_move_ground_energy` | моноколесо с энергией 100, помощник выключен. | `move(20, 0.5, "ground")`. | возвращается `10.0`; `energy == 80`; `position_km == 0`; `mileage_km == 10`; `on_track == False`. | medium |
| TC-011 | SPEC § 3.4.1; `test_move_sand_energy` | моноколесо с энергией 100. | `move(20, 0.5, "sand")`. | возвращается `10.0`; `energy == 60`; `mileage_km == 10`; `position_km == 0`. | medium |
| TC-012 | SPEC § 3.4.1; `test_move_track_no_energy_cost` | моноколесо с энергией 50. | `move(100, 0.2, "track", main_track=True)`. | `position_km == 20`; `mileage_km == 20`; `energy == 50`. | medium |
| TC-013 | SPEC § 3.4.1; `test_move_backward` | моноколесо на основной борозде с `position_km=30`, `mileage_km=30`. | `move(-100, 0.1, "track", main_track=True)`. | `position_km == 20`; `mileage_km == 40`; энергия не изменяется. | medium |
| TC-014 | SPEC § 3.4.1; `test_move_zero_speed` | моноколесо с `position_km=10`, `mileage_km=10`, `energy=80`, `on_track=True` и открытой гондолой. | `move(0, 0.5, "ground")`. | возвращается `0.0`; состояние, включая открытую гондолу, не изменяется. | medium |
| TC-015 | SPEC § 3.4.1; `test_move_invalid_time_raises` | моноколесо с энергией 100. | `move(20, 0, "ground")`. | поднимается `ValueError`; состояние не изменяется. | high |
| TC-016 | SPEC § 3.4.1; `test_move_invalid_terrain_raises` | моноколесо с энергией 100. | `move(20, 1, "water")`. | поднимается `ValueError`; состояние не изменяется. | high |
| TC-017 | SPEC § 3.4.1; `test_move_speed_limit_raises` | моноколесо с энергией 100 и выключенным помощником. | `move(50, 0.1, "ground")`. | поднимается `ValueError`; позиция, пробег и энергия не изменяются. | high |
| TC-018 | SPEC § 3.4.1; `test_helper_ground_speed_bonus` | моноколесо с энергией 100 и включённым помощником. | `move(50, 0.1, "ground")`. | возвращается `5.0`; `mileage_km == 5`; `energy == 90`; `position_km == 0`. | medium |
| TC-019 | SPEC § 3.4.1; `test_helper_sand_limit_unchanged` | моноколесо с включённым помощником. | `move(30, 0.1, "sand")`. | поднимается `ValueError`; состояние не изменяется. | medium |
| TC-020 | SPEC § 3.4.1; `test_move_no_energy_raises` | моноколесо с энергией 10. | `move(20, 0.5, "ground")`. | поднимается `MonowheelNoEnergy`; `energy == 10`; `position_km == 0`; `mileage_km == 0`. | high |
| TC-021 | SPEC § 3.4.1, §6.3; `test_move_open_gondola_raises` | моноколесо с открытой гондолой и энергией 0. | `move(20, 0.1, "ground")`. | поднимается `MonowheelGondolaOpen`, имеющее приоритет над `MonowheelNoEnergy`; состояние не изменяется. | high |
| TC-022 | SPEC § 3.4.1; `test_move_arrive_on_track` | моноколесо вне борозды с энергией 100. | `move(20, 0.25, "ground", arrive_on_track=True)`. | `mileage_km == 5`; `position_km == 0`; `energy == 90`; `on_track == True`. | medium |
| TC-023 | SPEC § 3.4.1; `test_move_ground_main_track_raises` | моноколесо с энергией 100. | `move(20, 0.5, "ground", main_track=True)`. | поднимается `ValueError`; состояние не изменяется. | high |
| TC-024 | SPEC § 3.4.1; `test_move_track_arrival_flag_raises` | моноколесо с энергией 100. | `move(100, 0.1, "track", arrive_on_track=True)`. | поднимается `ValueError`; состояние не изменяется. ### Проверка расчёта энергии и препятствий | high |
| TC-025 | SPEC § 3.4.2; `test_calculate_energy_no_state_change` | моноколесо с энергией 100, нулевыми позицией и пробегом. | `calculate_energy(20, 0.5, "ground")`. | возвращается `20.0`; `energy == 100`; `position_km == 0`; `mileage_km == 0`. | medium |
| TC-026 | SPEC § 3.4.3; `test_can_overcome_width_limit` | моноколесо с диаметром колеса 4 м. | `can_overcome(2.0)`. | возвращается `True`; энергия, позиция и пробег не изменяются. | medium |
| TC-027 | SPEC § 3.4.3; `test_can_overcome_too_wide` | моноколесо с диаметром колеса 4 м. | `can_overcome(2.5)`. | возвращается `False`; состояние не изменяется. | medium |
| TC-028 | SPEC § 3.4.3; `test_can_overcome_negative_width_raises` | моноколесо с диаметром колеса 4 м. | `can_overcome(-1)`. | поднимается `ValueError`. ### Проверка зарядки | high |
| TC-029 | SPEC § 3.4.4; `test_recharge_on_track` | моноколесо на направляющей борозде с энергией 50. | `recharge(100)`. | `energy == 100`; позиция и пробег не изменяются. | medium |
| TC-030 | SPEC § 3.4.4; `test_recharge_off_track_raises` | моноколесо вне борозды с энергией 20. | `recharge(70)`. | поднимается `MonowheelNotOnTrack`; `energy == 20`. | high |
| TC-031 | SPEC § 3.4.4; `test_recharge_over_100_raises` | моноколесо на борозде с энергией 20. | `recharge(101)`. | поднимается `ValueError`; `energy == 20`. | high |
| TC-032 | SPEC § 3.4.4; `test_recharge_below_current_raises` | моноколесо на борозде с энергией 70. | `recharge(20)`. | поднимается `ValueError`; `energy == 70`. ### Проверка гондолы | high |
| TC-033 | SPEC § 3.4.5; `test_open_gondola` | моноколесо с закрытой гондолой. | `open_gondola()`. | `gondola_open == True`. | medium |
| TC-034 | SPEC § 3.4.6; `test_close_gondola` | моноколесо с открытой гондолой. | `close_gondola()`. | `gondola_open == False`. ### Проверка уборочной машины | medium |
| TC-035 | SPEC § 3.4.7; `test_attach_equipment` | моноколесо без подключённого оборудования. | `attach_equipment()`. | `equipment_attached == True`; `equipment_active == False`. | medium |
| TC-036 | SPEC § 3.4.7; `test_attach_equipment_twice_raises` | моноколесо с подключённой уборочной машиной. | `attach_equipment()`. | поднимается `MonowheelEquipmentError`; оборудование остаётся подключённым. | high |
| TC-037 | SPEC § 3.4.8; `test_detach_equipment` | моноколесо с подключённой включённой уборочной машиной. | `detach_equipment()`. | `equipment_attached == False`; `equipment_active == False`. | medium |
| TC-038 | SPEC § 3.4.8; `test_detach_missing_equipment_raises` | моноколесо без подключённого оборудования. | `detach_equipment()`. | поднимается `MonowheelEquipmentError`. | high |
| TC-039 | SPEC § 3.4.9; `test_set_equipment_active` | моноколесо с подключённой выключенной уборочной машиной. | `set_equipment_active(True)`. | `equipment_active == True`; `equipment_attached == True`. | medium |
| TC-040 | SPEC § 3.4.9; `test_activate_missing_equipment_raises` | моноколесо без подключённой уборочной машины. | `set_equipment_active(True)`. | поднимается `MonowheelEquipmentError`; `equipment_active == False`. | high |
| TC-041 | SPEC § 3.4.10; `test_assess_trench` | ранее оценён ров объёмом 3 т. | `assess_trench(2)`. | новая оценка заменяет старую: `trench_volume_t == 2`; `trench_remaining_t == 2`; `trench_filled == False`; энергия не изменяется. | medium |
| TC-042 | SPEC § 3.4.10; `test_assess_trench_invalid_volume_raises` | моноколесо без зарегистрированного рва. | `assess_trench(-3)`. | поднимается `ValueError`; состояние не изменяется. | high |
| TC-043 | SPEC § 3.4.1, 3.4.10; `test_equipment_one_pass` | моноколесо вне борозды с энергией 100, включённой уборочной машиной и рвом, требующим 3 тонны грунта. | `move(20, 0.05, "ground")`. | `trench_remaining_t == 2`; `trench_filled == False`; `mileage_km == 1`; `energy == 83`. | medium |
| TC-044 | SPEC § 3.4.1, 3.4.10; `test_equipment_energy_cost` | моноколесо вне борозды с энергией 100, включённой уборочной машиной и рвом, требующим 3 тонны грунта. | `move(20, 0.05, "ground")`. | на движение израсходовано 2 единицы энергии; на перемещение 1 тонны грунта израсходовано 15 единиц; общий расход составляет 17 единиц; `energy == 83`. | medium |
| TC-045 | SPEC § 3.4.1, 3.4.10; `test_trench_filled` | моноколесо вне борозды с энергией 50, включённой уборочной машиной и рвом, в котором осталось засыпать 1 тонну грунта (предыдущие проходы выполнены при подготовке теста). | `move(20, 0.05, "ground")`. | `trench_remaining_t == 0`; `trench_filled == True`; `energy == 33`. ### Проверка помощника и состояния | medium |
| TC-046 | SPEC § 3.4.11; `test_set_helper_active` | моноколесо с выключенным помощником. | `set_helper_active(True)`. | `helper_active == True`; энергия не изменяется. | medium |
| TC-047 | SPEC § 3.4.12; `test_status_keys` | созданное моноколесо с начальными характеристиками. | `get_status()`. | возвращается словарь `dict`; словарь содержит все 14 ключей, перечисленных в разделе 3.4.12; значения соответствуют текущему состоянию моноколеса; состояние объекта не изменяется. | medium |
| TC-048 | SPEC § 6; `test_invalid_parameters_raise` | моноколесо с энергией 100. | `move("fast", 1, "ground")`. | поднимается `ValueError`; состояние не изменяется. | high |
| TC-049 | SPEC § 6; `test_domain_exception_hierarchy` | четыре класса `MonowheelNoEnergy`, `MonowheelGondolaOpen`, `MonowheelNotOnTrack`, `MonowheelEquipmentError`. | проверяется их наследование от `MonowheelError`. | каждый из четырёх классов является подклассом `MonowheelError`. | high |
| TC-050 | SPEC § 3.4.1; `test_move_exact_energy` | моноколесо с энергией 20. | `move(20, 0.5, "ground")`. | `energy == 0`, `mileage_km == 10`, `position_km == 0`. | high |
| TC-051 | SPEC § 3.4.1; `test_move_one_energy_short` | моноколесо с энергией 19. | `move(20, 0.5, "ground")`. | поднимается `MonowheelNoEnergy`; энергия, позиция и пробег не изменяются. | high |
| TC-052 | SPEC § 3.4.11; `test_set_helper_inactive` | моноколесо с включённым помощником. | `set_helper_active(False)`. | `helper_active == False`; энергия не изменяется. | medium |
| TC-053 | SPEC § 3.4.9; `test_set_equipment_inactive` | моноколесо с подключённой включённой уборочной машиной. | `set_equipment_active(False)`. | `equipment_active == False`, `equipment_attached == True`. | medium |
| TC-054 | SPEC § 3.4.1, 3.4.10; `test_equipment_partial_ton` | моноколесо с энергией 50, включённой уборочной машиной и рвом с остатком 0.5 тонны. | `move(20, 0.05, "ground")`. | `trench_remaining_t == 0`, `trench_filled == True`, `energy == 40.5` (2 единицы за 1 км и 7.5 за 0.5 тонны). | medium |
| TC-058 | SPEC § 6.3; `test_invalid_speed_has_priority_over_no_energy` | энергия 10, помощник выключен, гондола открыта. | `move(60, 0.5, "ground")`. | `ValueError` имеет приоритет над `MonowheelGondolaOpen` и `MonowheelNoEnergy`; состояние не изменяется. | high |
| TC-059 | SPEC § 3.4.1, §6.2; `test_equipment_no_energy_raises` | энергия 16, подключённая и включённая уборочная машина, ров 1 т. | `move(20, 0.05, "ground")`. | `MonowheelNoEnergy`; энергия, пробег и состояние рва не изменяются. | high |
| TC-060 | SPEC § 3.4.2; `test_calculate_energy_invalid_parameters_raise` | созданное моноколесо, помощник выключен. | `calculate_energy(50, 0.1, "ground")` и `calculate_energy(20, 0.1, "water")`. | Для каждого входа поднимается `ValueError`; состояние не изменяется. | high |
| TC-061 | SPEC § 3.2, §3.4.1, §3.4.3; `test_non_finite_numbers_raise` | созданное моноколесо. | `move(float("nan"), 0.1, "ground")`, `move(20, float("inf"), "ground")`, `can_overcome(float("inf"))`. | Для каждого входа поднимается `ValueError`; состояние не изменяется. | high |
| TC-062 | SPEC § 3.4.1; `test_equipment_works_on_sand` | энергия 100, подключённая и включённая уборочная машина, ров 1 т. | `move(20, 0.05, "sand")`. | Ров засыпан; `mileage_km == 1`; `energy == 81`. | medium |
| TC-063 | SPEC § 3.4.11, §6.2; `test_helper_ground_speed_limit_raises` | помощник включён. | `move(60, 0.1, "ground")`. | Поднимается `ValueError`; состояние не изменяется. | high |
| TC-064 | SPEC § 3.4.1; `test_equipment_works_after_starting_on_track` | энергия 100, включённое оборудование, ров 1 т, `on_track=True`. | `move(20, 0.05, "ground")`. | Ров засыпан; `energy == 83`. Предыдущее `on_track` не отключает оборудование. | medium |
| TC-065 | SPEC § 3.4.1; `test_equipment_works_when_arriving_on_track` | энергия 100, включённое оборудование, ров 1 т. | `move(20, 0.05, "ground", arrive_on_track=True)`. | Ров засыпан; `energy == 83`; итоговое `on_track == True` не отключает оборудование. | medium |
| TC-066 | SPEC § 3.4.4, §6.3; `test_recharge_validates_target_before_track` | моноколесо вне борозды с энергией 20. | `recharge(110)`. | Поднимается `ValueError`, а не `MonowheelNotOnTrack`; энергия не изменяется. | high |
| TC-067 | SPEC § 3.4.1; `test_track_speed_limit_uses_absolute_value` | `max_speed_kmh=300`. | `move(-301, 0.1, "track", main_track=True)`. | Поднимается `ValueError`; состояние не изменяется. | high |
| TC-068 | SPEC § 3.4.1, §3.4.11; `test_constructive_speed_caps_helper_limit` | `max_speed_kmh=45`, помощник включён. | `move(46, 0.1, "ground")`. | Поднимается `ValueError`: конструктивный предел 45 км/ч имеет приоритет над лимитом помощника 50 км/ч. | high |
| TC-069 | SPEC § 3.4.1; `test_invalid_route_flag_raises` | созданное моноколесо. | `move(20, 0.1, "ground", main_track="yes")`. | Поднимается `ValueError`; состояние не изменяется. | high |
| TC-070 | SPEC § 3.4.11; `test_invalid_helper_flag_raises` | помощник выключен. | `set_helper_active("yes")`. | Поднимается `ValueError`; помощник остаётся выключенным. | high |
| TC-071 | SPEC § 3.2, §6; `test_bool_is_not_numeric_speed` | созданное моноколесо. | `move(True, 0.1, "ground")`. | Поднимается `ValueError`; состояние не изменяется. | high |
| TC-072 | SPEC § 3.3; `test_read_only_energy_cannot_be_assigned` | созданное моноколесо. | присваивается `energy = 50`. | Поднимается `AttributeError`. | high |
| TC-073 | SPEC § 3.3; `test_on_track_requires_bool` | `on_track == False`. | присваивается `on_track = "yes"`. | Поднимается `ValueError`; `on_track` остаётся `False`. | high |
| TC-074 | SPEC § 3.4.1; `test_equipment_does_not_work_on_track` | энергия 100, включённое оборудование, ров 1 т. | `move(20, 0.05, "track")`. | Ров не изменяется; энергия не расходуется. | medium |
| TC-075 | SPEC § 3.4.1; `test_equipment_does_not_work_without_movement` | энергия 100, включённое оборудование, ров 1 т. | `move(0, 0.05, "ground")`. | Ров и энергия не изменяются. | medium |

## Сценарные тесты

| ID | Источник | Вход | Ожидание | Приоритет |
|---|---|---|---|---|
| TC-055 | SPEC § 4.2, сценарий 5; `test_escape_from_broken_track` | Выполнить все шаги «Побег с повреждённой борозды» по порядку: основная борозда → грунт → проверка расщелины → неудачная попытка движения → боковая борозда → зарядка → объезд → основная борозда | `position_km == 120`; `mileage_km == 165`; `energy == 50`; `on_track == True`; предусмотренные ошибки и промежуточные состояния совпадают с § 4.2 | high |
| TC-056 | SPEC § 4.2, сценарий 6; `test_trench_filling_adventure` | Выполнить все шаги «Машина, засыпающая ров»: `assess_trench(3)` → включить оборудование → три прохода по грунту → выключить оборудование → проехать 5 км | `trench_remaining_t == 0`; `trench_filled == True`; `position_km == 0`; `mileage_km == 8`; `energy == 19`; `equipment_active == False` | high |
| TC-057 | SPEC § 4.2, сценарий 7; `test_novice_pilot_adventure` | Выполнить все шаги «Первый рейс неопытного пилота»: открытая гондола → ошибка движения → закрытие → основная борозда → проверка ограничений скорости → помощник → грунт → прибытие на боковую борозду → зарядка | `position_km == 10`; `mileage_km == 40`; `energy == 70`; `on_track == True`; `helper_active == False`; `gondola_open == False`; предусмотренные исключения возникли | high |

