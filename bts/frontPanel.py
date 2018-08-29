# hopefully I can import this mamma jamma
# into my other python code
# and run this sucka
# without any fuss
#
# RPi Pinout:
#
#                3.3v 01|02 5v
#              GPIO02 03|04 5v
#              GPIO03 05|06 Gnd
#              GPIO04 07|08 GPIO14 
#     Ground -    Gnd 09|10 GPIO15
#      Btn_R - GPIO17 11|12 GPIO18
#      Btn_B - GPIO27 13|14 Gnd
#      LRed -  GPIO22 15|16 GPIO23 - RRed
#                3.3v 17|18 GPIO24 - LGreen
#     RGreen - GPIO10 19|20 Gnd
#       Blue - GPIO09 21|22 GPIO25 - TYel 
#       BYel - GPIO11 23|24 GPIO08
#                 Gnd 25|26 GPIO07 
#               ID_SD 27|28 ID_SC
#              GPIO05 29|30 Gnd
#              GPIO06 31|32 GPIO12 
#              GPIO13 33|34 Gnd
#              GPIO19 35|36 GPIO16 - Green
#        Red - GPIO26 37|38 GPIO20
#                 GND 39|40 GPIO21 

from gpiozero import LED, Button

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