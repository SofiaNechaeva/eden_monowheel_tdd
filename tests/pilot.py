"""Тестовая обёртка-пилот для сценариев в стиле Given–When–Then."""

from eden_monowheel import EdenMonowheel


class Pilot:

    def __init__(self, monowheel: EdenMonowheel) -> None:
        self.monowheel = monowheel

    def drive(self, speed_kmh, time_h, terrain, **flags):
        return self.monowheel.move(speed_kmh, time_h, terrain, **flags)

    def arrive_at_track(self, speed_kmh, time_h, terrain="ground"):
        return self.drive(speed_kmh, time_h, terrain, arrive_on_track=True)

    def recharge_to(self, energy):
        self.monowheel.recharge(energy)

    def open_gondola(self):
        self.monowheel.open_gondola()

    def close_gondola(self):
        self.monowheel.close_gondola()

    def enable_helper(self):
        self.monowheel.set_helper_active(True)

    def disable_helper(self):
        self.monowheel.set_helper_active(False)

    def attach_cleaner(self):
        self.monowheel.attach_equipment()

    def enable_cleaner(self):
        self.monowheel.set_equipment_active(True)

    def disable_cleaner(self):
        self.monowheel.set_equipment_active(False)
