# Explore the default dataset
class data_parser(object):
    def __init__(self):
        self.baseData = open("datasets/result.txt",'r')
    def open(self):
        for l in self.baseData:
                l = l.split(',')
                x,y,th = [float(i) for i in l[:3]]
                readings = [int(float(i)) for i in l[3:]]
                # print(x,y,th)
                # print(len(readings))
def process(data):
    if data > 1000:
        data = 0.0
    return data

f = open("datasets/five_sensors_9.txt","r")
print ("File: ",f.name)

data_buff = []

data = []

for line in f:
    data_buff.append(line.split())

p_flag = 0
r_flag = 0
t_flag = 0

for sensor_read in data_buff:

    if sensor_read[0] == '\x1bKPosition:':
        x = float(sensor_read[1])
        y = float(sensor_read[3])
        p_flag = 1

    if sensor_read[0] == '\x1b[KRanging:':
        ranges = []
        for i in range(1,6):
            raw = float(sensor_read[i].rstrip(','))
            ranges.append(process(raw))
        r_flag = 1

    if sensor_read[0] == '\x1b[KOrientation':
        th = float(sensor_read[6].rstrip(')'))
        t_flag = 1

    if p_flag and r_flag and t_flag:

        data.append([x,y,th]+ranges)

        p_flag = 0
        r_flag = 0
        t_flag = 0

print (data[0])

import csv

with open("datasets/result.txt", "wb") as result:
    writer = csv.writer(result, delimiter=',')
    writer.writerows(data)

d = data_parser()
d.open()
