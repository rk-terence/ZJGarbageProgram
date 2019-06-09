#!/usr/bin/env python3

import numpy as np
import random
from load_data import load_data


class Router:
    def __init__(self):
        self.stops = None
        self.students = None
        self.maxwalk = 450  # If a unit garbage is within 450 meters from another place, then it is possible that it
        # can be allocated to that place to choose potential stops
        self.capacity = 1500
        self.student_near_stops = None
        self.stop_near_stops = None
        self.stop_near_students = None
        self.global_path_list = None
        self.global_students_dict = None
        self.dist_mat, self.garbage_quantities, self.serial_numbers = load_data()  # intermediate variables
        # self.process_file(routes_fn)
        self.generate_students_and_stops()
        self.generate_student_near_stops()
        self.generate_stop_near_stops()
        self.generate_stop_near_students()

    def generate_students_and_stops(self):
        """
        we process keys as if we process the students. It changes self.students and self.stops, they are like -
        self.students: {student_id: place_serial_number
                        ...}
        self.stops: {serial_number: 1
                     ...}
        """
        num_of_places = self.dist_mat.shape[0]
        student_id = 1
        self.students = dict()
        for sn in range(num_of_places):
            for i in range(int(self.garbage_quantities[sn])):
                self.students[student_id] = sn
                student_id += 1

        self.stops = dict()
        for sn in range(num_of_places):
            self.stops[sn] = 1

    def generate_student_near_stops(self):
        """
        Calculate distance between students and stops.
        Assign available stops to student
        out = `( <student_id> : set( <stop_id>, <stop_id>, <stop_id>, ...)
                    <student_id> : set( <stop_id>, <stop_id>, <stop_id>, ...)
                  )
        """
        # For now, every place is only available for one stop - its place.
        num_of_places = self.dist_mat.shape[0]
        self.student_near_stops = dict()
        for key, value in self.students.items():
            self.student_near_stops[key] = set()
            for sn in range(num_of_places):
                if self.dist_mat[self.serial_numbers[value]][self.serial_numbers[sn]] <= 450:
                    self.student_near_stops[key].add(sn)

    def generate_stop_near_stops(self):
        """
        Calculate distance between stop and other stops
        out = dict( <stop_id> : tuple( tuple(<stop_id>, <distance>), tuple(<stop_id>,
        <distance>), ...)
                    <stop_id> : tuple( tuple(<stop_id>, <distance>), tuple(<stop_id>,
                    <distance>), ...)
                  )
        """
        num_of_places = self.dist_mat.shape[0]
        self.stop_near_stops = dict()
        for sn in range(num_of_places):
            this_sn_dict = dict(self.dist_mat[self.serial_numbers[sn]])
            # this_sn_dict.pop(self.serial_numbers[sn])  # delete self
            for snn in range(num_of_places):
                if snn != sn:
                    this_sn_dict[snn] = this_sn_dict.pop(self.serial_numbers[snn])  # Change string to serial number
                else:
                    this_sn_dict.pop(self.serial_numbers[snn])
            self.stop_near_stops[sn] = tuple(sorted(this_sn_dict.items(), key=lambda x : x[1]))

    def generate_stop_near_students(self):
        """
        Calculate distance between students and stops.
        Assign available student to stops
        out = dict( <stop_id> : set( <student_id>, <student_id>, <student_id>, ...)
                    <stop_id> : set( <student_id>, <student_id>, <student_id>, ...)
                  )
        """
        self.stop_near_students = dict()
        num_of_places = self.dist_mat.shape[0]
        for sn in range(num_of_places):
            self.stop_near_students[sn] = set()
        for key, value in self.student_near_stops.items():
            for sn in value:
                self.stop_near_students[sn].add(key)

    def route_local_search(self):
        # find route algorithm
        global_stops = list(self.stops.copy().keys())[1:]  # [1:] - remove base stop 0 which is unnecessary
        base_stop = 0
        global_path_list = []

        # init students list and zero dictionary
        global_students_dict = dict()
        global_students = set(self.students.copy().keys())
        for s in range(1, len(self.students)+1):
            global_students_dict[s] = None

        # stops_debug = [61,37,36] # only first stops, in reverse order
        while len(global_students) != 0:  # empty, also some stops can be unassigned. but students must be picked up
            local_stops = global_stops.copy()
            next_stop = random.choice(local_stops)  # if there's fault with routing, replace this
            # with debug stops list
            # next_stop = stops_debug.pop()
            # current_stop = 0  # base stop, always 0, by definition of file format
            capacity = self.capacity
            local_path_list = list()
            while True:
                if next_stop is None or len(global_students) == 0:
                    if local_path_list not in global_path_list:
                        global_path_list.extend([local_path_list])
                    break
                # if len(global_students)>capacity and local_stops == []:
                # return [None,None] # not feasible solution - conflict: not enough capacity to assign students to stop
                # get our stop and generate list of students connected with only our stop or many stops
                student_single = set()
                student_many = set()
                for student in self.stop_near_students[next_stop]:
                    temp = [x for x in self.student_near_stops[student] if x in global_stops]
                    if student in global_students:
                        if len(temp) == 1:
                            student_single.add(student)
                        elif len(temp) > 1:
                            student_many.add(student)
                        else:
                            raise Exception('Student has no stops!')

                if capacity < len(student_single):  # students with the same stop
                    if not local_stops:
                        if capacity == 1500:
                            return None, None  # if this is a first bus here, it means there isn't a feasible solution
                        global_path_list.extend([local_path_list])
                        # next_stop = None
                        break  # Go to outer loop, use another car
                    local_stops.remove(next_stop)
                    for s in self.stop_near_stops[next_stop]:
                        if s[0] in local_stops:
                            next_stop = s[0]
                            break
                else:  # if the single students' need can be fulfilled -
                    current_stop = next_stop
                    for s in student_single:
                        # take single and assign to stop
                        global_students_dict[s] = current_stop
                        # delete single from available list
                        global_students.remove(s)
                        capacity -= 1

                    for s in student_many:
                        if capacity > 0:
                            # take multiple  and assign to stop
                            global_students_dict[s] = current_stop
                            # delete from available list
                            global_students.remove(s)
                            capacity -= 1
                        else:
                            break  # when capacity is none, stop picking students.

                    local_stops.remove(current_stop)
                    global_stops.remove(current_stop)
                    local_path_list.extend([current_stop])

                    if capacity > 0 and local_stops:
                        for s in self.stop_near_stops[next_stop]:
                            if s[0] in local_stops:
                                next_stop = s[0]
                                break
                        # Truncate - if the distance is higher than that from base_stop to next_stop, abort:
                        if self.dist_mat[self.serial_numbers[current_stop]][self.serial_numbers[next_stop]] > \
                                self.dist_mat[self.serial_numbers[next_stop]][self.serial_numbers[base_stop]]:
                            next_stop = None
                            global_path_list.extend([local_path_list])
                    else:
                        next_stop = None
                        global_path_list.extend([local_path_list])

        self.global_path_list = global_path_list
        self.global_students_dict = global_students_dict
        return [self.global_path_list, self.global_students_dict]

    def get_stops(self):
        return self.stops

    def get_students(self):
        return self.students

    def get_maxwalk(self):
        return self.maxwalk

    def get_capacity(self):
        return self.capacity

    def get_student_near_stops(self):
        return self.student_near_stops

    def get_distance(self):
        dist = 0.0
        for path in self.global_path_list:
            for i in range(len(path)+1):
                if i == 0:
                    dist += np.linalg.norm(np.array(self.stops[0])-np.array(self.stops[path[0]]))
                elif i == len(path):
                    dist += np.linalg.norm(np.array(self.stops[0])-np.array(self.stops[path[i-1]]))
                elif i < len(path):
                    dist += np.linalg.norm(np.array(self.stops[path[i]])-np.array(self.stops[path[i-1]]))
        return dist


def process_file(fn):
    stops = dict()
    students = dict()
    # maxwalk = None
    # capacity = None
    stops_max = None
    students_max = None
    current_stop = 0
    current_student = 1
    with open(fn, 'r') as f:
        for num, line in enumerate(f):
            if num == 0:
                conf = line.split()
                stops_max = int(conf[0])
                students_max = int(conf[2])
                # maxwalk = float(conf[4])
                # capacity = int(conf[7])
            else:
                if len(line) < 2:
                    # empty line
                    continue
                else:
                    s_num, s_x, s_y = [float(v) for v in line.split()]
                    if current_stop < stops_max:
                        current_stop = current_stop + 1
                        stops[int(s_num)] = np.array([s_x, s_y])
                    elif current_student <= students_max:
                        current_student = current_student + 1
                        students[int(s_num)] = np.array([s_x, s_y])

    return stops, students


if __name__ == '__main__':
    print('route.py')
    router = Router()
    router.route_local_search()
