import os
import smserver
import smserver.server
from smserver.server import StepmaniaServer
from smserver import models, conf
from smserver.models import ranked_song
from smserver.models.ranked_song import Skillsets
from smserver.models.ranked_song import Diffs
from sqlalchemy.orm import object_session
import sys

chartkey = ""
radar = [0]
msds = [0]
foundsteps = False
diff = ""

config = conf.Conf(*sys.argv[1:])



directory = os.path.join(os.getcwd(), 'Songs')
if not os.path.exists(directory):
    os.makedirs(directory)
session = StepmaniaServer(config).db.session()
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
                newsong = models.RankedSong(chartkey = chartkey, taps = radar[5])
                for skillset in Skillsets:
                    exec("newsong." + skillset.name + " = msds[skillset.value]" )
                exec("diff = Diffs." + diff + ".value")
                newsong.diff = diff
                session.add(newsong)
                foundsteps=False
session.commit()
            