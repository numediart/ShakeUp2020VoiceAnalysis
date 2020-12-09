# # ShakeUp2020VoiceAnalysis
# ## License
# © - 2020 – UMONS - ISIA Lab - CLICK' Living Lab
# ShakeUp 2020 Voice Analysis of University of MONS – ISIA Lab (Kevin El Haddad) and CLICK' Living Lab (Thierry Ravet) is free software: 
# you can redistribute it and/or modify it under the terms of the GNU General Public License, version 3. 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License, version 3 for more details.
 
# You should have received a copy of the GNU General Public License, version 3 along with this program.  
 
# Each use of this software must be attributed to University of MONS – CLICK' Living Lab and ISIA Lab.
# ## Legal Notices
# This work was produced as part of the FEDER Digistorm project, co-financed by the European Union and the Wallonia Region.
# ![Logo FEDER-FSE](https://www.enmieux.be/sites/default/files/assets/media-files/signatures/vignette_FEDER%2Bwallonie.png)



import librosa as lb
from flask import logging, Flask, render_template, request, make_response, url_for, session, Markup, send_file
from flask import Response
from flask import send_from_directory
from subprocess import run, PIPE
import io, os
import os.path, time 
from os import walk
import random
import string
from zipfile import ZipFile

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG 
from matplotlib.figure import Figure

from audioapp import *



app = Flask(__name__)
app.config.from_object('config')

def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def cleanTmpRepository():
    f =[]
    for root, dirs, files in os.walk(app.config["CLIENT_SOUNDS"]):
        for filename in files:
            f.append(root+filename)
    for filePath in f:
        print(filePath)
        print("time: %s" % time.ctime(time.time()))
        print("last modified: %s" % time.ctime(os.path.getmtime(filePath)))
        if (time.time()-os.path.getmtime(filePath)>app.config["SOUND_MEMORY_DURATION"]):
            os.remove(filePath)
    return



def addSvgFigure(myList, myName,myFig):
    #TODO check if myList is a dict, if myName is a string and myStringTable is a list of Table
    try: 
        svg_io = io.StringIO()
        FigureCanvasSVG(myFig).print_svg(svg_io)
        myList[myName]=Markup(svg_io.getvalue())
    except:
        pass

def addStringTable(myList, myName, myStringTable):
    #TODO check if myList is a dict, if myName is a string and myStringTable is a list of Table
    myList[myName]=myStringTable


def addValueTable(myDictData, myName, myData,numVirg):
    tempData = myData
    for key,value in tempData.items():
        tempData[key]=round(value,numVirg)
    myDictData[myName]=tempData


@app.route('/tmp/audio.wav')
def download():
    print(session['wavName'])
    return send_file( session.get('wavName'))

@app.route('/analyze.html')
def analyze():
#we add a timestamp in the returned parameter for the template to avoid a cache effect when we want download zip and wav file

    print("analyze")
    if 'wavName' not in session or not os.path.exists(session.get('wavName')):
        return index()
    vowels = app.config["USED_VOWELS"]
    analyzer = segmentingAnalyzer(session.get('wavName'),vowels = vowels,useVoiceDetection = app.config["USE_VOICEDETECTION"])

    mySvgFigures= {}
    print("wave")
    addSvgFigure(mySvgFigures,'segmented sound wave',analyzer.segmentedSonogram())
    print("jitter")
    [figJitShim,tableJit,tableShim,pitch_av,pitch_var,pitch_beg_end,pitch_huitieme,bri_av]=analyzer.myJitterAndShimmer()
    addSvgFigure(mySvgFigures,'Jitter',figJitShim)
    
    print("FFT")
    fftFig,fft1000Fig=analyzer.myFft()
    addSvgFigure(mySvgFigures,'FFT',fftFig)
    addSvgFigure(mySvgFigures,'FFT_1000',fft1000Fig)
    print("Spectrogram")
    addSvgFigure(mySvgFigures,'Spectrogram',analyzer.mySpectrogramme())
    addSvgFigure(mySvgFigures,'Mel Spectrogram',analyzer.myMelSpectrogramme())

    myValueTables = {}
    myValueTables['key']={}
    for vowel in vowels:
        myValueTables['key'][vowel]=vowel

    addValueTable(myValueTables,'Jitter',tableJit,5)
    addValueTable(myValueTables,'Shimmer',tableShim,3)
    addValueTable(myValueTables,'Pitch moyen[Hz]',pitch_av,0)
    addValueTable(myValueTables,'Variance du pitch [Hz²]',pitch_var,2)
    addValueTable(myValueTables,'Evolution du pitch [Hz]',pitch_beg_end,2)
    addValueTable(myValueTables,'Pitch relatif au huitieme[Hz]',pitch_huitieme,2)
    addValueTable(myValueTables,'Centroide spectrale [Hz]',bri_av,1)

    return render_template('analyze.html', myValueTables = myValueTables, myStringTables = {},mySvgFigures= mySvgFigures, timestamp = int(time.time()))

 
@app.route('/tmp/archive.zip')
def archive():
    print("********************************************************************************************")
    baseName=os.path.basename(session['wavName'])
    print(baseName)
    #baseName=os.path.splitext( base)[0]+'.zip'
    myFileName =os.path.splitext( session['wavName'])[0]
    print(myFileName+'.zip') 
    if (os.path.isfile(myFileName+'.zip')):
        print("remove previous archive")
        os.remove(myFileName+'.zip')
    with ZipFile(myFileName+'.zip', 'w') as zipObj:
        zipObj.write( session['wavName'],'record.wav')
        
        vowels = app.config["USED_VOWELS"]
        analyzer = segmentingAnalyzer(session.get('wavName'),vowels = vowels,useVoiceDetection = app.config["USE_VOICEDETECTION"])

        [figJitShim,tableJit,tableShim,pitch_av,pitch_var,pitch_beg_end,pitch_huitieme,bri_av]=analyzer.myJitterAndShimmer()
        tempName=myFileName+'jitter.svg'
        figJitShim.savefig(tempName, format = 'svg')
        zipObj.write( tempName,'jitter.svg')
        os.remove(tempName)
        tempName=myFileName+'fft.svg'
        fftFig,fft1000Fig=analyzer.myFft() 
        tempName=myFileName+'fft.svg' 
        fftFig.savefig(tempName, format = 'svg')
        zipObj.write( tempName,'fft.svg')
        os.remove(tempName)
        tempName=myFileName+'fft_1000.svg' 
        fft1000Fig.savefig(tempName, format = 'svg')
        zipObj.write( tempName,'fft_1000.svg')
        os.remove(tempName)
        tempName=myFileName+'Spec.svg'
        analyzer.mySpectrogramme().savefig(tempName, format = 'svg')
        zipObj.write( tempName,'Spec.svg')
        os.remove(tempName)
        tempName=myFileName+'MelSpec.svg'
        analyzer.myMelSpectrogramme().savefig(tempName, format = 'svg')
        zipObj.write( tempName,'MelSpec.svg')
        os.remove(tempName)

        zipObj.close()
    tempSender = send_file(myFileName+'.zip')

    return tempSender

    
@app.route('/audio', methods=['POST'])
def audio():
    print('test------------------------------')
    if (len(request.data)>app.config["SOUND_MAX_SIZE"]):
        print("wav recording is too long",len(request.data))
        return ("too long")
    if (len(request.data)<2000):
        print("wav recording is too short")
        return ("too long")

    with open(session.get('wavName'), 'wb') as f:
        print(len(request.data))
        f.write(request.data)
    proc = run(['ffprobe', '-of', 'default=noprint_wrappers=1', session.get('wavName')], text=True, stderr=PIPE)
    print(proc.stderr)
    if proc.returncode:
        os.remove(session.get('wavName'))
        with open(session.get('wavName'), 'wb') as f:
            f.write(request.data)
        return "The sound data are not valid"
    else:
        return "The sound recording has a valid length"

@app.route('/')
@app.route('/index.html')
def index():
    cleanTmpRepository()
    if 'wavName' in session and os.path.exists(session.get('wavName')):
        print('wavname is already : ',session.get('wavName'))
    else:
        session['wavName']=app.config["CLIENT_SOUNDS"]+random_generator(10)+'.wav'
        print('new wav name:',session.get('wavName'))
        with open(session.get('wavName'), 'w') as fp: 
            pass
    return render_template('index.html')
