import socket
from psychopy import visual, core
from psychopy.hardware import keyboard
from pylsl import StreamInfo, StreamOutlet
import json
import random
import time
import select
import pyttsx3

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 6667))
sock.setblocking(0)
sock.settimeout(0.002)


## LSL
flux_info = StreamInfo(name='flux_stream', type='Markers', channel_count=1, channel_format='int8', source_id='flux_stream_001')
flux_outlet = StreamOutlet(flux_info)

win = visual.Window(size=(800, 800), monitor='testMonitor', units='cm')  # Change to your monitor name

kb = keyboard.Keyboard()

engine=pyttsx3.init()

def draw_dice(values,y):
    dice_size = 1.6  # Taille d'un dé en centimètres
    dice_spacing = 0.5  # Espacement entre les dés en centimètres
    
    num_dice = len(values)
    total_width = (num_dice * dice_size) + ((num_dice - 1) * dice_spacing)
    starting_x = (dice_size-total_width)/2  # Position x du premier dé
    
    for i, val in enumerate(values):
        dice_x = starting_x + (i * (dice_size + dice_spacing))
        
        # Créer les objets visuels pour chaque dé
        background = visual.Rect(
            win=win, name='background', units='cm',
            width=dice_size, height=dice_size,
            ori=0.0, pos=(dice_x, y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='white',
            opacity=None, depth=0.0, interpolate=True)

        dot_lt = visual.ShapeStim(
            win=win, name='dot_lt', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x - 0.5, 0.5 + y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)

        dot_rt = visual.ShapeStim(
            win=win, name='dot_rt', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x + 0.5, 0.5 + y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)
            
        dot_lm = visual.ShapeStim(
            win=win, name='dot_mm', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x -0.5, y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)
        dot_mm = visual.ShapeStim(
            win=win, name='dot_mm', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x, y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)
        dot_rm = visual.ShapeStim(
            win=win, name='dot_mm', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x + 0.5, y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)
        dot_lb = visual.ShapeStim(
            win=win, name='dot_mm', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x - 0.5, -0.5 + y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)
        dot_rb = visual.ShapeStim(
            win=win, name='dot_mm', units='cm',
            size=(0.25, 0.25), vertices='circle',
            pos=(dice_x + 0.5, -0.5 + y), anchor='center',
            lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
            opacity=None, depth=-1.0, interpolate=True)

        # Dessiner les dés
        background.draw()

        if val == 1:
            dot_mm.draw()

        elif val == 2:
            dot_lt.draw()
            dot_rb.draw()

        elif val == 3:
            dot_lt.draw()
            dot_mm.draw()
            dot_rb.draw()

        elif val == 4:
            dot_lt.draw()
            dot_rt.draw()
            dot_lb.draw()
            dot_rb.draw()

        elif val == 5:
            dot_lt.draw()
            dot_rt.draw()
            dot_mm.draw()
            dot_lb.draw()
            dot_rb.draw()

        elif val == 6:
            dot_lt.draw()
            dot_rt.draw()
            dot_lm.draw()
            dot_rm.draw()
            dot_lb.draw()
            dot_rb.draw()


#game of dice

def drawScore(score):
    score = visual.TextStim(
        win=win, name='score',
        text='votre score est de : ' + str(score),
        font='Open Sans',
        pos=(0, 4), height=1, wrapWidth=None, ori=0.0,
        color='black', colorSpace='rgb', opacity=None,
        languageStyle='LTR',
        depth=-1.0)
    score.draw()

def proposer_nombre(n):
    draw_dice(n,0)
    win.flip()
    if len(n) == 1:
        I = str(n[0])
        text= "Pour 1000 euros, si vous faites, " + I + " , c'est gagné"
        engine.say(text)
        engine.runAndWait()
    elif len(n) == 2:
        text= "Pour 500 euros, si vous faites, " + str(n[0]) + " ou, " + str(n[1]) + " , c'est gagné"
        engine.say(text)
        engine.runAndWait()
    elif len(n) == 3:
        text= "Pour 200 euros, si vous faites, " + str(n[0]) + " , " + str(n[1]) + " ou, " + str(n[2]) + " , c'est gagné"
        engine.say(text)
        engine.runAndWait()
    else:
        text= "Pour 100 euros, si vous faites, " + str(n[0]) + " , " + str(n[1]) + " , " + str(n[2]) + " ou, " + str(n[3]) + " , c'est gagné"
        engine.say(text)
        engine.runAndWait()


def generer_nombres_uniques(n):
    nombres = random.sample(range(1, 7), n)
    nombres.sort()
    return nombres


def jouer1():
    global nb_nombres
    global keys
    global score
    global nb_parties
    global choix5
    global nombres
    global fichier
    global sock
    
    visual.TextStim(win=win,text='Choisissez le nombre de faces sur lesquelles vous voulez parier:',font='Open Sans',pos=(0, 0), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
    win.flip()
    text= "combien de faces?"
    engine.say(text)
    engine.runAndWait()
    start_time = time.time()
    keys.clear()
    kb.clearEvents()
    while 'num_1' not in keys and 'num_2' not in keys and 'num_3' not in keys and 'num_4' not in keys:
        keys = kb.getKeys()
    if 'num_1' in keys:
        end_time = time.time()
        elapsed_time = end_time - start_time
        nb_nombres = 1
        flux_outlet.push_sample([1])
        fichier.write(str(elapsed_time)+"    "+str(nb_nombres)+"    ")
        fichier.flush()
    elif 'num_2' in keys:
        end_time = time.time()
        elapsed_time = end_time - start_time
        nb_nombres = 2
        flux_outlet.push_sample([2])
        fichier.write(str(elapsed_time)+"    "+str(nb_nombres)+"    ")
        fichier.flush()
    elif 'num_3' in keys:
        end_time = time.time()
        elapsed_time = end_time - start_time
        nb_nombres = 3
        flux_outlet.push_sample([3])
        fichier.write(str(elapsed_time)+"    "+str(nb_nombres)+"    ")
        fichier.flush()
    elif 'num_4' in keys:
        end_time = time.time()
        elapsed_time = end_time - start_time
        nb_nombres = 4
        flux_outlet.push_sample([4])
        fichier.write(str(elapsed_time)+"    "+str(nb_nombres)+"    ")
        fichier.flush()
    nombres = generer_nombres_uniques(nb_nombres)
    fichier.write(str(nombres)+"    ")
    fichier.flush()
    proposer_nombre(nombres)
    visual.TextStim(win=win,text='lancez le dé !:',font='Open Sans',pos=(0, 0), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
    win.flip()
    keys.clear()
    kb.clearEvents()
    vider_cache(sock)
    text= "lancez le dé"
    engine.say(text)
    engine.runAndWait()
    return   
        


def jouer2():
    global nb_nombres
    global keys
    global score
    global nb_parties
    global choix1,choix2,choix3,choix4
    global value
    global nombres
    global marker
    global fichier
    
    visual.TextStim(win=win,text='appuyez sur le bouton :',font='Open Sans',pos=(0, 8), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
    win.flip()
    text= "appuyez sur le bouton"
    engine.say(text)
    engine.runAndWait()
    V = str(value)
    while 'r' not in keys:
        keys = kb.getKeys()
    flux_outlet.push_sample([5])
    while 'o' not in keys:
        keys = kb.getKeys()
    flux_outlet.push_sample([marker])
    draw_dice([value],0)
    win.flip()
    if value in nombres:
        text= "gagné, vous avez fait, " + V
        engine.say(text)
        engine.runAndWait()
        if nb_nombres == 1:
            score += 1000
            choix1 +=1
        elif nb_nombres == 2:
            score += 500
            choix2 +=1
        elif nb_nombres == 3:
            score += 200
            choix3 +=1
        else:
            score += 100
            choix4 +=1
        visual.TextStim(win=win,text='C est gagné!',font='Open Sans',pos=(0, 8), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
        drawScore(score)
        win.flip()
    else:
        text= "perdu, vous avez fait, " + V
        engine.say(text)
        engine.runAndWait()
        if nb_nombres == 1:
            score -= 1000
            choix1 +=1
        elif nb_nombres == 2:
            score -= 500
            choix2 +=1
        elif nb_nombres == 3:
            score -= 200
            choix3 +=1
        else:
            score -= 100
            choix4 +=1
        visual.TextStim(win=win,text='Dommage c est perdu!',font='Open Sans',pos=(0, 8), height=1, wrapWidth=None, ori=0.0,color='black', colorSpace='rgb', opacity=None, languageStyle='LTR', depth=-1.0).draw()
        drawScore(score)
        win.flip()
    text= "cagnotte " + str(score) + " euros"
    engine.say(text)
    engine.runAndWait()
    nb_parties += 1
    keys.clear()
    kb.clearEvents()
    return

def vider_cache(sock):
    input = [sock]
    while 1:
        inputready, o, e =select.select(input,[],[], 0.0)
        if len(inputready)==0: 
            break
        for s in inputready :
            s.recv(8192)


#initialisation des variables
score  = 1000
nb_parties = 0
choix1,choix2,choix3,choix4,choix5 = 0,0,0,0,0
keys=[]
nombres = []
fichier = open("fichiers_texte/nom_du_patient.txt","w") #création d'un fichier texte
fichier.write("Essai    latence_choix(s)    choix    proposition    résultat_dé    résultat\n")
fichier.flush()


#boucle principale
while nb_parties < 5: #choisir combien de parties on veut faire   
    nb_nombres = 1
    fichier.write(str(nb_parties+1)+"    ")
    fichier.flush()    
    jouer1()
    msg = ""
    print("message1 :", msg)    
    while msg != 'throw':
        try:
            data = sock.recv(8192)  # This is the amount of bytes to read at maximum
            dataDict = json.loads(data)
            msg = dataDict['msg']
            value = dataDict['value']
            if value in nombres:
                marker = 6
                fichier.write(str(value)+"    "+"victoire\n")
                fichier.flush()
            else:
                marker = 7
                fichier.write(str(value)+"    "+"défaite\n")
                fichier.flush()
        except socket.error:
            pass
    jouer2()
    data=None
    dataDict.clear()
    msg=""
    value=None
    


print("nombre de parties : ",nb_parties)
print("score final : ",score)
print("nombre de choix 1 : ",choix1)
print("nombre de choix 2 : ",choix2)
print("nombre de choix 3 : ",choix3)
print("nombre de choix 4 : ",choix4)

fichier.close()
sock.close()
win.close()
core.quit()
