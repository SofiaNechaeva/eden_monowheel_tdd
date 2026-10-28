import unittest

from eden_monowheel import EdenMonowheel, MonowheelGondolaOpen, MonowheelNoEnergy, MonowheelNotOnTrack
from tests.pilot import Pilot


class EdenMonowheelScenarioTests(unittest.TestCase):
    def test_TC_055_escape_from_broken_track(self):
        # Given
        wheel = EdenMonowheel("Эдем-1", 4, 300, 60)
        wheel.on_track = True
        pilot = Pilot(wheel)

        # When / Then: основная борозда и повреждённый участок
        self.assertEqual(pilot.drive(300, 0.2, "track", main_track=True), 60)
        self.assertEqual(pilot.drive(40, 0.5, "ground"), 20)
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy, wheel.on_track), (60, 80, 20, False))
        # When / Then: расщелина и недостаток энергии для объезда
        self.assertFalse(wheel.can_overcome(2.5))
        with self.assertRaises(MonowheelNoEnergy): 
            pilot.drive(30, 0.5, "ground")
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (60, 80, 20))
        # When / Then: боковая борозда, зарядка, объезд и возвращение на основную
        pilot.arrive_at_track(20, 0.25)
        pilot.recharge_to(90)
        pilot.drive(20, 0.25, "ground")
        pilot.drive(30, 0.5, "ground")
        pilot.drive(300, 0.2, "track", main_track=True)
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy, wheel.on_track), (120, 165, 50, True))

    def test_TC_056_trench_filling_adventure(self):
        # Given
        wheel = EdenMonowheel("Эдем-2", 4, 300, 80)
        pilot = Pilot(wheel)
        pilot.attach_cleaner()
        trench = 3
        # When / Then: оценка рва и три рабочих прохода
        self.assertFalse(wheel.can_overcome(trench))
        wheel.assess_trench(3)
        pilot.enable_cleaner()
        pilot.drive(20, 0.05, "ground")
        self.assertEqual((wheel.trench_remaining_t, wheel.mileage_km, wheel.energy), (2, 1, 63))
        pilot.drive(-20, 0.05, "ground")
        self.assertEqual((wheel.trench_remaining_t, wheel.mileage_km, wheel.energy), (1, 2, 46))
        pilot.drive(20, 0.05, "ground")
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.mileage_km, wheel.energy), (0, True, 3, 29))
        # When / Then: проезд по засыпанному рву
        pilot.disable_cleaner()
        pilot.drive(20, 0.25, "ground")
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy, wheel.equipment_active), (0, 8, 19, False))

    def test_TC_057_novice_pilot_adventure(self):
        # Given
        wheel = EdenMonowheel("Эдем-3", 4, 300, 50)
        wheel.on_track = True
        pilot = Pilot(wheel)
        # When / Then: открытая гондола не позволяет ехать
        pilot.open_gondola()
        with self.assertRaises(MonowheelGondolaOpen): 
            pilot.drive(100, 0.1, "track", main_track=True)
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (0, 0, 50))
        # When / Then: поездка по борозде и ограничение без помощника
        pilot.close_gondola()
        pilot.drive(100, 0.1, "track", main_track=True)
        with self.assertRaises(ValueError):
            pilot.drive(100, 0.1, "ground")
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (10, 10, 50))
        # When / Then: помощник позволяет ехать по грунту
        pilot.enable_helper()
        pilot.drive(50, 0.2, "ground")
        pilot.disable_helper()
        with self.assertRaises(ValueError): 
            pilot.drive(50, 0.2, "ground")
        pilot.enable_helper()
        with self.assertRaises(MonowheelNotOnTrack):
            pilot.recharge_to(100)
        # When / Then: боковая борозда и зарядка
        pilot.arrive_at_track(50, 0.2)
        pilot.drive(100, 0.1, "track")
        pilot.recharge_to(70)
        pilot.disable_helper()
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy, wheel.on_track, wheel.helper_active, wheel.gondola_open), (10, 40, 70, True, False, False))
