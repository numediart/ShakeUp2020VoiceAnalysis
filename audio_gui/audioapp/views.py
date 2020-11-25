
import librosa as lb
from flask import logging, Flask, render_template, request, make_response, url_for, session, Markup, send_file
from subprocess import run, PIPE
import io, os
import random
import string

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG 
from matplotlib.figure import Figure
from flask import Response
import scipy.io.wavfile as wav
from flask import send_from_directory

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
    (rate, data) = wav.read(session.get('wavName'))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(data)
    output = io.BytesIO()    
    FigureCanvas(fig).print_png(output)
    #wav.write('./audioapp/tmp/audio.wav', rate, data)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot.svg/')
def plot_svg():
    print('test')
    svg_io = io.StringIO()
    (rate, data) = wav.read(session.get('wavName'))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(data)
    FigureCanvasSVG(fig).print_svg(svg_io)
    #print(svg_io.getvalue())
    return Response(svg_io.getvalue(), mimetype='image/svg+xml')


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

def addSvgFigure(myList, myName,myFig):
    #TODO check if myList is a dict, if myName is a string and myStringTable is a list of Table
    svg_io = io.StringIO()
    FigureCanvasSVG(myFig).print_svg(svg_io)
    myList[myName]=Markup(svg_io.getvalue())

def addStringTable(myList, myName,myStringTable):
    #TODO check if myList is a dict, if myName is a string and myStringTable is a list of Table
    myList[myName]=myStringTable



@app.route('/analyze.html')
def analyze():
    if 'wavName' not in session or not os.path.exists(session.get('wavName')):
        return index()
    (rate, data) = wav.read(session.get('wavName'))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(data)


    wavdata, fs = lb.load(session.get('wavName'))
    output = io.BytesIO()    
    
    [figJitShim,tableJit,tableShim]=myJitterAndShimmer(wavdata, fs)
    mySvgFigures= {}
    addSvgFigure(mySvgFigures,'Acoustical wave',fig)
    addSvgFigure(mySvgFigures,'Jitter',figJitShim)
    addSvgFigure(mySvgFigures,'FFT',myFft(wavdata, fs))
    addSvgFigure(mySvgFigures,'Spectrogram',mySpectrogramme(wavdata, fs))
    addSvgFigure(mySvgFigures,'Mel Spectrogram',myMelSpectrogramme(wavdata, fs))

    myStringTables = {}
    addStringTable(myStringTables,'Jitter',tableJit)
    addStringTable(myStringTables,'Shimmer',tableShim)

    #print(svg_io.getvalue()),plotJitterAndShimmer=Markup(svg_io1.getvalue())
    #return render_template('analyze.html', tableShim = tableShim, tableJit = tableJit, plotData = Markup(svg_io.getvalue()),plotJitterAndShimmer=Markup(svg_io1.getvalue()),plotFft=Markup(svg_io2.getvalue()),
    #    plotSpectrogramme=Markup(svg_io3.getvalue()), plotMelSpectrogramme=Markup(svg_io4.getvalue()))
    return render_template('analyze.html', myStringTables = myStringTables, mySvgFigures= mySvgFigures)

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
