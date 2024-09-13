import socket
from psychopy import visual, core
from psychopy.hardware import keyboard
from pylsl import StreamInfo, StreamOutlet
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 6667))
sock.setblocking(0)
sock.settimeout(0.002)


## LSL
flux_info = StreamInfo(name='flux_stream', type='Markers', channel_count=1, channel_format='int8', source_id='flux_stream_001')
flux_outlet = StreamOutlet(flux_info)

win = visual.Window(size=(800, 800), monitor='testMonitor', units='cm')  # Change to your monitor name
kb = keyboard.Keyboard()


def drawScore(score):
    score = visual.TextStim(
        win=win, name='score',
        text='score : '+ str(score),
        font='Open Sans',
        pos=(0, 8), height=1, wrapWidth=None, ori=0.0,
        color='black', colorSpace='rgb', opacity=None,
        languageStyle='LTR',
        depth=-1.0)
    score.draw()


def draw_card(value, stack):
    print("card", value, stack)
    if stack == 1:
        stack = "A"
    elif stack == 2:
        stack = "B"
    elif stack == 3:
        stack = "C"
    elif stack == 4:
        stack = "D"

    # Modify following code to change card appearance
    background = visual.Rect(
        win=win, name='background', units='cm',
        width=(5.9, 9.1)[0], height=(5.9, 9.1)[1],
        ori=0.0, pos=(0, 0),
        lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)
    number = visual.TextStim(
        win=win, name='number',
        text=value,
        font='Open Sans',
        pos=(0, 0), height=1, wrapWidth=None, ori=0.0,
        color='black', colorSpace='rgb', opacity=None,
        languageStyle='LTR',
        depth=-1.0)
    stack_tl = visual.TextStim(
        win=win, name='stack_tl',
        text=stack,
        font='Open Sans',
        pos=(-2.4, 4), height=0.7, wrapWidth=None, ori=0.0,
        color='black', colorSpace='rgb', opacity=None,
        languageStyle='LTR',
        depth=-1.0)
    stack_br = visual.TextStim(
        win=win, name='stack_br',
        text=stack,
        font='Open Sans',
        pos=(2.4, -4), height=0.7, wrapWidth=None, ori=0.0,
        color='black', colorSpace='rgb', opacity=None,
        languageStyle='LTR',
        depth=-1.0)

    background.draw()
    number.draw()
    stack_tl.draw()
    stack_br.draw()

#initialisation des variables
global score
global essai
score  = 2000
fichier = open("fichiers_texte/nom_du_patient.txt","w") #création d'un fichier texte
fichier.write("Essai    tas    points\n")
fichier.flush()
keys = kb.getKeys()
essai = 0

while 'escape' not in keys:

    try:
        global value
        global stack
        
        data = sock.recv(8192)  # This is the amount of bytes to read at maximum
        dataDict = json.loads(data)
        msg = dataDict['msg']
        value = dataDict['value']
        stack = dataDict['stack']
        
        if (msg == 'choose'):
            print(value, stack)
            draw_card(value, stack)
            score = score + int(value)
            drawScore(score)
            print("carte choisie")
            essai +=1
            fichier.write(str(essai)+"    "+str(stack)+"    "+str(value)+"\n")
            fichier.flush()
            if int(value) >= 0 :
                resultat = 1
            else : 
                resultat = 0
            

    except socket.error:
        pass

    keys = kb.getKeys()
    for thisKey in keys:
        if thisKey =='d':
            flux_outlet.push_sample([1])
            print("decision")
        
        elif thisKey =='r':
            flux_outlet.push_sample(2)
            print("button pressed")

        elif thisKey =='o':
            flux_outlet.push_sample([int(str(resultat))])
            win.flip()
            print("led_ON")

        elif thisKey =='h':
            win.flip()
            print("led_OFF")

sock.close()
win.close()
core.quit() 
