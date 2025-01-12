from balloon import balloon_scraper, process_data
from filehandling import output_reader
from boom import boom_runner
import numpy as np
import pickle

YEAR = '2018'
MONTH = '06'
DAY = '18'
HOUR = '00'
altitude = 50000
directory = './'
locations = ['72469']  # Corresponds to Fort Worth/Dallas
n_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
all_data = {'temperature': [], 'humidity': [], 'wind': [], 'month': [],
            'day': [], 'noise': [], 'height': []}
log = open('log.txt', 'w')
for month in range(1, len(n_days)+1):
    for day in range(1, n_days[month-1]+1):
        MONTH = '%02.f' % month
        DAY = '%02.f' % day
        try:
            filename = locations[0]+'.csv'
            balloon_scraper(YEAR, MONTH, DAY, HOUR, directory, save=True,
                            locations=locations, filename=filename)

            data = output_reader(filename, header=['latitude', 'longitude',
                                                   'pressure', 'height',
                                                   'temperature', 'dew_point',
                                                   'humidity', 'mixr',
                                                   'wind_direction',
                                                   'wind_speed',
                                                   'THTA', 'THTE', 'THTV'],
                                 separator=',')
            if max(np.array(data['height'])-data['height'][0]) > altitude * 0.3048:
                sBoom_data, height_to_ground = process_data(data, altitude,
                                                            directory='../data/weather/',
                                                            outputs_of_interest=['temperature', 'height',
                                                                                 'humidity', 'wind_speed',
                                                                                 'wind_direction',
                                                                                 'latitude', 'longitude'],
                                                            convert_celcius_to_fahrenheit=True)

                [temperature, wind, humidity] = sBoom_data

                noise = boom_runner(sBoom_data, height_to_ground,
                                    nearfield_file='./25D_M16_RL5.p')

                print(month, day, noise)
                all_data['temperature'].append(temperature)
                all_data['humidity'].append(humidity)
                all_data['wind'].append(wind)
                all_data['height'].append(data['height'])
                all_data['month'].append(month)
                all_data['noise'].append(noise)
                all_data['day'].append(day)
            else:
                print('Not enough data')
                log.write(YEAR + ', ' + MONTH + ', ' + DAY + '\n')
        except(IndexError, ValueError) as e:
            print('Empty data')
            log.write(YEAR + ', ' + MONTH + ', ' + DAY + '\n')

log.close()
f = open(locations[0] + '.p', 'wb')
pickle.dump(all_data, f)
f.close()
