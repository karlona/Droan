from preliminary_sizing import *

taxi = Phase("taxi", 3, 15, 30, 0, 3)
takeoff = Phase("takeoff", 13.4, 15, 10, 0, 13.4)
climb = Phase("climb", 22.4, 10, 48, 2.54, 9)
endurance = Phase("endurance", 22.4, 20, 1800, 0, 0)
descent = Phase("descent", 13.4, 15, 48, -2.54, -9)
pattern = Phase("pattern", 13.4, 10, 60, 0, 0)
land = Phase("land", 0, 5, 30, -1, -13.4)

droan_endurance_mission = Mission(12.5)
droan_motor = Motor(11.1, 0.8, 110)
droan_battery = Battery(11.1, 25, 2.2, 140)  # Gens ace 25C 2200mah 11.1V 3S Lipo Battery

droan_endurance_mission.add_all_phases([taxi, takeoff, climb, endurance, descent, pattern, land, taxi])
droan_power_per_phase = PhasePower(droan_endurance_mission)
droan_battery_pack = BatteryPackMass(droan_motor, droan_endurance_mission, droan_battery)
droan_battery_pack_mass = BatteryPackMass(droan_motor, droan_endurance_mission, droan_battery).battery_pack_mass

for phase in droan_endurance_mission.unique_phases:
    print("Power during {} is ".format(phase.name) + str(math.ceil(phase.maximum_power)) + " Watts.")
print("Maximum mission power is " + str(math.ceil(droan_endurance_mission.maximum_power)) + " watts.")
print(str(droan_battery_pack.number_in_series) + " batteries in series.")
print(str(droan_battery_pack.number_in_parallel_endurance) + " batteries in parallel for endurance.")
print(str(droan_battery_pack.number_in_parallel_power) + " batteries in parallel for power.")
print(str(droan_battery_pack.number_in_parallel) + " batteries in parallel.")
print(str(droan_battery_pack.number_of_cells) + " total batteries.")
print("Each battery has a mass of " + str(round(droan_battery.battery_cell_mass, 3)) + " kilograms")
print("Total battery pack mass is " + str(round(droan_battery_pack_mass, 3)) + " kilograms")

print("*** New Mission Below ***")

pattern_climb = Phase("pattern_climb", 13.4, 10, 12, 2.54, 0)
touch_and_go_pattern = Phase("touch_and_go_pattern", 13.4, 10, 60, 0, 0)

droan_touch_and_go_mission = Mission(12.5)
droan_touch_and_go_mission.add_all_phases([taxi, takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land,
                                           takeoff, pattern_climb, touch_and_go_pattern, land, taxi])
droan_power_per_phase_touch_and_go = PhasePower(droan_touch_and_go_mission)
droan_battery_pack_touch_and_go = BatteryPackMass(droan_motor, droan_touch_and_go_mission, droan_battery)
droan_battery_pack_mass_touch_and_go = BatteryPackMass(droan_motor, droan_touch_and_go_mission,
                                                       droan_battery).battery_pack_mass

for phase in droan_touch_and_go_mission.unique_phases:
    print("Power during {} is ".format(phase.name) + str(math.ceil(phase.maximum_power)) + " Watts.")
print("Maximum mission power is " + str(math.ceil(droan_touch_and_go_mission.maximum_power)) + " watts.")
print(str(droan_battery_pack_touch_and_go.number_in_series) + " batteries in series.")
print(str(droan_battery_pack_touch_and_go.number_in_parallel_endurance) + " batteries in parallel for endurance.")
print(str(droan_battery_pack_touch_and_go.number_in_parallel_power) + " batteries in parallel for power.")
print(str(droan_battery_pack_touch_and_go.number_in_parallel) + " batteries in parallel.")
print(str(droan_battery_pack_touch_and_go.number_of_cells) + " total batteries.")
print("Each battery has a mass of " + str(round(droan_battery.battery_cell_mass, 3)) + " kilograms")
print("Total battery pack mass is " + str(round(droan_battery_pack_mass_touch_and_go, 3)) + " kilograms")
