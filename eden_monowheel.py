"""Программная модель моноколеса «Эдем» по SPEC.md версии 1.0."""

import math


class MonowheelError(Exception):
    """Базовая ошибка эксплуатации моноколеса."""


class MonowheelNoEnergy(MonowheelError):
    """Недостаточно энергии для всего прохода."""


class MonowheelGondolaOpen(MonowheelError):
    """Движение запрещено при открытой гондоле."""


class MonowheelNotOnTrack(MonowheelError):
    """Для зарядки требуется направляющая борозда."""


class MonowheelEquipmentError(MonowheelError):
    """Нарушены правила подключения оборудования."""


def _number(value: float, name: str) -> float:
    """Проверить число и привести к float, исключая bool, NaN и inf."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _boolean(value: bool, name: str) -> bool:
    """Проверить логический параметр без неявного преобразования."""
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")
    return value


class EdenMonowheel:
    """Моноколесо с гондолой, помощником и уборочной машиной."""

    def __init__(
        self,
        name: str,
        wheel_diameter_m: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        diameter = _number(wheel_diameter_m, "wheel_diameter_m")
        speed = _number(max_speed_kmh, "max_speed_kmh")
        charge = _number(energy, "energy")
        if diameter <= 0 or speed <= 0:
            raise ValueError("diameter and maximum speed must be positive")
        if not 0 <= charge <= 100:
            raise ValueError("energy must be between 0 and 100")
        self._name = name
        self._wheel_diameter_m = diameter
        self._max_speed_kmh = speed
        self._energy = charge
        self._position_km = 0.0
        self._mileage_km = 0.0
        self._on_track = False
        self._gondola_open = False
        self._equipment_attached = False
        self._equipment_active = False
        self._helper_active = False
        self._trench_volume_t = 0.0
        self._trench_remaining_t = 0.0
        self._trench_filled = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def wheel_diameter_m(self) -> float:
        return self._wheel_diameter_m

    @property
    def max_speed_kmh(self) -> float:
        return self._max_speed_kmh

    @property
    def energy(self) -> float:
        return self._energy

    @property
    def position_km(self) -> float:
        return self._position_km

    @property
    def mileage_km(self) -> float:
        return self._mileage_km

    @property
    def on_track(self) -> bool:
        return self._on_track

    @on_track.setter
    def on_track(self, value: bool) -> None:
        self._on_track = _boolean(value, "on_track")

    @property
    def gondola_open(self) -> bool:
        return self._gondola_open

    @property
    def equipment_attached(self) -> bool:
        return self._equipment_attached

    @property
    def equipment_active(self) -> bool:
        return self._equipment_active

    @property
    def helper_active(self) -> bool:
        return self._helper_active

    @property
    def trench_volume_t(self) -> float:
        return self._trench_volume_t

    @property
    def trench_remaining_t(self) -> float:
        return self._trench_remaining_t

    @property
    def trench_filled(self) -> bool:
        return self._trench_filled

    def _movement(
        self, speed_kmh: float, time_h: float, terrain: str
    ) -> tuple[float, float]:
        """Проверить параметры и получить скорость и расстояние."""
        speed = _number(speed_kmh, "speed_kmh")
        duration = _number(time_h, "time_h")
        if duration <= 0:
            raise ValueError("time_h must be positive")
        if not isinstance(terrain, str) or terrain not in (
            "track", "ground", "sand"
        ):
            raise ValueError("unknown terrain")
        limit = self._max_speed_kmh
        if terrain == "ground":
            limit = min(limit, 50 if self._helper_active else 40)
        elif terrain == "sand":
            limit = min(limit, 20)
        if abs(speed) > limit:
            raise ValueError("speed exceeds the limit for this terrain")
        distance = abs(speed) * duration
        if not math.isfinite(distance):
            raise ValueError("distance must be finite")
        return speed, distance

    def move(
        self,
        speed_kmh: float,
        time_h: float,
        terrain: str,
        main_track: bool = False,
        arrive_on_track: bool = False,
    ) -> float:
        """Выполнить один проход; при ошибке сохранить всё состояние."""
        speed, distance = self._movement(speed_kmh, time_h, terrain)
        _boolean(main_track, "main_track")
        _boolean(arrive_on_track, "arrive_on_track")
        if main_track and terrain != "track":
            raise ValueError("main_track requires track terrain")
        if arrive_on_track and terrain == "track":
            raise ValueError("arrive_on_track requires ground or sand")

        position = self._position_km
        if main_track:
            position += distance if speed >= 0 else -distance
        mileage = self._mileage_km + distance
        if not math.isfinite(position) or not math.isfinite(mileage):
            raise ValueError("position and mileage must be finite")
        if speed == 0:
            return 0.0
        if self._gondola_open:
            raise MonowheelGondolaOpen("close the gondola before moving")

        soil = 0.0
        if (
            distance > 0
            and self._equipment_active
            and terrain != "track"
            and self._trench_remaining_t > 0
        ):
            soil = min(1.0, self._trench_remaining_t)
        rate = {"track": 0, "ground": 2, "sand": 4}[terrain]
        cost = distance * rate + soil * 15
        if cost > self._energy:
            raise MonowheelNoEnergy(
                f"not enough energy: required {cost}, have {self._energy}"
            )

        # Все проверки завершены: применяем результат прохода целиком.
        self._position_km = position
        self._mileage_km = mileage
        self._energy -= cost
        self._on_track = terrain == "track" or arrive_on_track
        if soil > 0:
            self._trench_remaining_t -= soil
            self._trench_filled = self._trench_remaining_t == 0
        return distance

    def calculate_energy(
        self, speed_kmh: float, time_h: float, terrain: str
    ) -> float:
        """Рассчитать только движение, без расхода уборочной машины."""
        _, distance = self._movement(speed_kmh, time_h, terrain)
        return distance * {"track": 0, "ground": 2, "sand": 4}[terrain]

    def can_overcome(self, obstacle_width_m: float) -> bool:
        """Проверить ширину препятствия относительно диаметра колеса."""
        width = _number(obstacle_width_m, "obstacle_width_m")
        if width < 0:
            raise ValueError("obstacle width must not be negative")
        return width <= self._wheel_diameter_m / 2

    def recharge(self, target_energy: float) -> None:
        """Зарядить до целевого уровня на любой направляющей борозде."""
        target = _number(target_energy, "target_energy")
        if not self._energy <= target <= 100:
            raise ValueError("target must be between current energy and 100")
        if not self._on_track:
            raise MonowheelNotOnTrack("recharging requires a track")
        self._energy = target

    def open_gondola(self) -> None:
        """Открыть гондолу; повторный вызов допустим."""
        self._gondola_open = True

    def close_gondola(self) -> None:
        """Закрыть гондолу; повторный вызов допустим."""
        self._gondola_open = False

    def attach_equipment(self) -> None:
        """Подключить выключенную уборочную машину."""
        if self._equipment_attached:
            raise MonowheelEquipmentError("equipment is already attached")
        self._equipment_attached = True

    def detach_equipment(self) -> None:
        """Отсоединить и выключить уборочную машину."""
        if not self._equipment_attached:
            raise MonowheelEquipmentError("equipment is not attached")
        self._equipment_attached = False
        self._equipment_active = False

    def set_equipment_active(self, active: bool) -> None:
        """Включить подключённую машину либо выключить оборудование."""
        _boolean(active, "active")
        if active and not self._equipment_attached:
            raise MonowheelEquipmentError("attach equipment before enabling")
        self._equipment_active = active

    def assess_trench(self, volume_t: float) -> None:
        """Заменить оценку рва и начать учёт его засыпки заново."""
        volume = _number(volume_t, "volume_t")
        if volume <= 0:
            raise ValueError("trench volume must be positive")
        self._trench_volume_t = volume
        self._trench_remaining_t = volume
        self._trench_filled = False

    def set_helper_active(self, active: bool) -> None:
        """Включить или выключить помощника без расхода энергии."""
        self._helper_active = _boolean(active, "active")

    def get_status(self) -> dict:
        """Вернуть независимый снимок всех публичных атрибутов."""
        return {
            "name": self._name,
            "wheel_diameter_m": self._wheel_diameter_m,
            "max_speed_kmh": self._max_speed_kmh,
            "energy": self._energy,
            "position_km": self._position_km,
            "mileage_km": self._mileage_km,
            "on_track": self._on_track,
            "gondola_open": self._gondola_open,
            "equipment_attached": self._equipment_attached,
            "equipment_active": self._equipment_active,
            "helper_active": self._helper_active,
            "trench_volume_t": self._trench_volume_t,
            "trench_remaining_t": self._trench_remaining_t,
            "trench_filled": self._trench_filled,
        }
