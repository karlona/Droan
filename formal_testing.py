from preliminary_sizing import *
import unittest


class FormalTesting(unittest.TestCase):

    def test_mission(self):
        taxi = Phase("taxi", 3, 15, 30, 0, 3)
        takeoff = Phase("takeoff", 13.4, 15, 10, 0, 13.4)
        land = Phase("land", 0, 5, 30, -1, -13.4)
        land_duplicate = Phase("land", 0, 5, 30, -1, -13.4)

        mission1  = Mission(12.5)
        mission1.add_all_phases([taxi, takeoff, land, land_duplicate])
        self.assertEqual(len(mission1.unique_phases), 3)
        self.assertEqual(len(mission1.all_phases), 4)

        mission2 = Mission(13.5)
        mission2.add_all_phases([taxi, taxi, taxi])
        self.assertEqual(len(mission2.unique_phases), 1)
        self.assertEqual(len(mission2.all_phases), 3)

if __name__ == '__main__':
    unittest.main()