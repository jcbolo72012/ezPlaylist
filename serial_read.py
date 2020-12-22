import serial
import re
import matplotlib.pyplot as plot
# "COM3" is the port that your Arduino board is connected.set it to port that your are using        
ser = serial.Serial("COM3", 9600)
print("FOCUS ON ME")

def scan_for(type, threshold, duration): 
    """While loop scans for duration of time, logs
    a particular feature specified by type var
    """
    channels = ['Signal Quality', 'Attention', 'Meditation', 'Delta', 'Theta', 'Low Alpha', 'High Alpha', 'Low Beta', 'High Beta', 'Low Gamma', 'High Gamma']
    record = []
    while True:
        cc=str(ser.readline())
        # print(cc[2:][:-5])   
        split = cc.split(",")
        if (len(split)>type and int(split[type]) < 101):
            if(int(split[type]) >threshold):
                print(split[type] + "% " + channels[type])
            record.append(int(split[type]))
        if (len(record)>duration):
            break
    return record

record = scan_for(2, 80, 120)
plot.plot(record)
plot.ylabel('feature')
plot.show()
# channels[0] = new Channel("Signal Quality", color(0), "");
# channels[1] = new Channel("Attention", color(100), "");
# channels[2] = new Channel("Meditation", color(50), "");
# channels[3] = new Channel("Delta", color(219, 211, 42), "Dreamless Sleep");
# channels[4] = new Channel("Theta", color(245, 80, 71), "Drowsy");
# channels[5] = new Channel("Low Alpha", color(237, 0, 119), "Relaxed");
# channels[6] = new Channel("High Alpha", color(212, 0, 149), "Relaxed");
# channels[7] = new Channel("Low Beta", color(158, 18, 188), "Alert");
# channels[8] = new Channel("High Beta", color(116, 23, 190), "Alert");
# channels[9] = new Channel("Low Gamma", color(39, 25, 159), "Multi-sensory processing");
# channels[10] = new Channel("High Gamma", color(23, 26, 153), "???");