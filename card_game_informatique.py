import socket
from psychopy import visual, core
from psychopy.hardware import keyboard
from pylsl import StreamInfo, StreamOutlet
import random
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 6667))
sock.setblocking(0)
sock.settimeout(0.002)


## LSL
flux_info = StreamInfo(name='flux_stream', type='Markers', channel_count=1, channel_format='int8', source_id='flux_stream_001')
flux_outlet = StreamOutlet(flux_info)

win = visual.Window(size=(1530, 800), monitor='testMonitor', units='cm')  # Change to your monitor name
kb = keyboard.Keyboard()


def drawScore(score):
    score = visual.TextStim(
        win=win, name='score',
        text='score : '+ str(score),
        font='Open Sans',
        pos=(0, 5), height=1, wrapWidth=None, ori=0.0,
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
    
def draw_cross():
    cross_size = 2
    cross_thickness = 5
    cross_color = "white"
    
    line1 = visual.Line(win, start=(-cross_size, 0), end=(cross_size, 0), lineColor=cross_color, lineWidth=cross_thickness) 
    line2 = visual.Line(win, start=(0, -cross_size), end=(0,cross_size), lineColor=cross_color, lineWidth=cross_thickness)
    
    line1.draw()
    line2.draw()
    win.flip()
    
def draw_choice(n):
    tas_size = 10 
    tas_spacing = 0.5 
    total_width = (4 * tas_size) + ((3) * tas_spacing)
    starting_x = (tas_size-total_width)/2 
    
    for i in range(4):
        tas_x = starting_x + (i * (tas_size + tas_spacing))
        if i == n-1:
            image = visual.ImageStim(win, image="images/tas_main.jpg",size=(tas_size,tas_size*1.5),pos=(tas_x, -5))
        else :
            image = visual.ImageStim(win, image="images/tas_vide.jpg",size=(tas_size,tas_size*1.5),pos=(tas_x, -5))
        image.draw()
    drawScore(score)
    win.flip()

def tirer_carte(tas):
    tas[0]+=1
    return tas[tas[0]]

#initialisation des variables
global score
global essai
score  = 2000
fichier = open("fichiers_texte/nom_du_patient.txt","w") #création d'un fichier texte
fichier.write("Essai    tas    points\n")
fichier.flush()
keys = kb.getKeys()
essai = 0
tas1 = [0, 600, -200, -600, -600, 1000, -600, -200, -200, 600, -200, -600, -200, -200, -600, -200, -200, -600, 1000, -200, -600, -200, -200, 600, -200, -200, -200, -600, 1000, -600, -200, -200, 600, -600, 1000, -600, -200, -200, -600, 1000, -600, 600, -200, -200, -600, -600, -200, 600, -200, -200, -200]
tas2 = [0, -200, 1000, -200, -200, 600, -200, -200, -600, -600, -200, -600, 600, -600, 1000, -600, -200, -200, -600, 1000, -600, 600, -200, -200, -600, -600, -200, 600, -200, -200, -200, -200, -200, 600, -200, -200, -200, -600, 1000, -600, -200, -200, -200, -200, -600, -600, 1000, -600, -200, -200, 600]
tas3 = [0, 150, -50, 75, 150, -50, -100, 150, -50, 75, -100, -50, 75, -100, -50, 150, -100, -50, 75, 150, -50, 150, 75, 150, 75, -50, 150, -100, 75, -50, -50, -100, -100, 150, -50, 75, 150, -50, 75, -100, -100, 75, -100, 150, -50, 75, -100, 75, 75, -50, -100]
tas4 = [0, -50, 75, -100, -50, 150, -100, -50, 75, 150, -50, 150, 75, 150, 75, -50, 150, -100, 75, -50, -50, -100, -100, 150, -50, 75, 150, -50, 75, -100, -100, 75, -100, 150, -50, 75, -100, 75, 75, -50, -100, 150, -50, 75, 150, -50, -100, 150, -50, 75, -100]

while essai < 10:
    draw_cross()
    essai+=1
    fichier.write(str(essai)+"    ")
    fichier.flush()
    keys.clear()
    kb.clearEvents()
    """
    while "d" not in keys:
        keys = kb.getKeys()
    flux_outlet.push_sample([1])
    """
    while 'num_1' not in keys and 'num_2' not in keys and 'num_3' not in keys and 'num_4' not in keys:
        keys = kb.getKeys()
    if 'num_1' in keys:
        stack = tas1
        num = 1
    elif 'num_2' in keys:
        stack = tas2
        num = 2
    elif 'num_3' in keys:
        stack = tas3
        num = 3
    elif 'num_4' in keys:
        stack = tas4
        num = 4
    keys=[]
    draw_choice(num)
    value = tirer_carte(stack)
    fichier.write(str(num)+"    "+str(value)+"\n")
    fichier.flush()
    if value >=0 :
        resultat = 1
    else : 
        resultat = 0
    time.sleep(2)
    visual.TextStim(win=win,text='appuyez sur le bouton :',font='Open Sans',pos=(0, 8), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
    win.flip()
    keys.clear()
    kb.clearEvents()
    while 'r' not in keys:
        keys = kb.getKeys()
    flux_outlet.push_sample([2])
    draw_cross()
    time.sleep(random.uniform(0.8,1.0))
    draw_card(value, num)
    win.flip()
    score = score + int(value)
    flux_outlet.push_sample([int(str(num)+str(resultat))])
    keys.clear()
    kb.clearEvents()
    time.sleep(2)

sock.close()
win.close()
core.quit()
