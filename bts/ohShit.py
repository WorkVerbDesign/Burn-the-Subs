import serial
import settings
import time

speed = settings.serialSpeed
serialLoc = settings.serialAddy

reset = settings.pwr_cycle
homies = settings.homing
if __name__ == "__main__":
    print("FUCK FUCK FUCK")
    s = serial.Serial(serialLoc, speed)
    s.write(reset.encode())
    time.sleep(2)
    s.write(homies.encode())
    print("phew")