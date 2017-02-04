import os
from smserver import models, conf
from smserver.models import ranked_chart
from smserver.models.ranked_chart import Diffs
from smserver.models.pack import Pack
from sqlalchemy.orm import object_session
import sys, getopt
from optparse import OptionParser

import sys
import datetime
import codecs

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

directory = os.path.join(os.getcwd(), u'Songs')
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
    print("Deleted " + str(session.query(models.RankedChart).delete()) + " rows")
    session.commit()
    print("Table deleted")
if update:
    print("Updating table from cache files ")
    update_users = []
    for filename in os.listdir(directory):
        try:
            #print("Opening " + filename)
            datafile = codecs.open(os.path.join(directory,filename), mode='r', encoding="utf-8")
            title = ""
            subtitle = ""
            artist = ""
            pack_name = ""
            pack = None
            song = None
            foundsteps=False
            foundsub=False
            foundtit=False
            foundart=False
            chartkey = ""
            radar = [0]
            msds = [0]
            foundsteps = False
            diff = ""
            try:
                for line in datafile:
                    if foundsteps == True and song and pack_name:
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
                        if chartkey and pack and len(radar) > 3 and len(msds) > 1 and diff:
                            newchart = models.RankedChart(chartkey = chartkey, taps = float(radar[6]), jumps = float(radar[7]), hands = float(radar[8]), song_id=song.id, pack_id=pack.id)
                            newchart.rating = msds[0]
                            diffnum = Diffs[diff].value
                            newchart.diff = diffnum
                            exists = session.query(models.RankedChart).filter_by(chartkey = chartkey).first()
                            if exists:
                                #print("Updating "+" Hash: "+newchart.chartkey+" Title: "+song.title+" Pack: "+pack_name+" Diff: "+diff)
                                update_users = exists.update(newchart, update_users, session)
                            else:
                                #print("Updating "+" Hash: "+newchart.chartkey+" Title: "+song.title+" Pack: "+pack_name+" Diff: "+diff)
                                session.add(newchart)
                            foundsteps = False
                    elif '#DIFFICULTY:' in line:
                        foundsteps = True
                        chartkey = ""
                        radar = [0]
                        msds = [0]
                        line = line[12:]
                        line = line[:line.rfind(";")]
                        diff = line
                    elif '#ARTIST:' in line:
                        foundart = True
                        line = line[8:]
                        line = line[:line.rfind(";")]
                        artist = line
                    elif '#TITLE:' in line:
                        foundtit = True
                        line = line[7:]
                        line = line[:line.rfind(";")]
                        title = line
                    elif '#SUBTITLE:' in line:
                        foundsub = True
                        line = line[10:]
                        line = line[:line.rfind(";")]
                        subtitle = line
                    elif '#SONGFILENAME:' in line:
                        line = line[14:]
                        line = line[:line.rfind(";")]
                        line = line.split('/')
                        pack_name = line[-3]
                        pack = models.Pack.find_or_create(pack_name, session)
                    if foundsub and foundtit and foundart:
                        song = models.Song.find_or_create(title, subtitle, artist, session)
            except UnicodeDecodeError:
                print("Error in file "+ filename)
                continue
        except UnicodeEncodeError:
            print("Error in filename ")
            continue
    print("Recalculating user ratings")
    for user in update_users:
        #print("Recalculating "+ user.name + "'s rating")
        user.rating = user.updaterating(uer.topssrs(session))
    session.commit()
if deletechart != "":
    exists = session.query(models.RankedChart).filter_by(chartkey = deletechart).first()
    if exists:
        exists.remove(session)
        session.commit()
        #print(deletechart + " removed.")
    else:
        print("Could not find " + deletechart)
print("There are " + str(session.query(models.RankedChart).count()) + " ranked charts")
