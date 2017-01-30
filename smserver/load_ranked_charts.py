import os
from smserver import models, conf
from smserver.models import ranked_chart
from smserver.models.ranked_chart import Diffs
from sqlalchemy.orm import object_session
import sys, getopt
from optparse import OptionParser

import sys
import datetime

from sqlalchemy.orm import object_session

from smserver.pluginmanager import PluginManager
from smserver.authplugin import AuthPlugin
from smserver.database import DataBase
from smserver.watcher import StepmaniaWatcher
from smserver import conf, logger, models, sdnotify, __version__
from smserver.chathelper import with_color
from smserver.smutils import smthread, smpacket


config = conf.Conf(*sys.argv[3:])

delete = False
update = False
deletechart = ""

if len(sys.argv) > 1:
    print(sys.argv[1])
    if sys.argv[1]  == "-r" or sys.argv[1]  == "--rebuild":
        delete = True
        update = True
    elif sys.argv[1]  == "-u" or sys.argv[1]  == "--update":
        delete = False
        update = True
    elif sys.argv[1]  == "-d" or sys.argv[1]  == "--delete":
        delete = True
        update = False
    elif sys.argv[1]  == "-c" or sys.argv[1]  == "--deletechart":
        delete = False
        update = False
        deletechart = sys.argv[2]
if not update and not delete and deletechart == "":
    print("Commands:")
    print("-r --rebuild")
    print("Delete table and load from cache files")
    print("-u --update")
    print("Load from cache files, update if already loaded")
    print("-d --delete")
    print("Delete table")
    print("-c --deletechart CHARTKEY/HASH")
    print("Delete a chart from table")

directory = os.path.join(os.getcwd(), 'Songs')
if not os.path.exists(directory):
    os.makedirs(directory)

db = DataBase(
    type=config.database.get("type", 'sqlite'),
    database=config.database.get("database"),
    user=config.database.get("user"),
    password=config.database.get("password"),
    host=config.database.get("host"),
    port=config.database.get("port"),
    driver=config.database.get("driver"),
)
db.create_tables()
session = db.session()

if delete:
    print("Deleted " + str(session.query(models.RankedChart).delete()) + " rows.")
    session.commit()
    print("Table deleted.")
if update:
    print("Updating table from cache file. ")
    update_users = []
    chartkey = ""
    radar = [0]
    msds = [0]
    foundsteps = False
    diff = ""
    for filename in os.listdir(directory):
        print("Opening " + filename)
        datafile = open(os.path.join(directory,filename))
        title = ""
        subtitle = ""
        artist = ""
        for line in datafile:
            if '#DIFFICULTY:' in line:
                foundsteps = True
                chartkey = ""
                radar = [0]
                msds = [0]
                line = line[12:]
                line = line[:line.rfind(";")]
                diff = line
            elif '#ARTIST:' in line:
                line = line[8:]
                line = line[:line.rfind(";")]
                artist = line
            elif '#TITLE:' in line:
                line = line[7:]
                line = line[:line.rfind(";")]
                title = line
            elif '#SUBTITLE:' in line:
                line = line[10:]
                line = line[:line.rfind(";")]
                subtitle = line
            if foundsteps == True:
                if '#MSDVALUES:' in line:
                    line = line[11:]
                    line = line[:line.rfind(";")]
                    line = line.split(':')
                    msds = (line[3]).split(',')
                elif '#CHARTKEY:' in line:
                    line = line[10:]
                    line = line[:line.rfind(";")]
                    chartkey = line
                elif '#RADARVALUES:' in line:
                    line = line[13:]
                    line = line[:line.rfind(";")]
                    radar = line.split(',')
                song = models.Song.find_or_create(title, subtitle, artist, session)
                if chartkey and len(radar) > 3 and len(msds) > 1 and diff:
                    newchart = models.RankedChart(chartkey = chartkey, taps = float(radar[6]), jumps = float(radar[7]), hands = float(radar[8]), song_id=song.id)
                    newchart.rating = msds[0]
                    exec("diff = Diffs." + diff + ".value")
                    newchart.diff = diff
                    exists = session.query(models.RankedChart).filter_by(chartkey = chartkey).first()
                    if exists:
                        print("Updating "+ newchart.chartkey)
                        update_users = exists.update(newchart, update_users, session)
                    else:
                        print("Adding "+ newchart.chartkey)
                        session.add(newchart)
                    foundsteps=False
    print("Recalculating user ratings")
    for user in update_users:
        print("Recalculating "+ user.name + "'s rating")
        user.rating = user.updaterating(uer.topssrs(session))
    session.commit()
if deletechart != "":
    exists = session.query(models.RankedChart).filter_by(chartkey = deletechart).first()
    if exists:
        exists.remove(session)
        session.commit()
        print(deletechart + " removed.")
    else:
        print("Could not find " + deletechart)
