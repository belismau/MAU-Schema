from icalendar import Calendar, Event
import urllib.request
from flask import Flask, render_template, request, session, url_for, redirect, flash
import datetime
import locale
import time
import pytz
import tzlocal
import html

def changeTime(time):
    local_timezone = tzlocal.get_localzone()
    utc_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_time

app = Flask(__name__)
app.secret_key = "1234abcd"

@app.route("/")
def index():

  veckaList = []
  veckaStart = 0
  saker = []

  try:
    g = urllib.request.urlopen('https://schema.mau.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser=p.TGIAA18h', timeout=8)
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

    moment = html.unescape(moment)
    
    l = kursnamn.find(':')
    k = kursnamn.find(',')

    kursnamn = kursnamn[l+2:k]

    ##########################################################

    location = component.get('location')

    start = str(component.get('dtstart').dt)

    change = start.find("+00:00")

    start = start[:change]

    start = str(changeTime(start))

    remove = start.find(':00+')
    startTime = start[10:remove]
    
    end = str(component.get('dtend').dt)

    change = end.find("+00:00")

    end = end[:change]

    end = str(changeTime(end))

    endTime = end[10:remove]

    datum = start[:10]

    year, month, day = (int(x) for x in datum.split('-'))    
    veckaStop = int(datetime.date(year, month, day).strftime("%V"))

    datumNu = datetime.datetime(year, month, day)

    locale.setlocale(locale.LC_TIME, 'sv_SE.UTF-8')

    dag = datetime.date(year, month, day).strftime("%A")

    dag = bigLetter(dag)

    currentDay = datetime.datetime.now().day
    currentMonth = datetime.datetime.now().month
    currentYear = datetime.datetime.now().year
 
    dateToday = datetime.datetime(currentYear, currentMonth, currentDay)

    if dateToday <= datumNu:

      if veckaStart == veckaStop or veckaStart == 0:
          if veckaStart == 0:
            veckaList.append([True, dag, kursnamn, sign, moment, datum, startTime, endTime, location, veckaStop])
          elif (veckaList[-1][1] == dag and veckaList[-1][5] == datum):
            veckaList.append([False, dag, kursnamn, sign, moment, datum, startTime, endTime, location, veckaStop])
          else:
            veckaList.append([True, dag, kursnamn, sign, moment, datum, startTime, endTime, location, veckaStop])
      else:
        saker.append(veckaList)
        veckaList = []
        veckaList.append([True, dag, kursnamn, sign, moment, datum, startTime, endTime, location, veckaStop])
      
      veckaStart = veckaStop

    ##########################################################
  
  g.close()
  
  return render_template("index.html", schema=saker)

# Krävs för Heroku
def bigLetter(dag):
  first = dag[0].upper()
  second = dag[1:].lower()
  return first + second

if __name__ == '__main__':
    app.run(debug=True)