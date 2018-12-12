from preliminary_sizing import *

taxi = Phase("taxi", 3, 15, 30, 0, 3)
takeoff = Phase("takeoff", 13.4, 15, 10, 0, 13.4)
climb = Phase("climb", 22.4, 10, 48, 2.54, 9)
endurance = Phase("endurance", 22.4, 20, 1800, 0, 0)
descent = Phase("descent", 13.4, 15, 48, -2.54, -9)
pattern = Phase("pattern", 13.4, 10, 60, 0, 0)
land = Phase("land", 0, 5, 15, -1, -13.4)

droan_mission = Mission(12.5)
droan_motor = Motor(11.1, 0.8, 110)
droan_battery = Battery(11.1, 25, 2.2, 140)  # Gens ace 25C 2200mah 11.1V 3S Lipo Battery

droan_mission.add_all_phases([taxi, takeoff, climb, endurance, descent, pattern, land, taxi])
droan_power_per_phase = PhasePower(droan_mission)
droan_battery_pack_mass = BatteryPackMass(droan_motor, droan_mission, droan_battery).battery_pack_mass

print([math.ceil(phase.maximum_power) for phase in droan_mission.unique_phases])
print("Maximum mission power is " + str(math.ceil(droan_mission.maximum_power)) + " watts.")
print("Each battery has a mass of " + str(round(droan_battery.battery_cell_mass, 3)) + " kilograms")
print("Total battery pack mass is " + str(round(droan_battery_pack_mass, 3)) + " kilograms")
