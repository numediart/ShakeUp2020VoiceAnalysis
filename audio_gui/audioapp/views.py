
import librosa as lb
from flask import logging, Flask, render_template, request, make_response, url_for, session, Markup, send_file
from flask import Response
from flask import send_from_directory
from subprocess import run, PIPE
import io, os
import random
import string
from zipfile import ZipFile

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG 
from matplotlib.figure import Figure

from .evaAnalyze import *



app = Flask(__name__)
app.config.from_object('config')

def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route('/visits-counter/')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1  # reading and updating session data
    else:
        session['visits'] = 1 # setting session data
    return "Total visits: {}".format(session.get('visits'))

@app.route('/delete-visits/')
def delete_visits():
    session.pop('visits', None) # delete visits
    return 'Visits deleted'


@app.route('/tmp/audio.wav')
def download():
    print(session['wavName'])
    return send_file( session.get('wavName'))

    
@app.route('/plot.png')
def plot_png():
    wavdata, fs = lb.load(session.get('wavName'))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(wavdata)
    output = io.BytesIO()    
    FigureCanvas(fig).print_png(output)
    #wav.write('./audioapp/tmp/audio.wav', rate, data)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot.svg/')
def plot_svg():
    print('test')
    svg_io = io.StringIO()
    wavdata, fs = lb.load(session.get('wavName'))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(wavdata)
    FigureCanvasSVG(fig).print_svg(svg_io)
    #print(svg_io.getvalue())
    return Response(svg_io.getvalue(), mimetype='image/svg+xml')


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

@app.route('/analyze.html')
def analyze():
    if 'wavName' not in session or not os.path.exists(session.get('wavName')):
        return index()
    
    wavdata, fs = lb.load(session.get('wavName'), sr =None, dtype = np.double)

    fig = Figure( figsize=(10,7.5))
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(wavdata)
        
    mySvgFigures= {}
    [figJitShim,tableJit,tableShim,pitch_av,pitch_var,pitch_beg_end,pitch_huitieme,bri_av]=myNewJitterAndShimmer(wavdata, fs)
    #[figJitShim,tableJit,tableShim]=myJitterAndShimmer(wavdata, fs)
    addSvgFigure(mySvgFigures,'Acoustical wave',fig)
    
    addSvgFigure(mySvgFigures,'Jitter',figJitShim)
    seg_names = ["O", "A", "E", "I", "OU"]

    addSvgFigure(mySvgFigures,'FFT',myFft(wavdata, fs,seg_names))
    addSvgFigure(mySvgFigures,'FFT_1000',myFft_1000(wavdata, fs,seg_names))
    addSvgFigure(mySvgFigures,'Spectrogram',mySpectrogramme(wavdata, fs))
    addSvgFigure(mySvgFigures,'Mel Spectrogram',myMelSpectrogramme(wavdata, fs))
    

    #myStringTables = {}
    #addValueTable(myStringTables,'Jitter',tableJit)
    #addValueTable(myStringTables,'Shimmer',tableShim)
    myValueTables = {}
    myValueTables['key']={'O':'O','A':'A','E':'E','I':'I','OU':'OU'}

    addValueTable(myValueTables,'Jitter',tableJit,5)
    addValueTable(myValueTables,'Shimmer',tableShim,3)
    addValueTable(myValueTables,'pitch_av',pitch_av,0)
    addValueTable(myValueTables,'pitch_var',pitch_var,2)
    addValueTable(myValueTables,'pitch_beg_end',pitch_beg_end,2)
    addValueTable(myValueTables,'pitch_huitieme',pitch_huitieme,2)
    addValueTable(myValueTables,'bri_av',bri_av,1)
    #print(svg_io.getvalue()),plotJitterAndShimmer=Markup(svg_io1.getvalue())
    #return render_template('analyze.html', tableShim = tableShim, tableJit = tableJit, plotData = Markup(svg_io.getvalue()),plotJitterAndShimmer=Markup(svg_io1.getvalue()),plotFft=Markup(svg_io2.getvalue()),
    #    plotSpectrogramme=Markup(svg_io3.getvalue()), plotMelSpectrogramme=Markup(svg_io4.getvalue()))
    return render_template('analyze.html', myValueTables = myValueTables, myStringTables = {},mySvgFigures= mySvgFigures)

 
@app.route('/tmp/archive.zip')
def archive():
    baseName=os.path.basename(session['wavName'])
    print(baseName)
    #baseName=os.path.splitext( base)[0]+'.zip'
    myFileName =os.path.splitext( session['wavName'])[0]
    print(myFileName) 
    with ZipFile(myFileName+'.zip', 'w') as zipObj:
        zipObj.write( session['wavName'],'record.wav')

        wavdata, fs = lb.load(session.get('wavName'), sr =None, dtype = np.double)

        [figJitShim,tableJit,tableShim,pitch_av,pitch_var,pitch_beg_end,pitch_huitieme,bri_av]=myNewJitterAndShimmer(wavdata, fs)
        tempName=myFileName+'jitter.svg'
        figJitShim.savefig(tempName, format = 'svg')
        zipObj.write( tempName,'jitter.svg')
        os.remove(tempName)
        tempName=myFileName+'fft.svg'
        seg_names = ["O", "A", "E", "I", "OU"]
        myFft(wavdata, fs,seg_names).savefig(tempName, format = 'svg')
        zipObj.write( tempName,'fft.svg')
        os.remove(tempName)
        tempName=myFileName+'Spec.svg'
        mySpectrogramme(wavdata, fs).savefig(tempName, format = 'svg')
        zipObj.write( tempName,'Spec.svg')
        os.remove(tempName)
        tempName=myFileName+'MelSpec.svg'
        myMelSpectrogramme(wavdata, fs).savefig(tempName, format = 'svg')
        zipObj.write( tempName,'MelSpec.svg')
        os.remove(tempName)

        zipObj.close()
    tempSender = send_file(myFileName+'.zip')

    return tempSender

@app.route('/analyze2.html')
def analyze2():    
    return render_template('analyze2.html')
    
@app.route('/audio', methods=['POST'])
def audio():
    print('test------------------------------')
    with open(session.get('wavName'), 'wb') as f:
        print(len(request.data))
        f.write(request.data)
    print('test------------------------------')
    proc = run(['ffprobe', '-of', 'default=noprint_wrappers=1', session.get('wavName')], text=True, stderr=PIPE)
    print(proc.stderr)
    return proc.stderr

@app.route('/')
@app.route('/index.html')
def index():

    print(app.config["CLIENT_SOUNDS"])
    if 'wavName' in session and os.path.exists(session.get('wavName')):
        print('wavname is already : ',session.get('wavName'))
    else:
        session['wavName']=app.config["CLIENT_SOUNDS"]+random_generator(10)+'.wav'
        print('new wav name:',session.get('wavName'))
        with open(session.get('wavName'), 'w') as fp: 
            pass
    return render_template('index.html')
