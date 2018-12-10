import math


class MissionSpecifications:
    """ Complete
    This class enables the documentation of a possible mission for an aircraft to be designed around. """

    def __init__(self, payload, length, length_type, speed, altitude, runway, climb, turn, unique_phases, guess):
        """ Mission requirements are the inputs for a conceptual aircraft design.

        Inputs: payload is the payload mass in kilograms, length is either the mission range in kilometers or the
        mission endurance in minutes, length_type is either the string 'range' or 'endurance' based on length, speed
        is the cruise speed in meters per second, altitude is the cruise altitude in meters, runway is the runway
        length in meters, climb is the climb rate in meters per second, turn is the turn radius in meters, phases is
        an integer detailing the number of phases in the mission profile, guess is the takeoff weight guess in
        kilograms. """

        # Create Class Variables
        self.payload = payload
        if length_type == 'range':
            self.range = length
        elif length_type == 'endurance':
            self.endurance = length
        else:
            raise NameError('Length type {} not found.  Accepted length types are \'range\' and \'endurance.\'')
        self.speed_cruise = speed
        self.altitude_cruise = altitude
        self.field_length = runway
        self.climb = climb
        self.turn_radius = turn
        self.unique_phases = unique_phases
        self.takeoff_weight_guess = guess

        # Detail specifics of each mission phase
        self.phases = [self.input_phase_details(phase) for phase in range(self.unique_phases)]

    def input_phase_details(self, phase):
        final_speed = float(input("Input phase {0} final speed in m/s.".format(str(phase))))
        lift_over_drag = float(input("Input phase {0} L/D.".format(str(phase))))
        time = float(input("Input phase {0} time in s.".format(str(phase))))
        vertical_speed = float(input("Input phase {0} vertical speed in m/s.".format(str(phase))))
        speed_change = float(input("Input phase {0} speed change in m/s.".format(str(phase))))
        return [final_speed, lift_over_drag, time, vertical_speed, speed_change]


class MaximumPower:
    """ Complete
    Determine the mission phase that has the maximum power requirements."""

    def __init__(self, mission_specifications):
        self.power_mission_phase = [self.calculate_power(mission_specifications, phase)
                                    for phase in range(mission_specifications.unique_phases)]
        self.maximum_power = max(self.power_mission_phase)

    def calculate_power(self, mission_specifications, phase):
        return self.calculate_energy_delta_power(mission_specifications, phase) \
               + self.calculate_aerodynamic_power(mission_specifications, phase)

    def calculate_energy_delta_power(self, mission_specifications, phase):
        total_energy_delta = self.calculate_kinetic_delta(mission_specifications, phase) \
                             + self.calculate_potential_delta(mission_specifications, phase)
        phase_time = mission_specifications.phases[phase][2]
        return total_energy_delta / phase_time

    def calculate_kinetic_delta(self, mission_specifications, phase):
        initial_velocity = mission_specifications.phases[phase][0] - mission_specifications.phases[phase][4]
        square_velocity_difference = mission_specifications.phases[phase][0] ** 2 - initial_velocity ** 2
        return (mission_specifications.takeoff_weight_guess / 2) * square_velocity_difference

    def calculate_potential_delta(self, mission_specifications, phase):
        altitude_delta = mission_specifications.phases[phase][2] * mission_specifications.phases[phase][3]
        return 9.80665 * mission_specifications.takeoff_weight_guess * altitude_delta

    def calculate_aerodynamic_power(self, mission_specifications, phase):
        maximum_speed = self.calculate_maximum_speed(mission_specifications, phase)
        weight = 9.80665 * mission_specifications.takeoff_weight_guess
        return weight * maximum_speed / mission_specifications.phases[phase][1]

    def calculate_maximum_speed(self, mission_specifications, phase):
        final_speed = mission_specifications.phases[phase][0]
        initial_speed = final_speed + mission_specifications.phases[phase][4]
        if final_speed == initial_speed:
            return final_speed
        else:
            return max(final_speed, initial_speed)


class MotorSpecifications:
    """ User inputs specifications for the electric motor chosen. """

    def __init__(self, input_voltage, whole_chain_efficiency, max_continuous_power):
        self.input_voltage = input_voltage
        self.whole_chain_efficiency = whole_chain_efficiency
        self.max_continuous_power = max_continuous_power


class BatterySpecifications:
    """ User inputs specifications for the battery chemistry chosen. """

    def __init__(self, nominal_cell_voltage, c_max, cell_capacity, specific_energy_density):
        self.nominal_cell_voltage = nominal_cell_voltage
        self.c_max = c_max
        self.cell_capacity = cell_capacity
        self.specific_energy_density = specific_energy_density
        self.battery_cell_mass = self.cell_capacity * self.nominal_cell_voltage / self.specific_energy_density


class BatteryPackMass:
    """ Complete
    The aircraft battery is sized to execute the provided mission with appropriate power and capacity. """

    def __init__(self, maximum_power, motor_specifications, mission_specifications, battery_specifications):
        self.number_in_series = self.size_number_in_series(motor_specifications, battery_specifications)
        self.number_in_parallel = self.size_number_in_parallel(maximum_power, battery_specifications,
                                                               motor_specifications, mission_specifications)
        self.number_of_cells = self.number_in_series * self.number_in_parallel
        self.battery_pack_mass = self.number_of_cells * self.battery_cell_mass

    def size_number_in_series(self, motor_specifications, battery_specifications):
        return math.ceil(motor_specifications.input_voltage / battery_specifications.nominal_cell_voltage)

    def size_number_in_parallel(self, maximum_power, battery_specifications, motor_specifications,
                                mission_specifications):
        power = self.size_parallel_for_power(maximum_power, battery_specifications, motor_specifications)
        endurance = self.size_parallel_for_endurance(maximum_power, battery_specifications, motor_specifications,
                                                     mission_specifications)
        return max(power, endurance)

    def size_parallel_for_endurance(self, maximum_power, battery_specifications, motor_specifications,
                                    mission_specifications):
        phase_energy = [maximum_power.power_mission_phase[phase] * mission_specifications.phases[phase][2]
                        for phase in range(mission_specifications.unique_phases)]
        cell_energy_capacity = battery_specifications.nominal_cell_voltage * battery_specifications.cell_capacity\
                               * motor_specifications.whole_chain_efficiency
        phase_parallel = [phase_energy[phase] / cell_energy_capacity for phase in mission_specifications.unique_phases]
        return sum(phase_parallel)

    def size_parallel_for_power(self, maximum_power, battery_specifications, motor_specifications):
        max_power = maximum_power.maximum_power
        c_max = battery_specifications.c_max
        cell_capacity = battery_specifications.cell_capacity
        whole_chain_efficiency = motor_specifications.whole_chain_efficiency
        battery_pack_voltage = self.number_in_series * battery_specifications.nominal_cell_voltage
        return max_power / (c_max * cell_capacity * whole_chain_efficiency * battery_pack_voltage)


class EmptyWeight:
    def __init__(self):
        return


class TakeoffWeight:
    def __init__(self):
        return


droan_mission = MissionSpecifications(1, 30, 'endurance', 22, 120, 120, 2.54, 75, 7, 12.5)
droan_power = MaximumPower(droan_mission)
droan_motor = MotorSpecifications(11.1, 0.8, 110)
droan_battery = BatterySpecifications(3.7, 25, 0.5, 200)
droan_battery_pack_mass = BatteryPackMass(droan_power, droan_motor, droan_mission, droan_battery).battery_pack_mass
print(droan_battery_pack_mass)
