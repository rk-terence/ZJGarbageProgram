#!python3
# encoding = UTF-8

# import numpy as np
import pandas as pd


def load_data():
    """
    generate data formats to cater to Router class in router.py
    """

    # Read the distance matrix:
    dist_mat = pd.read_excel('data/distance_matrix.xlsx', index_col=0)
    num_of_places = dist_mat.shape[0]
    for i in range(num_of_places):
        for j in range(i, num_of_places):
            dist_mat.iloc[i, j] = dist_mat.iloc[j, i]

    # Read the number of people for each place:
    num_of_people_s = dict(pd.read_excel('data/num_of_people.xlsx', index_col=0)['平均'])
    serial_numbers = dict(zip(range(num_of_places), num_of_people_s.keys()))  # The serial number for each
    # place in ZJG campus.
    # Move xiaoyiyuan to the first (base place)
    for key, value in serial_numbers.items():
        if value == '校医院':
            serial_numbers[key] = serial_numbers.pop(0)
            serial_numbers[0] = '校医院'
    garbage_quantities = dict()
    for sn in range(num_of_places):
        garbage_quantities[sn] = num_of_people_s[serial_numbers[sn]]
    garbage_quantities[0] = 0  # base stop: 0
    return dist_mat, garbage_quantities, serial_numbers


def load_longitude_and_latitude():
    """
    This function can return the longitude and latitude of each place (not processed with serial numbers)
    :return: locations: {<name of place>: (<longitude>, <latitude>),
                         <name of place>: (<longitude>, <latitude>),
                         ...}
    """
    df = pd.read_excel('data/LongitudeNLatitude.xlsx', skiprows=[0, 1, 2], index_col=0)
    lnls = dict()
    for place_name in df.index:
        lnls[place_name] = (df['经度'][place_name], df['纬度'][place_name])

    return lnls


def load_location():
    """
    :return: locations: {<serial number of a place>: (<x coordinate>, <y coordinate>), ...}
    """
    df = pd.read_csv('data/zjg.txt', header=None, delimiter=' ')
    # df.set_index(range(21))
    # df.set_
    locations = dict()
    for sn in df.index:
        locations[sn] = (df[0][sn], df[1][sn])

    return locations


if __name__ == "__main__":
    print('load_data.py')
    dist_mat, garbage_quantities, serial_numbers = load_data()
    lnls = load_longitude_and_latitude()

    # update locations with serial numbers:
    new_lnls = dict()
    for sn in serial_numbers:
        new_lnls[sn] = lnls[serial_numbers[sn]]

    load_location()
