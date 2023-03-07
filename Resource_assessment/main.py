import os
import json
import matplotlib.pyplot as plt
import re

DATA_FOLDER = "data"

# info: https://towardsdatascience.com/wind-energy-physics-and-resource-assessment-with-python-789a0273e697
# info: https://power.larc.nasa.gov/data-access-viewer/

if __name__ == "__main__":
    data = os.listdir(DATA_FOLDER)
    for file in data:
        with open(f'{DATA_FOLDER}/{file}', 'r') as f:
                wind_data = json.load(f)
        wind_data_overview = {}
        for entry in wind_data['properties']['parameter']['WS10M']:
            if entry[0:4] == "2021":
                if entry[4:6] in wind_data_overview:
                    pass
                else:
                    wind_data_overview[entry[4:6]] = {}
                if entry[6:8] in wind_data_overview[entry[4:6]]:
                    pass
                else:
                    wind_data_overview[entry[4:6]][entry[6:8]] = {'list': []}
                wind_data_overview[entry[4:6]][entry[6:8]]['list'].append(wind_data['properties']['parameter']['WS10M'][entry])
            else:
                pass

        # Post processing
        for month in wind_data_overview:
            for day in wind_data_overview[month]:
                wind_data_overview[month][day]['avg'] = sum(wind_data_overview[month][day]['list'])/\
                                                        len(wind_data_overview[month][day]['list'])

        # Make graph overview per month
        for month in wind_data_overview:
            data_to_plot = []
            for day in wind_data_overview[month]:
                data_to_plot.append(wind_data_overview[month][day]['avg'])
            plt.figure()
            plt.plot(data_to_plot)
            plt.ylabel('Windspeed [m/s]')
            plt.title(f'Average wind speed in {month}')
        plt.show()


