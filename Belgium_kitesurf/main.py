import os
import json
import matplotlib.pyplot as plt
import math
from windrose import WindroseAxes
import numpy as np
from copy import deepcopy
import july
from july.utils import date_range
import re

# source of data: https://power.larc.nasa.gov/data-access-viewer/

DATA_FOLDER = "data"
M_S_TO_KNOT = 1.9438452
COAST_SW_LIMIT = 230
COAST_NE_LIMIT = 50
RAIN_INTENSITY = 1
KITE_THS1 = 8
KITE_THS2 = 16
KITE_THS3 = 24
KITE_THS4 = 32

DAYLIGHT = {'01': ['09','10','11','12','13','14','15'],
            '02': ['09','10','11','12','13','14','15'],
            '03': ['08','09','10','11','12','13','14','15','16'],
            '04': ['07','08','09','10','11','12','13','14','15','16','17','18'],
            '05': ['06','07','08','09','10','11','12','13','14','15','16','17','18','19'],
            '06': ['06','07','08','09','10','11','12','13','14','15','16','17','18','19','20'],
            '07': ['06','07','08','09','10','11','12','13','14','15','16','17','18','19','20'],
            '08': ['06','07','08','09','10','11','12','13','14','15','16','17','18','19'],
            '09': ['07','08','09','10','11','12','13','14','15','16','17','18','19'],
            '10': ['08','09','10','11','12','13','14','15','16','17','18'],
            '11': ['08','09','10','11','12','13','14','15','16'],
            '12': ['09','10','11','12','13','14','15']}


# Main script
if __name__ == "__main__":
    files = os.listdir(DATA_FOLDER)
    for file in files:
        with open(f'{DATA_FOLDER}/{file}', 'r') as f:
                data = json.load(f)

        # Init of variables
        kite_hours = {'1': 0, '2': 0, '3': 0,'4': 0}
        kite_days = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0}
        kite_days_intensity = {}
        data_overview = {}
        wind_speed_list = []
        wind_direction_list = []
        wind_speed_distribution = {}

        for entry in data['properties']['parameter']['WS10M']:
            if entry[0:4] == "2022":
                if entry[4:6] in data_overview:
                    pass
                else:
                    data_overview[entry[4:6]] = {}
                if entry[6:8] in data_overview[entry[4:6]]:
                    pass
                else:
                    data_overview[entry[4:6]][entry[6:8]] = {}
                if data['properties']['parameter']['WS10M'][entry] < 0:
                    if entry[:8] not in kite_days_intensity:
                        kite_days_intensity[entry[:8]] = 0
                else:
                    day = True if entry[6:8] in DAYLIGHT[entry[4:6]] else False
                    # Make overview of data
                    data_overview[entry[4:6]][entry[6:8]][entry[8:10]] = {'wind_speed': data['properties']['parameter']['WS10M'][entry],
                                                                           'wind_direction': data['properties']['parameter']['WD10M'][entry],
                                                                          'day': day,
                                                                          'rain': data['properties']['parameter']['PRECTOTCORR'][entry]}

                    # Init for kite days intensity
                    if entry[:8] not in kite_days_intensity:
                        kite_days_intensity[entry[:8]] = 0

                    # Lists for windrose
                    wind_speed_list.append(data['properties']['parameter']['WS10M'][entry])
                    wind_direction_list.append(data['properties']['parameter']['WD10M'][entry])

                    # Wind speeds distribution
                    if int(data['properties']['parameter']['WS10M'][entry]*M_S_TO_KNOT) in wind_speed_distribution:
                        wind_speed_distribution[int(data['properties']['parameter']['WS10M'][entry]*M_S_TO_KNOT)]
                    else:
                        wind_speed_distribution[int(data['properties']['parameter']['WS10M'][entry]*M_S_TO_KNOT)]={'OK':0, 'NOK':0}

                    # Kite wind conditions
                    # NOK when offshore wind or at night or when raining
                    if (data['properties']['parameter']['WD10M'][entry] > COAST_NE_LIMIT and \
                            data['properties']['parameter']['WD10M'][entry] < COAST_SW_LIMIT) or \
                            entry[6:8] not in DAYLIGHT[entry[4:6]] or \
                            data['properties']['parameter']['PRECTOTCORR'][entry] > RAIN_INTENSITY:
                        wind_speed_distribution[int(data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT)]['NOK']+=1
                        wind_prev = -1
                    else:
                        wind_speed_distribution[int(data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT)]['OK'] += 1

                        # Determine the kite intensity zones
                        if (data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT) >= KITE_THS4:
                            kite_hours['4']+=1
                            if wind_prev >= KITE_THS4:
                                kite_days_intensity[entry[:8]] = 4
                            else:
                                pass
                        elif (data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT) >= KITE_THS3:
                            kite_hours['3']+=1
                            if wind_prev >= KITE_THS3:
                                if kite_days_intensity[entry[:8]] < 3:
                                    kite_days_intensity[entry[:8]] = 3
                            else:
                                pass
                        elif (data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT) >= KITE_THS2:
                            kite_hours['2']+=1
                            if wind_prev >= KITE_THS2:
                                if kite_days_intensity[entry[:8]] < 2:
                                    kite_days_intensity[entry[:8]] = 2
                            else:
                                pass
                        elif (data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT) >= KITE_THS1:
                            kite_hours['1']+=1
                            if wind_prev >= KITE_THS1:
                                if kite_days_intensity[entry[:8]] < 1:
                                    kite_days_intensity[entry[:8]] = 1
                            else:
                                pass
                        else:
                            pass
                        wind_prev = deepcopy(data['properties']['parameter']['WS10M'][entry] * M_S_TO_KNOT)
            else:
                pass

        # Post processing
        wind_speed_distribution = dict(sorted(wind_speed_distribution.items()))
        for key, value in kite_days_intensity.items():
            kite_days[str(value)]+=1


        if True:
            wind_speeds = []
            wind_speed_OK = []
            wind_speed_NOK = []
            for i in range(max(wind_speed_distribution)):
                wind_speeds.append(i)
                if i in wind_speed_distribution:
                    wind_speed_OK.append(wind_speed_distribution[i]['OK'])
                    wind_speed_NOK.append(wind_speed_distribution[i]['NOK'])
                else:
                    wind_speed_OK.append(0)
                    wind_speed_NOK.append(0)
            wind_speeds = tuple(wind_speeds)
            kite_wind = {
                "NOK": np.array(wind_speed_NOK),
                "OK": np.array(wind_speed_OK)
            }
            width = 0.5
            fig, ax = plt.subplots()
            bottom = np.zeros(len(wind_speeds))

            for label, kite_wind in kite_wind.items():
                p = ax.bar(wind_speeds, kite_wind, width, label=label, bottom=bottom)
                bottom += kite_wind
            ax.legend(loc="upper right")
            ax.set_title("Distribution curve of wind speed")
            ax.set_xlabel('Wind speed [knot]')
            ax.set_ylabel('Number of hours')
            plt.grid()
            plt.show()


        if True:
            # Plot kiteable hours
            fig, (ax1) = plt.subplots(1)
            wind_speeds = [key + 0.5 for key in wind_speed_distribution]
            hours = [value['OK'] for key, value in wind_speed_distribution.items()]
            ax1.bar(wind_speeds, hours)
            plt.xticks(np.arange(0, max(wind_speeds)+1, 1))
            ax1.set_ylabel('Number of hours')
            ax1.set_xlabel('Wind speed [knot]')
            ax1.set_title('Distribution curve of wind speed')
            plt.show()

        if True:
            dates = date_range("2022-01-01", "2022-12-31")
            data = np.array([value for key, value in kite_days_intensity.items()])
            july.heatmap(dates, data, title='Kitesurf days', cmap="kitesurf", month_grid=True)


        if True:
            # Plot wind rose
            ax = WindroseAxes.from_ax()
            ax.bar(wind_direction_list, wind_speed_list, normed=True, bins=np.arange(0,max(wind_speed_list),5), opening=0.8, edgecolor='white')
            ax.set_legend()
            ax.set_title('Wind direction distribution')
            plt.show()