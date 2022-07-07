from machine import Pin
import rp2

# Release candidate 2, 17.Juni 2022

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW,fifo_join=rp2.PIO.JOIN_TX)  # rx- und tx-fifo werden zusammengelegt (8 Worte tief)
# short: 50ms, long: 200ms, pause: 300ms, Wiederholung: 2000ms (über Hauptprogramm)
# 1 sm cycle: 2000Hz = 0.5ms
# Es werden immer mindestens zwei Worte an die pio gesendet:
# Wort 1: Anzahl der Blink-Signale (0 bis n)
# Wort 2: Art des LED Impulses (3: kurz, 50ms, 18: lang, 200ms)

def blink():
    label("get_parms")
    pull(block)
    mov(y,osr)    # im y-Register steht die Anzahl der Blink-Signale (0= keine)
    pull(block)
    mov(x,osr)    # das x-Register unterscheidet zwischen kurzem oder langem Impuls
    jmp(not_y, "get_parms")  # keine Impulse? Dann neues Wertepaar holen
    jmp(y_dec, "do_cycle")  # Korrektur der tatsächlichen Anzahl der Zyklen
    label("do_cycle")
    # Cycles: 1+ 19 + 19 * (19+1) = 400
    set(pins, 1)     # LED einschalten (1 pio Zyklus)
    mov(x,osr) [18]  # Die Schleifenzahl vom fifo holen (1 Zyklus) und 18 Zyklen warten
    label("delay_high")  # Warteschleife, wird x-mal durchlaufen
    nop() [18]           # nichts tun, einfach 1+18 pio Zyklen warten
    jmp(x_dec, "delay_high") # 1. Entscheide: Ist x noch nicht 0? Nochmal in die Warteschleife! 2. Dekrementiere x!
    # Cycles: 1 + 23 + 32 * (17 + 1) = 600
    set(pins, 0)     # LED ausschalten (gleiche Zyklus-Mechanik wie oben)
    set(x, 28) [17]
    label("delay_low")
    nop() [18] 
    jmp(x_dec, "delay_low")
    jmp(y_dec, "do_cycle")   # schicke noch einen LED-Impuls, falls die Anzahl der Impulse noch nicht erreicht ist
    
    
class led_msg:
    def __init__(self,outpin=25):    # pi pico onboard LED: Pin 25 (RP2040 Tiny Grün LED: Pin 19)
        self.short = 3               # vier 10ms Warteschleifen, um 50ms LED-Impuls zu erzeugen
        self.long = 18               # neunzehn 10ms Warteschleifen, um 200ms LED-Impuls zu erzeugen
        self.sm = rp2.StateMachine(0, blink, freq=2000, set_base=Pin(outpin))  # statemachine #0 läuft mit 2kHz
        self.sm.active(1)            # statemachine einschalten

    def msg(self,a,b):           # Funktion, um zwei Wertepaare (Zyklus,Anzahl) an die pio zu schicken
        self.sm.put(a)           # Syntax: msg(Anzahl 200ms Zyklen, Anzahl 50ms Zyklen)
        self.sm.put(self.long)
        self.sm.put(b)
        self.sm.put(self.short)
        
    def done(self):  # Funktion gibt den Status der pio zurück ans Hauptprogramm
        if self.sm.tx_fifo() > 4:  # wenn mehr als vier Instruktionen im pio fifo stehen, ist die pio noch busy
            return(False)
        else:
            return(True)
  

