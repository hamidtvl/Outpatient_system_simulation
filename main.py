#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 15:53:13 2021

@author: hamid
"""

# objective : Avg wating time in queue-avg system time-optimum number of servers-number of reneged -server ulitization rate
import numpy as np
import pandas as pd
import random
import csv
import simpy

# open 3 files for normal patients results,emergency patients results,reneged patients results
with open('normal_patient.csv', 'w') as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow(['Normal Patient Waiting Time', 'Normal Patient Server Time', 'Normal patientt service time'])
with open('emergency_patient.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(
        ['Emergency patient waiting time', 'Emergency patient Server Time', 'Emergency Patient Service Time'])
with open('reneged_patient.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['reneged patient id', 'reneged patient time'])


# generate arrival time of normal customers(patients)
def Normal_patients_arrival():
    return random.expovariate(1 / 5)


# generate arrival time of emergency patients
def Emergency_patients_arrival():
    return random.expovariate(1 / 15)


# generate service time of normal servers(nurses) and makes sure no negetive service time go through
def Normal_server_rate():
    a = random.normalvariate(12, 4)
    while a < 0:
        a = random.normalvariate(12, 4)
    return a


# generate service time of emergency servers(nurses) and makes sure no negetive service time go through
def Emergency_server_rate():
    a = random.normalvariate(9, 5)
    while a < 0:
        a = random.normalvariate(9, 5)
    return a


# this generator is used to generate new normal patients arrival
def normal_patient(env, resource):
    patient_id = 0
    # it will generate patients as long as the simulation is running
    while True:
        # Here, the patient go through their process(waiting in line, get served and etc.)
        patient_act = normal_patient_activity(env, normal_nurse, patient_id)

        env.process(patient_act)
        # generates new arrival of the next patient
        patient_arr = Normal_patients_arrival()
        # freezes time till next patients arrival
        yield env.timeout(patient_arr)

        patient_id += 1
        p.append(patient_id)


# this generator defines the path and actions that each normal patient take.
def normal_patient_activity(env, resource, patient_id):
    # patient eneters the the system
    patient_enter_system = env.now
    print(f'patient {patient_id} entered the system at : {patient_enter_system}')

    # request a nurse
    with normal_nurse.request() as req:
        # generates each normal patient's renege time
        patience = random.uniform(8, 40)
        # freezes time till server(s) get(s) free or patient reneges
        results = yield req | env.timeout(patience)

        # checks wether patients reneged or got served and then take the action accordingly
        if req in results:
            # here , patient made it to a server.
            patient_entered_nurse_section = env.now
            # calculating the waiting time
            waiting_time = patient_entered_nurse_section - patient_enter_system

            normal_wating_time[patient_id] = waiting_time

            print(
                f'patient {patient_id} left Queue for nurse at : {patient_entered_nurse_section} and the had waited in the Queue for : {waiting_time} minutes')

            service_time = Normal_server_rate()

            normal_patient_service_time[patient_id] = service_time

            yield env.timeout(service_time)

            patient_leaving = env.now

            total_system_time = patient_leaving - patient_enter_system

            normal_avg_server_time[patient_id] = total_system_time

            print(f'Patient {patient_id} is served and now leaves the system at:{patient_leaving}')
            print(f'total system time for patient {patient_id} is : {total_system_time}')
        else:
            # patient has reneged and the renege time and etc. get calculated below
            normal_patient_service_time[patient_id] = 'Reneged'
            normal_avg_server_time[patient_id] = 'Reneged'
            normal_wating_time[patient_id] = 'Reneged'
            normal_patient_reneged_now = env.now
            reneged_time = normal_patient_reneged_now - patient_enter_system
            reneged_patient_time.append(reneged_time)
            reneged_patient_id.append(patient_id)
            reneged_waiting_time = normal_patient_reneged_now - patient_enter_system
            print(
                f'patient {patient_id} has reneged after waiting {reneged_waiting_time} time and leaving now at {normal_patient_reneged_now}')


# this generator is used to generate new emergency patients arrival
def emergency_patient(env, resource):
    E_patient_id = 0
    # generates new emergency patients as long as simulation is running
    while True:
        # just like normal patients arrival generation, only difference is that in  this case emeregnecy patients wont start comming at T=0,according to intial conditions the first patient comes at time T=exponenatial(1/15)
        E_patient_arr = Emergency_patients_arrival()

        yield env.timeout(E_patient_arr)

        E_patient_act = emergency_patient_activity(env, emergency_nurse, E_patient_id)

        env.process(E_patient_act)

        E_patient_id += 1
        E.append(E_patient_id)


# this generator defines the path and actions that each  emergency patient takes.
def emergency_patient_activity(env, resource, E_patient_id):
    # patient eneters the the system
    E_patient_enter_system = env.now
    print(f'emergency patient {E_patient_id} entered the system at : {E_patient_enter_system}')

    # request a nurse
    with emergency_nurse.request() as req1:
        # freezes time till server is free
        yield req1

        # calculating the waiting time
        E_patient_entered_nurse_section = env.now

        E_waiting_time = E_patient_entered_nurse_section - E_patient_enter_system

        emergency_waiting_time[E_patient_id] = E_waiting_time

        print(
            f'emergency patient {E_patient_id} left Queue for nurse at : {E_patient_entered_nurse_section} and the had waited in the Queue for : {E_waiting_time} minutes')

        E_service_time = Emergency_server_rate()

        emergency_patient_service_time[E_patient_id] = E_service_time
        # freezes time till patient get served
        yield env.timeout(E_service_time)

        E_patient_leaving = env.now

        E_total_system_time = E_patient_leaving - E_patient_enter_system

        emergency_avg_server_time[E_patient_id] = E_total_system_time

        print(f'emergency Patient {E_patient_id} is served and now leaves the system at:{E_patient_leaving}')
        print(f'total system time for emergency patient {E_patient_id} is : {E_total_system_time}')

    # we run the simulation for 60 days and each day is 420 working minutes, each day everything get reset.


for i in range(30):
    # on average, each day we receive 80 patients, I just pre-allocated 150 slots to cover all customers per day(when printing results to CSV file, it will cut and remove the execcive arrays in each list)
    normal_wating_time = [0] * 150
    emergency_waiting_time = [0] * 150
    reneged_patient_time = []
    reneged_patient_id = []
    normal_avg_server_time = [0] * 150
    emergency_avg_server_time = [0] * 150
    # list P is used to get record of number of normal patients per dey so i can cut execcive arrays in each list
    p = []
    # list E is used to get record of number of emeregency patients per dey so i can cut execcive arrays in each list
    E = []
    normal_patient_service_time = [0] * 150
    emergency_patient_service_time = [0] * 150
    env = simpy.Environment()
    normal_nurse = simpy.Resource(env, capacity=1)
    emergency_nurse = simpy.Resource(env, capacity=1)
    env.process(normal_patient(env, normal_nurse))
    env.process(emergency_patient(env, emergency_nurse))
    env.run(until=420)
    # each day,results are appened to CVS files created in the beginning
    with open('normal_patient.csv', 'a') as f:
        for i in range(len(p) - 3):
            writer = csv.writer(f, delimiter=',')
            writer.writerow([normal_wating_time[i], normal_avg_server_time[i], normal_patient_service_time[i]])
        writer.writerow(['Next Day', 'Next Day'])
    with open('emergency_patient.csv', 'a') as f:
        for i in range(len(E)):
            writer2 = csv.writer(f, delimiter=',')
            writer2.writerow(
                [emergency_waiting_time[i], emergency_avg_server_time[i], emergency_patient_service_time[i]])
        writer2.writerow(['Next Day', 'Next Day'])
    with open('reneged_patient.csv', 'a') as f:
        writer3 = csv.writer(f, delimiter=',')
        for i in range(len(reneged_patient_id)):
            writer3.writerow([reneged_patient_id[i], reneged_patient_time[i]])
        writer3.writerow(['Next Day', 'Next Day'])

# this part will only yield the day 60 result and is just used to see if everything is working!!!(I commented them to avoid confusion)
# import statistics as sta
# print(f'avg waiting time for normal patients is : {sta.mean(normal_wating_time)} ')
# print(f'avh waiting time for emergency patients is : {sta.mean(emergency_waiting_time)}')
# print(F'number of reneged costumers: {len(reneged_patient_id)}')
# print(f'avg waiting time befor renege : {sta.mean(reneged_patient_time)}')
# print(f'avg system time for normal patients : {sta.mean(normal_avg_server_time)}')
# print(f'avg system time for emergency patients : {sta.mean(emergency_avg_server_time)}')
# print(f'avg server utilization rate is :{sum(normal_patient_service_time)/840}')



