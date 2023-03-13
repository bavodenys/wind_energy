import os
import json
import matplotlib.pyplot as plt
from calibrations import *
import math
from windrose import WindroseAxes
import numpy as np
from functions import *
import re

# info: https://towardsdatascience.com/wind-energy-physics-and-resource-assessment-with-python-789a0273e697
# info: https://power.larc.nasa.gov/data-access-viewer/
# https://www.tesup.nl/product-page/magnum5-windturbine-het-beste-Nederland

if __name__ == "__main__":
    data = os.listdir(DATA_FOLDER)
    for file in data:
        with open(f'{DATA_FOLDER}/{file}', 'r') as f:
                wind_data = json.load(f)
        wind_data_overview = {}
        wind_speed_list = []
        wind_direction_list = []
        wind_speed_distribution = {}
        wind_energy_distribution = {}
        for entry in wind_data['properties']['parameter']['WS10M']:
            if entry[0:4] == "2021":
                if entry[4:6] in wind_data_overview:
                    pass
                else:
                    wind_data_overview[entry[4:6]] = {}
                if entry[6:8] in wind_data_overview[entry[4:6]]:
                    pass
                else:
                    wind_data_overview[entry[4:6]][entry[6:8]] = {}
                wind_data_overview[entry[4:6]][entry[6:8]][entry[8:10]] = {'wind_speed': wind_data['properties']['parameter']['WS10M'][entry],
                                                                           'wind_direction': wind_data['properties']['parameter']['WD10M'][entry]}
                wind_speed_list.append(wind_data['properties']['parameter']['WS10M'][entry])
                wind_direction_list.append(wind_data['properties']['parameter']['WD10M'][entry])

                # Wind speeds distribution
                if int(wind_data['properties']['parameter']['WS10M'][entry]) in wind_speed_distribution:
                    wind_speed_distribution[int(wind_data['properties']['parameter']['WS10M'][entry])]+=1
                else:
                    wind_speed_distribution[int(wind_data['properties']['parameter']['WS10M'][entry])]=1

                # Wind energy distribution
                if int(wind_data['properties']['parameter']['WS10M'][entry]) in wind_energy_distribution:
                    wind_energy_distribution[int(wind_data['properties']['parameter']['WS10M'][entry])] += calculate_hourly_wind_energy(wind_data['properties']['parameter']['WS10M'][entry])
                else:
                    wind_energy_distribution[int(wind_data['properties']['parameter']['WS10M'][entry])] = calculate_hourly_wind_energy(wind_data['properties']['parameter']['WS10M'][entry])
            else:
                pass

        # Sort the wind distributions
        wind_speed_distribution = dict(sorted(wind_speed_distribution.items()))
        wind_energy_distribution = dict(sorted(wind_energy_distribution.items()))

        # Plot figure
        fig, (ax1, ax2) = plt.subplots(2)
        wind_speeds = [key + 0.5 for key in wind_speed_distribution]
        hours = [value for key, value in wind_speed_distribution.items()]
        energy = [value for key, value in wind_energy_distribution.items()]
        ax1.bar(wind_speeds, hours)
        ax2.bar(wind_speeds, energy)
        plt.xticks(np.arange(0, max(wind_speeds)+1, 1))
        ax1.set_ylabel('Number of hours')
        ax1.set_xlabel('Wind speed [m/s]')
        ax1.set_title('Distribution curve of wind speed')
        ax2.set_ylabel('Total wind energy [J]')
        ax2.set_xlabel('Wind speed [m/s]')
        ax2.set_title('Distribution curve of wind energy')
        plt.show()

        # Plot wind rose
        ax = WindroseAxes.from_ax()
        ax.bar(wind_direction_list, wind_speed_list, normed=True, opening=0.8, edgecolor='white')
        ax.set_legend()
        ax.set_title('Wind direction distribution')
        plt.show()


        # Calculate the total energy
        total_energy = 0
        for key, value in wind_energy_distribution.items():
            # Only sum up if wind speed > 3 m/s
            if key >= 3:
                total_energy = total_energy + value
        total_energy_elec = total_energy*TURBINE_EFF
        total_energy_elec_kWh = total_energy_elec/KWH
        total_profit = total_energy_elec_kWh*PROFIT_KWH


    MAX_POWER = 5000  # TESUP turbine is rated with a max power of 5 kW
    # Calculate the speed needed to reach the max power
    v_needed_theory = ((((1*MAX_POWER*3600)/(BETZ_LIM))*2)/(RHO*math.pi*(RADIUS**2)*3600))**(1/3)
    v_needed_real = (((1*MAX_POWER*3600)/(TURBINE_EFF)*2)/(RHO*math.pi*(RADIUS**2)*3600))**(1/3)
