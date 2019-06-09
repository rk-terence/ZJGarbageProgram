#!python3
# encoding = UTF-8

from router import Router
from generate_my1_images import route_local_search


if __name__ == "__main__":
    print('main.py')
    router = Router()
    min_path_list, min_students_dict, place_allocation_status = route_local_search(1000)
    print("place allocation status:")
    print(place_allocation_status)
    print("min_path_list:")
    print(min_path_list)
