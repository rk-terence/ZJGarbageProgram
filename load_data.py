#!python3
# encoding = UTF-8

# import numpy as np
import pandas as pd

# TODO: adapt the algorithm


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
    serial_numbers = dict(zip(range(1, num_of_places+1), num_of_people_s.keys()))  # The serial number for each place in
    # ZJG campus.
    garbage_quantities = dict(zip(range(1, num_of_places+1), num_of_people_s.values()))  # establish the amount of
    # garbage of each place according to their serial number.

    return dist_mat, garbage_quantities, serial_numbers


if __name__ == "__main__":
    print('load_data.py')
    dist_mat, garbage_quantities, serial_numbers = load_data()
