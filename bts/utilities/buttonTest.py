# gpioZero button test
# this is just to make sure the LEDs and buttons
# attached to Burn the Subs actually work. 
# so yeah, that.

from gpiozero import Button, LED
from time import sleep

Btn_Red = Button(17)
Btn_Blk = Button(27)
LED_BB_Red = LED(23)
LED_BB_Grn = LED(10)
LED_RB_Red = LED(22)
LED_RB_Grn = LED(24)

LED_Blue = LED(9)
LED_TYel = LED(25)
LED_BYel = LED(11)
LED_Grn = LED(16)
LED_Red = LED(26)

def allOn():
    print("ass")
    LED_BB_Red.on()
    LED_BB_Grn.on()
    LED_RB_Red.on()
    LED_RB_Grn.on()

    LED_Blue.on()
    LED_TYel.on()
    LED_BYel.on()
    LED_Grn.on()
    LED_Red.on()
    
def allOff():
    print("hole")
    LED_BB_Red.off()
    LED_BB_Grn.off()
    LED_RB_Red.off()
    LED_RB_Grn.off()

    LED_Blue.off()
    LED_TYel.off()
    LED_BYel.off()
    LED_Grn.off()
    LED_Red.off()

Btn_Red.when_released = allOn
Btn_Red.when_pressed = allOn
Btn_Blk.when_released = allOff

if __name__ == "__main__":
    while True:
        sleep(20)