import math


class Phase:
    """ This class details the various phases associated with the mission. """

    def __init__(self, name, final_speed, lift_over_drag, time, vertical_speed, speed_change):
        """
        name is a string naming the mission phase
        final_speed in m/s
        lift_over_drag no units
        time in seconds
        vertical_speed in m/s
        speed_change in m/s
        """
        self.name = name
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
        # Lowest voltage ratio at which you still want to execute max power, i.e. 0.8 is 80% of full charge !voltage!
        self.lowest_voltage_maximum_power_ratio = 0.8
        self.maximum_power = None

    def add_all_phases(self, phases):
        [self.all_phases.append(phase) for phase in phases]
        self.compile_unique_phases()

    def compile_unique_phases(self):  # Unsure how to not use a for loop here
        for specific_phase in self.all_phases:
            if self.unique_phases.count(specific_phase) >= 1:
                pass
            else:
                self.unique_phases.append(specific_phase)

    def add_maximum_power(self):
        power = []
        [power.append(phase.maximum_power) for phase in self.unique_phases]
        self.maximum_power = max(power)


class Motor:
    """ User inputs specifications for the electric motor chosen. """

    def __init__(self, input_voltage, whole_chain_efficiency, max_continuous_power):
        """
        input_voltage in volts
        whole chain efficiency no units as a decimal less than or equal to 1 and greater than 0
        max_continuous_power in watts
        """
        self.input_voltage = input_voltage
        self.whole_chain_efficiency = whole_chain_efficiency
        self.max_continuous_power = max_continuous_power


class Battery:
    """ User inputs specifications for the battery chemistry chosen. """

    def __init__(self, nominal_cell_voltage, c_max, cell_capacity, specific_energy_density):
        """
        nominal_cell_voltage in volts
        c_max in Amps per Amp - hour (current / battery capacity)
        cell_capacity in ampere hours
        specific_energy_density in watt hours per kilogram
        """
        self.nominal_cell_voltage = nominal_cell_voltage
        self.c_max = c_max / 3600  # Convert 1/hours to 1/seconds
        self.cell_capacity = cell_capacity * 3600  # Convert ampere hours to ampere seconds
        self.specific_energy_density = specific_energy_density * 3600  # Convert W-h/kg to W-s/kg
        self.battery_cell_mass = self.cell_capacity * self.nominal_cell_voltage / self.specific_energy_density


class PhasePower:
    """ Calculate maximum power required for each phase. This seems like a large function lol, but whatever. We'll
    talk about next time we talk."""

    def __init__(self, mission):
        [self.calculate_power(phase, mission.takeoff_weight_guess) for phase in mission.unique_phases]
        mission.add_maximum_power()

    def calculate_power(self, phase, mass):
        power = self.calculate_energy_delta_power(phase, mass) \
                + self.calculate_aerodynamic_power(phase.final_speed, phase.speed_change, phase.lift_over_drag, mass)
        if power > 0:  # Assuming that energy recovery is not an option
            phase.add_maximum_power(power)
        else:
            phase.add_maximum_power(0)

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

    def __init__(self, motor, mission, battery):
        self.number_in_series = self.size_number_in_series(motor.input_voltage, battery.nominal_cell_voltage)
        self.number_in_parallel_power = None
        self.number_in_parallel_endurance = None
        self.number_in_parallel = self.size_number_in_parallel(battery, motor.whole_chain_efficiency,
                                                               mission.all_phases, mission.maximum_power,
                                                               mission.lowest_voltage_maximum_power_ratio)
        self.number_of_cells = self.number_in_series * self.number_in_parallel
        self.battery_pack_mass = self.number_of_cells * battery.battery_cell_mass

    def size_number_in_series(self, input_voltage, nominal_cell_voltage):
        return math.ceil(input_voltage / nominal_cell_voltage)

    def size_number_in_parallel(self, battery, efficiency, all_phases, max_power, low_voltage_ratio):
        parallel_power = self.size_parallel_for_power(max_power, battery.nominal_cell_voltage, efficiency,
                                                      battery.c_max, battery.cell_capacity, low_voltage_ratio)
        parallel_endurance = self.size_parallel_for_endurance(battery.nominal_cell_voltage, battery.cell_capacity,
                                                              efficiency, all_phases)
        return math.ceil(max(parallel_power, parallel_endurance))

    def size_parallel_for_endurance(self, cell_voltage, cell_capacity, efficiency, phases):
        phase_energy = [specific_phase.maximum_power * specific_phase.time for specific_phase in phases]
        cell_energy_capacity = cell_voltage * cell_capacity * efficiency
        self.number_in_parallel_endurance = math.ceil(sum(phase_energy) / cell_energy_capacity)
        return math.ceil(sum(phase_energy) / cell_energy_capacity)

    def size_parallel_for_power(self, max_power, cell_voltage, efficiency, c_max, cell_capacity, low_voltage_ratio):
        battery_pack_voltage = self.number_in_series * cell_voltage * low_voltage_ratio
        self.number_in_parallel_power = math.ceil(max_power / (c_max * cell_capacity * efficiency
                                                               * battery_pack_voltage))
        return math.ceil(max_power / (c_max * cell_capacity * efficiency * battery_pack_voltage))


class EmptyWeight:
    def __init__(self):
        return


class TakeoffWeight:
    def __init__(self):
        return
