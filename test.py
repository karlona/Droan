from preliminary_sizing import *

taxi = Phase("taxi", 3, 15, 30, 0, 3, 0)
takeoff = Phase("takeoff", 13.4, 15, 10, 0, 13.4, 0)
climb = Phase("climb", 22.4, 10, 48, 2.5, 9, 120)
endurance = Phase("endurance", 22.4, 20, 1800, 0, 0, 120)
descent = Phase("descent", 13.4, 15, 36, -2.5, -9, 30)
pattern = Phase("pattern", 13.4, 10, 60, 0, 0, 30)
land = Phase("land", 0, 5, 30, -1, -13.4, 0)
land_duplicate = Phase("land", 0, 5, 30, -1, -13.4, 0)

droan_endurance_mission = Mission(12.5, 1, 100)
droan_motor = Motor(11.1, 0.8, 110)
droan_battery = Battery(11.1, 25, 2.2, 140)  # Gens ace 25C 2200mah 11.1V 3S Lipo Battery

droan_endurance_mission.add_all_phases([taxi, takeoff, climb, endurance, descent, pattern, land, taxi])
droan_power_per_phase = PhasePower(droan_endurance_mission)
droan_battery_pack = BatteryPackMass(droan_motor, droan_endurance_mission, droan_battery)
droan_battery_pack_mass = BatteryPackMass(droan_motor, droan_endurance_mission, droan_battery).battery_pack_mass

print("Maximum mission power is " + str(math.ceil(droan_endurance_mission.maximum_power)) + " watts.")
print(str(droan_battery_pack.number_in_series) + " batteries in series.")
print(str(droan_battery_pack.number_in_parallel) + " batteries in parallel.")
print(str(droan_battery_pack.number_of_cells) + " total batteries.")
print("Each battery has a mass of " + str(round(droan_battery.battery_cell_mass, 3)) + " kilograms")
print("Total battery pack mass is " + str(round(droan_battery_pack_mass, 3)) + " kilograms")

bowers_fly_baby_1b = SimilarPlane(441, 295)
bushby_mm_1_85 = SimilarPlane(397, 261)
cassutt_ii = SimilarPlane(363, 196)
monnett_sonera_i = SimilarPlane(340, 200)
mooney_mite = SimilarPlane(354, 229)
pazmany_pl_2a = SimilarPlane(642, 397)
pazmany_pl_4a = SimilarPlane(386, 262)
quickie_q2 = SimilarPlane(454, 215)
rutan_variviggen = SimilarPlane(771, 431)
rutan_varieze = SimilarPlane(476, 254)
rutan_longeze = SimilarPlane(601, 340)
zenith_ch_200 = SimilarPlane(680, 400)
pik_21 = SimilarPlane(320, 199)
croses_eac_3 = SimilarPlane(260, 141)
gatard_ag02 = SimilarPlane(280, 170)
jodel_d92 = SimilarPlane(320, 191)
jurca_mj_5ea2 = SimilarPlane(680, 430)
piel_emeraude_cp320 = SimilarPlane(650, 410)
piel_super_diamant = SimilarPlane(850, 520)
pottier_p50 = SimilarPlane(400, 270)
stelio_frati_falco_f8l = SimilarPlane(820, 550)
nasa_gl_10 = SimilarPlane(26, 21)
roskam_home_built = HistoricalTrend()
roskam_home_built.add_similar_planes([bowers_fly_baby_1b, bushby_mm_1_85, cassutt_ii, monnett_sonera_i, mooney_mite,
                                      pazmany_pl_2a, pazmany_pl_4a, quickie_q2, rutan_variviggen, rutan_varieze,
                                      rutan_longeze, zenith_ch_200, pik_21, croses_eac_3, gatard_ag02, jodel_d92,
                                      jurca_mj_5ea2, piel_emeraude_cp320, piel_super_diamant, pottier_p50,
                                      stelio_frati_falco_f8l, nasa_gl_10])

droan_empty_mass_required = roskam_home_built.calculate_empty_mass_required(12.5)
iteration = MassIteration(droan_motor, droan_endurance_mission, droan_battery, roskam_home_built)
print("Empty mass is " + str(round(iteration.iterated_empty_mass, 3)) + " kilograms")
print("Takeoff mass is " + str(round(iteration.iterated_takeoff_mass, 3)) + " kilograms")

matching = Matching(iteration.iterated_takeoff_mass, max_wing_loading=2000)
print(matching.estimate_drag_polar(iteration.iterated_takeoff_mass, 1000, 13, 6, True, 0.85, 2.0))  # Delete after use
matching.create_matching_chart()

# **** Plot various lines to be shown on Matching Chart ****
matching.plot_stall_speed('Stall 13 m/s CL=1.5', 1000, 1.5, 13)
matching.plot_stall_speed('Stall 13 m/s CL=2.0', 1000, 2.0, 13, pattern='--')
matching.plot_stall_speed('Stall 13 m/s CL=2.5', 1000, 2.5, 13, pattern='-.')
matching.plot_stall_speed('Stall 13 m/s CL=3.0', 1000, 3.0, 13, pattern=':')
matching.plot_stall_speed('Stall 13 m/s CL=4.0', 1000, 4.0, 13)
matching.plot_stall_speed('Stall 13 m/s CL=5.0', 1000, 5.0, 13)
matching.plot_takeoff_distance('Takeoff CL=1.5', 100, 1000, 1.5)  # Cl_max should be ~1.5, but DEP multiplies it by 2
matching.plot_takeoff_distance('Takeoff CL=2.0', 100, 1000, 2.0, pattern='--')
matching.plot_takeoff_distance('Takeoff CL=2.5', 100, 1000, 2.5, pattern='-.')
matching.plot_takeoff_distance('Takeoff CL=3.0', 100, 1000, 3.0, pattern=':')
matching.plot_landing_distance('Landing CL=1.5', 1000, 100, 1.5)
matching.plot_landing_distance('Landing CL=2.0', 1000, 100, 2.0, pattern='--')
matching.plot_landing_distance('Landing CL=2.5', 1000, 100, 2.5, pattern='-.')
matching.plot_landing_distance('Landing CL=3.0', 1000, 100, 3.0, pattern=':')
matching.plot_climbing_requirements(
    'Climb AR=5', iteration.iterated_takeoff_mass, 1000, climb.final_speed, 5, 2.54, gear_down=True)
matching.plot_climbing_requirements(
    'Climb AR=6', iteration.iterated_takeoff_mass, 1000, climb.final_speed, 6, 2.54, gear_down=True, pattern='--')
matching.plot_climbing_requirements(
    'Climb AR=7', iteration.iterated_takeoff_mass, 1000, climb.final_speed, 7, 2.54, gear_down=True, pattern='-.')
matching.plot_climbing_requirements(
    'Climb AR=8', iteration.iterated_takeoff_mass, 1000, climb.final_speed, 8, 2.54, gear_down=True, pattern=':')
matching.plot_cruise_speed_requirements('Cruise 22.5 m/s', 22.5, 100, 0.5, iteration.iterated_takeoff_mass, 10)
# **** Plot various lines to be shown on Matching Chart ****

matching.plot_matching_chart()


# print(iteration.iterated_empty_mass)
# print(iteration.iterated_takeoff_mass)

# print("*** New Mission Below ***")
#
# pattern_climb = Phase("pattern_climb", 13.4, 10, 12, 2.54, 0)
# touch_and_go_pattern = Phase("touch_and_go_pattern", 13.4, 10, 60, 0, 0)
#
# droan_touch_and_go_mission = Mission(12.5, 1)
# droan_touch_and_go_mission.add_all_phases([taxi, takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land,
#                                            takeoff, pattern_climb, touch_and_go_pattern, land, taxi])
# droan_power_per_phase_touch_and_go = PhasePower(droan_touch_and_go_mission)
# droan_battery_pack_touch_and_go = BatteryPackMass(droan_motor, droan_touch_and_go_mission, droan_battery)
# droan_battery_pack_mass_touch_and_go = BatteryPackMass(droan_motor, droan_touch_and_go_mission,
#                                                        droan_battery).battery_pack_mass
#
# for phase in droan_touch_and_go_mission.unique_phases:
#     print("Power during {} is ".format(phase.name) + str(math.ceil(phase.maximum_power)) + " Watts.")
# print("Maximum mission power is " + str(math.ceil(droan_touch_and_go_mission.maximum_power)) + " watts.")
# print(str(droan_battery_pack_touch_and_go.number_in_series) + " batteries in series.")
# print(str(droan_battery_pack_touch_and_go.number_in_parallel_endurance) + " batteries in parallel for endurance.")
# print(str(droan_battery_pack_touch_and_go.number_in_parallel_power) + " batteries in parallel for power.")
# print(str(droan_battery_pack_touch_and_go.number_in_parallel) + " batteries in parallel.")
# print(str(droan_battery_pack_touch_and_go.number_of_cells) + " total batteries.")
# print("Each battery has a mass of " + str(round(droan_battery.battery_cell_mass, 3)) + " kilograms")
# #Check out these two print lines, copies of above - I think these are easier than doing "+" and I prefer the first one
# #Use these techniques to fix the line in the for loop above (was line 21 as of this writing)
# print("Each battery has a mass of {} kilograms".format(str(round(droan_battery.battery_cell_mass, 3))))
# print("Each battery has a mass of %s kilograms" % str(round(droan_battery.battery_cell_mass, 3)))
# print("Total battery pack mass is " + str(round(droan_battery_pack_mass_touch_and_go, 3)) + " kilograms")
# #Check out this line as well - this is why you need the __str__ method for Phase
# print(*droan_endurance_mission.unique_phases, sep = "\n")
