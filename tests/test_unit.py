"""Модульные тесты SPEC.md. Каждый тест построен по Arrange–Act–Assert."""

import unittest

from eden_monowheel import (
    EdenMonowheel,
    MonowheelEquipmentError,
    MonowheelError,
    MonowheelGondolaOpen,
    MonowheelNoEnergy,
    MonowheelNotOnTrack,
)


class EdenMonowheelUnitTests(unittest.TestCase):
    def make_wheel(self, energy=100):
        return EdenMonowheel("Эдем", 4, 300, energy)

    def snapshot(self, wheel):
        return wheel.get_status().copy()

    def assert_state(self, wheel, expected):
        self.assertEqual(wheel.get_status(), expected)

    def test_TC_001_init_valid(self):
        # Arrange / Act
        wheel = EdenMonowheel("Эдем", 4, 300, 80)
        # Assert
        self.assertEqual((wheel.name, wheel.wheel_diameter_m, wheel.max_speed_kmh, wheel.energy), ("Эдем", 4, 300, 80))

    def test_TC_002_init_empty_name_raises(self):
        # Arrange / Act / Assert
        with self.assertRaises(ValueError):
            EdenMonowheel("", 4, 300)

    def test_TC_003_init_invalid_diameter_raises(self):
        # Arrange / Act / Assert
        with self.assertRaises(ValueError):
            EdenMonowheel("Эдем", 0, 300)

    def test_TC_004_init_invalid_max_speed_raises(self):
        # Arrange / Act / Assert
        with self.assertRaises(ValueError):
            EdenMonowheel("Эдем", 4, -20)

    def test_TC_005_init_invalid_energy_raises(self):
        # Arrange / Act / Assert
        with self.assertRaises(ValueError):
            EdenMonowheel("Эдем", 4, 300, 120)

    def test_TC_006_init_default_state(self):
        # Arrange / Act
        wheel = self.make_wheel()
        # Assert
        self.assertEqual((wheel.energy, wheel.position_km, wheel.mileage_km), (100, 0, 0))
        self.assertFalse(any((wheel.on_track, wheel.gondola_open, wheel.equipment_attached, wheel.equipment_active, wheel.helper_active, wheel.trench_filled)))
        self.assertEqual(wheel.trench_remaining_t, 0)

    def test_TC_007_public_attributes(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        status = wheel.get_status()
        # Assert
        self.assertEqual(set(status), {"name", "wheel_diameter_m", "max_speed_kmh", "energy", "position_km", "mileage_km", "on_track", "gondola_open", "equipment_attached", "equipment_active", "helper_active", "trench_volume_t", "trench_remaining_t", "trench_filled"})
        self.assertIsInstance(wheel.name, str)
        for value in (wheel.wheel_diameter_m, wheel.max_speed_kmh, wheel.energy, wheel.position_km, wheel.mileage_km, wheel.trench_volume_t, wheel.trench_remaining_t):
            self.assertIsInstance(value, float)
        for value in (wheel.on_track, wheel.gondola_open, wheel.equipment_attached, wheel.equipment_active, wheel.helper_active, wheel.trench_filled):
            self.assertIsInstance(value, bool)

    def test_TC_008_move_main_track(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        distance = wheel.move(300, .1, "track", main_track=True)
        # Assert
        self.assertEqual((distance, wheel.position_km, wheel.mileage_km, wheel.energy, wheel.on_track), (30, 30, 30, 100, True))

    def test_TC_009_move_side_track(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        distance = wheel.move(100, .1, "track")
        # Assert
        self.assertEqual((distance, wheel.position_km, wheel.mileage_km, wheel.energy, wheel.on_track), (10, 0, 10, 100, True))

    def test_TC_010_move_ground_energy(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        distance = wheel.move(20, 0.5, "ground")
        # Assert
        self.assertEqual((distance, wheel.energy, wheel.position_km, wheel.mileage_km, wheel.on_track), (10, 80, 0, 10, False))

    def test_TC_011_move_sand_energy(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        distance = wheel.move(20, 0.5, "sand")
        # Assert
        self.assertEqual((distance, wheel.energy, wheel.mileage_km, wheel.position_km), (10, 60, 10, 0))

    def test_TC_012_move_track_no_energy_cost(self):
        # Arrange
        wheel = self.make_wheel(50)
        # Act
        wheel.move(100, .2, "track", main_track=True)
        # Assert
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (20, 20, 50))

    def test_TC_013_move_backward(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.move(300, .1, "track", main_track=True)
        # Act
        wheel.move(-100, .1, "track", main_track=True)
        # Assert
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (20, 40, 100))

    def test_TC_014_move_zero_speed(self):
        # Arrange
        wheel = self.make_wheel(80)
        wheel.move(100, .1, "track", main_track=True)
        wheel.open_gondola()
        before = self.snapshot(wheel)
        # Act
        distance = wheel.move(0, 0.5, "ground")
        # Assert
        self.assertEqual(distance, 0)
        self.assert_state(wheel, before)

    def test_TC_015_move_invalid_time_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(20, 0, "ground")
        self.assert_state(wheel, before)

    def test_TC_016_move_invalid_terrain_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(20, 1, "water")
        self.assert_state(wheel, before)

    def test_TC_017_move_speed_limit_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(50, .1, "ground")
        self.assert_state(wheel, before)

    def test_TC_018_helper_ground_speed_bonus(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.set_helper_active(True)
        # Act
        distance = wheel.move(50, .1, "ground")
        # Assert
        self.assertEqual((distance, wheel.mileage_km, wheel.energy, wheel.position_km), (5, 5, 90, 0))

    def test_TC_019_helper_sand_limit_unchanged(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.set_helper_active(True)
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(30, .1, "sand")
        self.assert_state(wheel, before)

    def test_TC_020_move_no_energy_raises(self):
        # Arrange
        wheel = self.make_wheel(10)
        # Act / Assert
        with self.assertRaises(MonowheelNoEnergy): 
            wheel.move(20, 0.5, "ground")
        self.assertEqual((wheel.energy, wheel.position_km, wheel.mileage_km), (10, 0, 0))

    def test_TC_021_move_open_gondola_raises(self):
        # Arrange
        wheel = self.make_wheel(0)
        wheel.open_gondola()
        # Act / Assert
        with self.assertRaises(MonowheelGondolaOpen): 
            wheel.move(20, .1, "ground")
        self.assertEqual((wheel.position_km, wheel.mileage_km, wheel.energy), (0, 0, 0))

    def test_TC_022_move_arrive_on_track(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        wheel.move(20, .25, "ground", arrive_on_track=True)
        # Assert
        self.assertEqual((wheel.mileage_km, wheel.position_km, wheel.energy, wheel.on_track), (5, 0, 90, True))

    def test_TC_023_move_ground_main_track_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(20, 0.5, "ground", main_track=True)
        self.assert_state(wheel, before)

    def test_TC_024_move_track_arrival_flag_raises(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(100, .1, "track", arrive_on_track=True)

    def test_TC_025_calculate_energy_no_state_change(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act
        cost = wheel.calculate_energy(20, 0.5, "ground")
        # Assert
        self.assertEqual(cost, 20)
        self.assert_state(wheel, before)

    def test_TC_026_can_overcome_width_limit(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        self.assertTrue(wheel.can_overcome(2))
        self.assert_state(wheel, before)

    def test_TC_027_can_overcome_too_wide(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        self.assertFalse(wheel.can_overcome(2.5))
        self.assert_state(wheel, before)

    def test_TC_028_can_overcome_negative_width_raises(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(ValueError): 
            wheel.can_overcome(-1)

    def test_TC_029_recharge_on_track(self):
        # Arrange
        wheel = self.make_wheel(50)
        wheel.move(1, 1, "track")
        # Act
        wheel.recharge(100)
        # Assert
        self.assertEqual((wheel.energy, wheel.position_km, wheel.mileage_km), (100, 0, 1))

    def test_TC_030_recharge_off_track_raises(self):
        # Arrange
        wheel = self.make_wheel(20)
        # Act / Assert
        with self.assertRaises(MonowheelNotOnTrack):
            wheel.recharge(70)
        self.assertEqual(wheel.energy, 20)

    def test_TC_031_recharge_over_100_raises(self):
        # Arrange
        wheel = self.make_wheel(20)
        wheel.move(1, 1, "track")
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.recharge(101)
        self.assertEqual(wheel.energy, 20)

    def test_TC_032_recharge_below_current_raises(self):
        # Arrange
        wheel = self.make_wheel(70)
        wheel.move(1, 1, "track")
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.recharge(20)
        self.assertEqual(wheel.energy, 70)

    def test_TC_033_open_gondola(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        wheel.open_gondola()
        self.assertTrue(wheel.gondola_open)

    def test_TC_034_close_gondola(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.open_gondola()
        # Act / Assert
        wheel.close_gondola()
        self.assertFalse(wheel.gondola_open)

    def test_TC_035_attach_equipment(self):
        # Arrange
        wheel = self.make_wheel()
        # Act 
        wheel.attach_equipment()
        # Assert
        self.assertTrue(wheel.equipment_attached)
        self.assertFalse(wheel.equipment_active)

    def test_TC_036_attach_equipment_twice_raises(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.attach_equipment()
        # Act
        with self.assertRaises(MonowheelEquipmentError): 
            wheel.attach_equipment()
        self.assertTrue(wheel.equipment_attached)

    def test_TC_037_detach_equipment(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.attach_equipment()
        wheel.set_equipment_active(True)
        # Act
        wheel.detach_equipment()
        # Assert
        self.assertFalse(wheel.equipment_attached)
        self.assertFalse(wheel.equipment_active)

    def test_TC_038_detach_missing_equipment_raises(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(MonowheelEquipmentError): 
            wheel.detach_equipment()

    def test_TC_039_set_equipment_active(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.attach_equipment()
        # Act
        wheel.set_equipment_active(True)
        # Assert
        self.assertTrue(wheel.equipment_active)
        self.assertTrue(wheel.equipment_attached)

    def test_TC_040_activate_missing_equipment_raises(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(MonowheelEquipmentError): 
            wheel.set_equipment_active(True)
        self.assertFalse(wheel.equipment_active)

    def test_TC_041_assess_trench(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.assess_trench(3)
        # Act
        wheel.assess_trench(2)
        # Assert
        self.assertEqual((wheel.trench_volume_t, wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (2, 2, False, 100))

    def test_TC_042_assess_trench_invalid_volume_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError): 
            wheel.assess_trench(-3)
        self.assert_state(wheel, before)

    def _equipped_wheel(self, energy=100, trench=3):
        wheel = self.make_wheel(energy)
        wheel.attach_equipment()
        wheel.assess_trench(trench)
        wheel.set_equipment_active(True)
        return wheel

    def test_TC_043_equipment_one_pass(self):
        # Arrange
        wheel = self._equipped_wheel()
        # Act
        wheel.move(20, .05, "ground")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.mileage_km, wheel.energy), (2, False, 1, 83))

    def test_TC_044_equipment_energy_cost(self):
        # Arrange
        wheel = self._equipped_wheel()
        # Act
        wheel.move(20, .05, "ground")
        # Assert
        self.assertEqual(wheel.energy, 83)

    def test_TC_045_trench_filled(self):
        # Arrange
        wheel = self._equipped_wheel(50, 1)
        # Act
        wheel.move(20, .05, "ground")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (0, True, 33))

    def test_TC_046_set_helper_active(self):
        # Arrange
        wheel = self.make_wheel()
        # Act
        wheel.set_helper_active(True)
        # Assert
        self.assertTrue(wheel.helper_active)
        self.assertEqual(wheel.energy, 100)

    def test_TC_047_status_keys(self):
        # Arrange
        wheel = self.make_wheel()
        expected = {
            "name": "Эдем",
            "wheel_diameter_m": 4.0,
            "max_speed_kmh": 300.0,
            "energy": 100.0,
            "position_km": 0.0,
            "mileage_km": 0.0,
            "on_track": False,
            "gondola_open": False,
            "equipment_attached": False,
            "equipment_active": False,
            "helper_active": False,
            "trench_volume_t": 0.0,
            "trench_remaining_t": 0.0,
            "trench_filled": False,
        }
        # Act
        status = wheel.get_status()
        # Assert
        self.assertIsInstance(status, dict)
        self.assertEqual(status, expected)
        for name, value in expected.items():
            self.assertEqual(getattr(wheel, name), value)

    def test_TC_048_invalid_parameters_raise(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError): 
            wheel.move("fast", 1, "ground")
        self.assert_state(wheel, before)

    def test_TC_049_domain_exception_hierarchy(self):
        # Arrange
        domain_errors = (MonowheelNoEnergy, MonowheelGondolaOpen, MonowheelNotOnTrack, MonowheelEquipmentError)
        # Act / Assert
        for error in domain_errors: 
            self.assertTrue(issubclass(error, MonowheelError))

    def test_TC_050_move_exact_energy(self):
        # Arrange
        wheel = self.make_wheel(20)
        # Act
        wheel.move(20, 0.5, "ground")
        # Assert
        self.assertEqual((wheel.energy, wheel.mileage_km, wheel.position_km), (0, 10, 0))

    def test_TC_051_move_one_energy_short(self):
        # Arrange
        wheel = self.make_wheel(19)
        before = self.snapshot(wheel)
        # Act # Assert
        with self.assertRaises(MonowheelNoEnergy): 
            wheel.move(20, 0.5, "ground")
        self.assert_state(wheel, before)

    def test_TC_052_set_helper_inactive(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.set_helper_active(True)
        # Act
        wheel.set_helper_active(False)
        # Assert
        self.assertFalse(wheel.helper_active)
        self.assertEqual(wheel.energy, 100)

    def test_TC_053_set_equipment_inactive(self):
        # Arrange
        wheel = self._equipped_wheel()
        # Act
        wheel.set_equipment_active(False)
        # Assert
        self.assertFalse(wheel.equipment_active)
        self.assertTrue(wheel.equipment_attached)

    def test_TC_054_equipment_partial_ton(self):
        # Arrange
        wheel = self._equipped_wheel(50, 0.5)
        # Act
        wheel.move(20, .05, "ground")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (0, True, 40.5))

    def test_TC_058_invalid_speed_has_priority_over_no_energy(self):
        # Arrange
        wheel = self.make_wheel(10)
        wheel.open_gondola()
        before = self.snapshot(wheel)

        # Act / Assert
        with self.assertRaises(ValueError): 
            wheel.move(60, .5, "ground")
        self.assert_state(wheel, before)

    def test_TC_059_equipment_no_energy_raises(self):
        # Arrange
        wheel = self._equipped_wheel(16, 1)
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(MonowheelNoEnergy):
            wheel.move(20, .05, "ground")
        self.assert_state(wheel, before)

    def test_TC_060_calculate_energy_invalid_parameters_raise(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        for speed, time, terrain in ((50, .1, "ground"), (20, .1, "water")):
            with self.subTest(speed=speed, terrain=terrain):
                with self.assertRaises(ValueError): 
                    wheel.calculate_energy(speed, time, terrain)
                self.assert_state(wheel, before)

    def test_TC_061_non_finite_numbers_raise(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)

        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(float("nan"), 0.1, "ground")
        self.assert_state(wheel, before)

        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(20, float("inf"), "ground")
        self.assert_state(wheel, before)

        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.can_overcome(float("inf"))
        self.assert_state(wheel, before)

    def test_TC_062_equipment_works_on_sand(self):
        # Arrange
        wheel = self._equipped_wheel(100, 1)
        # Act
        wheel.move(20, .05, "sand")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.mileage_km, wheel.energy), (0, True, 1, 81))

    def test_TC_063_helper_ground_speed_limit_raises(self):
        # Arrange
        wheel = self.make_wheel()
        wheel.set_helper_active(True)
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError): 
            wheel.move(60, .1, "ground")
        self.assert_state(wheel, before)

    def test_TC_064_equipment_works_after_starting_on_track(self):
        # Arrange
        wheel = self._equipped_wheel(100, 1)
        wheel.on_track = True
        # Act
        wheel.move(20, .05, "ground")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (0, True, 83))

    def test_TC_065_equipment_works_when_arriving_on_track(self):
        # Arrange
        wheel = self._equipped_wheel(100, 1)
        # Act
        wheel.move(20, .05, "ground", arrive_on_track=True)
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy, wheel.on_track), (0, True, 83, True))

    def test_TC_066_recharge_validates_target_before_track(self):
        # Arrange
        wheel = self.make_wheel(20)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.recharge(110)
        self.assertEqual(wheel.energy, 20)

    def test_TC_067_track_speed_limit_uses_absolute_value(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(-301, .1, "track", main_track=True)
        self.assert_state(wheel, before)

    def test_TC_068_constructive_speed_caps_helper_limit(self):
        # Arrange
        wheel = EdenMonowheel("Эдем", 4, 45, 100)
        wheel.set_helper_active(True)
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(46, .1, "ground")
        self.assert_state(wheel, before)

    def test_TC_069_invalid_route_flag_raises(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(20, .1, "ground", main_track="yes")
        self.assert_state(wheel, before)

    def test_TC_070_invalid_helper_flag_raises(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.set_helper_active("yes")
        self.assertFalse(wheel.helper_active)

    def test_TC_071_bool_is_not_numeric_speed(self):
        # Arrange
        wheel = self.make_wheel()
        before = self.snapshot(wheel)
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.move(True, .1, "ground")
        self.assert_state(wheel, before)

    def test_TC_072_read_only_energy_cannot_be_assigned(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(AttributeError):
            wheel.energy = 50

    def test_TC_073_on_track_requires_bool(self):
        # Arrange
        wheel = self.make_wheel()
        # Act / Assert
        with self.assertRaises(ValueError):
            wheel.on_track = "yes"
        self.assertFalse(wheel.on_track)

    def test_TC_074_equipment_does_not_work_on_track(self):
        # Arrange
        wheel = self._equipped_wheel(100, 1)
        # Act
        wheel.move(20, .05, "track")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (1, False, 100))

    def test_TC_075_equipment_does_not_work_without_movement(self):
        # Arrange
        wheel = self._equipped_wheel(100, 1)
        # Act
        wheel.move(0, .05, "ground")
        # Assert
        self.assertEqual((wheel.trench_remaining_t, wheel.trench_filled, wheel.energy), (1, False, 100))
