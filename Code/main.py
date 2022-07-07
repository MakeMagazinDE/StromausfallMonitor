# Release candidate 2, 17.Juni 2022

import brownout
import pio_led_msg
from machine import lightsleep,freq
from time import sleep

sleep(1)          # warte 1 Sekunde mit dem Programmstart, nur fuer den Fall, dass der Thonny Stop-Knopf nicht funktioniert
freq(50000000)                    # der System-Clock wird auf 50MHz reduziert, um Strom bei Batteriebetrieb zu sparen
mydis = pio_led_msg.led_msg()         #erzeugt das display Objekt zur Statusanzeige über die Pi Pico LED
mybrownout = brownout.brownout()  #erzeugt das brownout Objekt zum Erkennen und Verarbeiten der Stromausfälle

while True:
    status = mybrownout.check_status()  #holt den momentanen Status vom Stromausfall-Monitor (init/normal/no time/low bat)
    if mydis.done():    # Zeige den neuen Status ueber Pi Pico LED an, falls der pio-Puffer leer ist
        if mybrownout.in_power_loss(): # Stromausfall erkannt?
            mydis.msg(0,status)      # ändere Statusanzeige in kurze Lichtblitze
        else:                        # Kein Stromausfall:
            mydis.msg(status,mybrownout.power_loss_events)  # Statusanzeige über lange LED-Impulse, gefolgt von der Anzahl der bisherigen Stromausfälle per kurzen Lichtblitz
    lightsleep((500 + mybrownout.power_loss_events *350)+2000)    # legt die CPU schlafen, RTC läuft weiter (spart aber leider kein Strom)
