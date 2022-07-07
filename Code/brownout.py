# brownout module
# release candidate 2, 17.Juni 2022

import os
from machine import Pin,ADC
from time import time,localtime
from micropython import schedule


class brownout():
    
    
    def __init__(self):
        self.err_map = ('normal','no_time','low_bat','init')
        self.log_variables = 'sys status,usb power,year,month,day,hour,minute,second,bat voltage' 
        self.no_dst = 1   # keine Sommerzeit: 1 Stunde Korrektur für MEZ
        self.dst = 0      # Sommerzeit: 0 Stunden Korrektur für MESZ
        self.t_adj = self.dst  # die richtige Zeitjustierung, abhängig von Sommerzeit
        self.power_loss_events = 0  # die Stromausfall-zähl-Variable
        self.sys_start = True       # Betriebszustands-Variablen
        self.power_loss = False
        self.record = ''       # Zwischenspeicher für das Protokoll vom Beginn eines Stromausfalls
        self.USBpower = Pin(24, Pin.IN, Pin.PULL_DOWN) # GPIO24 überwacht die USB Versorgung (GPIO16 für Test)
        self.adc = ADC(29)    # GPIO19 überwacht die Batteriespannung der beiden AA-Zellen
        self.cf = 3.3*3/65535  # Vref(adc)=3.3V, Vadc wird über 1:3 Spannungsteiler abgegriffen, 16 bit full scale
        os.chdir("/")               # Das log file wird in der root directory vom Pico gespeichert
        self.logvars(self.log_variables)    # Die Variablennamen werden als Header in die Flash Datei geschrieben
        self.USBpower.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.isr_bo_event) # Der Interrupt wird scharf geschaltet
            
            
    def check_status(self):
        if localtime()[0] < 2022:  # keine gültige Zeitangabe in der RTC?
            self.err_status = 2
        if self.power_loss and self.readVdd() < 2.0: # niedrige Batteriespannung bei Stromausfall?
            self.err_status = 3
        if self.sys_start:          # Nach Systemstart ist der Stromausfallmonitor im Initialisierungsmode
            self.err_status = 4
        return (self.err_status)
    
    def logvars(self,varstr1,varstr2=''):      # Funktion zum Beschreiben des Pi Pico Flash im Text-(String-)Format
        self.file = open("powerlog.txt", "a")  # Die Funktion wird nur nach Ende eines Stromausfalls aufgerufen,
        self.file.write(varstr1+"\n")          # um einen Interrupt während des Flash-Zugriffs zu vermeiden
        if varstr2 != '':
            self.file.write(varstr2+"\n")
        self.file.close()
        
    def readVdd(self):           # Funktion zum Messen der Batteriespannung (Spannungsteiler 1:3!)
        return(self.adc.read_u16()*self.cf)
    
            
    def isr_bo_event(self,b):    # Interrupt Service Routine (ISR), kurz und knackig, für den GPIO Interrupt
        schedule(self.bo_scheduled,1)  # Der Flash update wird über den MicroPython Scheduler gemacht!
        
    def bo_scheduled(self,a):    # Der Scheduler speichert GPIO Logikpegel und Zeit in einen String
        self.bo_event = self.USBpower.value()
        self.eventstr = self.err_map[self.err_status-1]+','+str(self.bo_event)+','+self.localtime2str()+str('%.02f' %(self.readVdd()))
        if self.bo_event == 0:    # Stromausfall erkannt!
            self.power_loss_events += 1
            self.record = self.eventstr
            if self.sys_start:    # Wurde der Pico gerade vom PC getrennt?
                self.power_loss_events -= 1  # Dann war es kein echter Stromausfall
                self.sys_start = False  # Der Monitor ist nun nicht mehr im Initialisierungsmodus
                self.err_status = 1 
            self.power_loss = True
        else:                     # Der Stromausfall ist vorbei!
            self.power_loss = False
            self.logvars(self.record,self.eventstr) # Beide Protokoll-Strings werden in den Flash geschrieben
        
    def localtime2str(self):   # Funktion erzeugt einen Jahr/Monat/Tag/Stunden/Minuten/Sekunden String
        self.timestr = ''
        for i in range(6):
            if i == 3:
                self.timestr += str(localtime()[i]+self.t_adj)+',' # MEZ und ggf Sommerzeit korrigieren
            else:
                self.timestr += str(localtime()[i])+','
        return (self.timestr)
        
    def in_power_loss(self):   # Funktion zum Abfragen des Stromausfall-Status
        return (self.power_loss)       # Boolscher Wert als Rückgabe für Stromausfall / kein Stromausfall
