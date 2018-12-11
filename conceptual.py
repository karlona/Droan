import math


class Phase:
    """ This class details the various phases associated with the mission. """

    def __init__(self, final_speed, lift_over_drag, time, vertical_speed, speed_change):
        """final_speed in m/s, lift_over_drag no units, time in seconds, vertical_speed in m/s, speed_change in m/s. """
        self.final_speed = final_speed
        self.lift_over_drag = lift_over_drag
        self.time = time
        self.vertical_speed = vertical_speed
        self.speed_change = speed_change
        self.maximum_power = None

    def add_maximum_power(self, power):
        self.maximum_power = power


class Mission:
    """ All the phases are combined into a mission. """

    def __init__(self, takeoff_weight_guess):
        self.all_phases = []
        self.unique_phases = []
        self.takeoff_weight_guess = takeoff_weight_guess
        self.maximum_power = None

    def add_all_phases(self, phases):
        [self.all_phases.append(phase) for phase in phases]

    def compile_unique_phases(self, phases):
        [self.unique_phases.append(phase) for phase in phases]

    def add_maximum_power(self):
        power = []
        [power.append(phase.maximum_power) for phase in self.unique_phases]
        self.maximum_power = max(power)


class Motor:
    """ User inputs specifications for the electric motor chosen. """

    def __init__(self, input_voltage, whole_chain_efficiency, max_continuous_power):
        self.input_voltage = input_voltage
        self.whole_chain_efficiency = whole_chain_efficiency
        self.max_continuous_power = max_continuous_power


class Battery:
    """ User inputs specifications for the battery chemistry chosen. """

    def __init__(self, nominal_cell_voltage, c_max, cell_capacity, specific_energy_density):
        self.nominal_cell_voltage = nominal_cell_voltage
        self.c_max = c_max
        self.cell_capacity = cell_capacity
        self.specific_energy_density = specific_energy_density
        self.battery_cell_mass = self.cell_capacity * self.nominal_cell_voltage / self.specific_energy_density


class PhasePower:
    """ Determine the mission phase that has the maximum power requirements."""

    def __init__(self, mission):
        [self.calculate_power(phase, mission.takeoff_weight_guess) for phase in mission.unique_phases]
        mission.add_maximum_power()

    def calculate_power(self, phase, mass):
        power = self.calculate_energy_delta_power(phase, mass) \
                + self.calculate_aerodynamic_power(phase.final_speed, phase.speed_change, phase.lift_over_drag, mass)
        phase.add_maximum_power(power)

    def calculate_energy_delta_power(self, phase, mass):
        total_energy_delta = self.calculate_kinetic_delta(phase.final_speed, phase.speed_change, mass) \
                             + self.calculate_potential_delta(phase.time, phase.vertical_speed, mass)
        return total_energy_delta / phase.time

    def calculate_kinetic_delta(self, final_speed, speed_change, mass):
        initial_velocity = final_speed - speed_change
        square_velocity_difference = final_speed ** 2 - initial_velocity ** 2
        return (mass / 2) * square_velocity_difference

    def calculate_potential_delta(self, time, vertical_speed, mass):
        altitude_delta = time * vertical_speed
        return 9.80665 * mass * altitude_delta

    def calculate_aerodynamic_power(self, final_speed, speed_change, lift_over_drag, mass):
        maximum_speed = self.calculate_maximum_speed(final_speed, speed_change)
        weight = 9.80665 * mass
        return weight * maximum_speed / lift_over_drag

    def calculate_maximum_speed(self, final_speed, speed_change):
        initial_speed = final_speed - speed_change
        if final_speed == initial_speed:
            return final_speed
        else:
            return max(final_speed, initial_speed)


class BatteryPackMass:
    """ The aircraft battery is sized to execute the provided mission with appropriate power and capacity. """

    def __init__(self, maximum_power, motor, mission, battery):
        self.number_in_series = self.size_number_in_series(motor.input_voltage, battery.nominal_cell_voltage)
        self.number_in_parallel = self.size_number_in_parallel(maximum_power, battery,
                                                               motor, mission)
        self.number_of_cells = self.number_in_series * self.number_in_parallel
        self.battery_pack_mass = self.number_of_cells * battery.battery_cell_mass

    def size_number_in_series(self, input_voltage, nominal_cell_voltage):
        return math.ceil(input_voltage / nominal_cell_voltage)

    def size_number_in_parallel(self, phase_power, battery, motor, mission):
        power = self.size_parallel_for_power(phase_power, battery, motor)
        endurance = self.size_parallel_for_endurance(phase_power, battery, motor, mission)
        return max(power, endurance)

    def size_parallel_for_endurance(self, phase_power, battery, motor, mission):
        phase_energy = [phase_power.power_mission_phase[phase] * mission.phases[phase][2]
                        for phase in range(mission.unique_phases)]
        cell_energy_capacity = battery.nominal_cell_voltage * battery.cell_capacity * motor.whole_chain_efficiency
        phase_parallel = [phase_energy[phase] / cell_energy_capacity for phase in range(mission.unique_phases)]
        return sum(phase_parallel)

    def size_parallel_for_power(self, phase_power, battery, motor):
        max_power = phase_power.maximum_power
        c_max = battery.c_max
        cell_capacity = battery.cell_capacity
        whole_chain_efficiency = motor.whole_chain_efficiency
        battery_pack_voltage = self.number_in_series * battery.nominal_cell_voltage
        return max_power / (c_max * cell_capacity * whole_chain_efficiency * battery_pack_voltage)


class EmptyWeight:
    def __init__(self):
        return


class TakeoffWeight:
    def __init__(self):
        return


taxi = Phase(3, 15, 30, 0, 3)
takeoff = Phase(13.4, 15, 10, 0, 13.4)
climb = Phase(22.4, 10, 48, 2.54, 9)
endurance = Phase(22.4, 20, 1800, 0, 0)
descent = Phase(13.4, 15, 48, -2.54, -9)
pattern = Phase(13.4, 10, 60, 0, 0)
land = Phase(0, 5, 15, -1, -13.4)
droan_mission = Mission(12.5)
# I feel like compile_unique_phases could be automated fairly easily
droan_mission.compile_unique_phases([taxi, takeoff, climb, endurance, descent, pattern, land])
droan_mission.add_all_phases([taxi, takeoff, climb, endurance, descent, pattern, land, taxi])
droan_power_per_phase = PhasePower(droan_mission)
print(droan_power_per_phase.maximum_power)
droan_motor = Motor(11.1, 0.8, 110)
droan_battery = Battery(3.7, 25, 0.5, 200)
droan_battery_pack_mass = BatteryPackMass(droan_power_per_phase, droan_motor, droan_mission,
                                          droan_battery).battery_pack_mass
print(droan_battery_pack_mass)
