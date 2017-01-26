import os
import smserver
import smserver.server
from smserver.server import StepmaniaServer
from smserver import models, conf
from smserver.models import ranked_chart
# from smserver.models.ranked_chart import Skillsets
from smserver.models.ranked_chart import Diffs
from sqlalchemy.orm import object_session
import sys, getopt
from optparse import OptionParser

chartkey = ""
radar = [0]
msds = [0]
foundsteps = False
diff = ""

config = conf.Conf(*sys.argv[3:])

rebuild = False
update = True

if len(sys.argv) > 1 and sys.argv[1]  == "-r":
    rebuild = True
    update = False

directory = os.path.join(os.getcwd(), 'Songs')
if not os.path.exists(directory):
    os.makedirs(directory)
session = StepmaniaServer(config).db.session()
if rebuild:
    session.query(models.RankedSong).delete()
for filename in os.listdir(directory):
    datafile = open(os.path.join(directory,filename))
    for line in datafile:
        if '#DIFFICULTY:' in line:
            foundsteps = True
            chartkey = ""
            radar = [0]
            msds = [0]
            line = line[12:]
            line = line[:line.rfind(";")]
            diff = line
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
            if chartkey and len(radar) > 3 and len(msds) > 1 and diff:
                newsong = models.RankedChart(chartkey = chartkey, taps = float(radar[6]))
                #for skillset in Skillsets:
                #    exec("newsong." + skillset.name + " = msds[skillset.value]" )
                newsong.rating = msds[0]
                exec("diff = Diffs." + diff + ".value")
                newsong.diff = diff
                exists = session.query(models.RankedChart).filter_by(chartkey = chartkey).first()
                if exists:
                    exists.diff = newsong.diff
                    exists.taps = newsong.taps
                    exists.rating = newsong.rating
                    # for skillset in Skillsets:
                    #     exec("exists." + skillset.name + " = newsong." + skillset.name )
                else:
                    session.add(newsong)
                foundsteps=False
session.commit()