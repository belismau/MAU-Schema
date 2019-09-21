from icalendar import Calendar, Event
import urllib.request
from flask import Flask, render_template, request, session, url_for, redirect, flash
import datetime
import locale
import time
import pytz
import tzlocal

veckaList = []
veckaStart = 0
saker = []

def changeTime(time):
    local_timezone = tzlocal.get_localzone()
    utc_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_time

try:
    g = urllib.request.urlopen('https://schema.mau.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser=p.TGIAA18h', timeout=4)
    cal = Calendar.from_ical(g.read())
except:
    g = open('schema.ics','rb')
    cal = Calendar.from_ical(g.read())

for component in cal.walk("vevent"):

    summary = component.get('summary')

    sign = summary.find('Sign: ')
    moment = summary.find('Moment: ')
    program = summary.find('Program: ')
    kursnamn = summary.find('Kurs.grp: ')

    kursnamn = summary[kursnamn+10:sign]
    sign = summary[sign+6:moment]
    moment = summary[moment+8:program]

    l = kursnamn.find(':')
    k = kursnamn.find(',')

    kursnamn = kursnamn[l+2:k]

    ##########################################################

    location = component.get('location')

    start = str(component.get('dtstart').dt)

    change = start.find("+00:00")

    start = start[:change]

    start = changeTime(start)

    print(start)

##########################################################

g.close()