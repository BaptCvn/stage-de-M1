import asyncio
from bleak import BleakScanner, BleakClient
from pynput import keyboard
import csv
import math
from psychopy import visual
import random
from pylsl import StreamInfo, StreamOutlet
import datetime

global client
global power
global bpm
global cadence
global keys
global win

def date():
    maintenant = datetime.datetime.now()
    annee = str(maintenant.year)
    if maintenant.month < 10:
        mois = "0"+str(maintenant.month)
    else:
        mois = str(maintenant.month)
    if maintenant.day < 10:
        jour = "0"+str(maintenant.day)
    else:
        jour = str(maintenant.day)
    if maintenant.hour < 10:
        heure = "0"+str(maintenant.hour)
    else:
        heure = str(maintenant.hour)
    if maintenant.minute < 10:
        minutes = "0"+str(maintenant.minute)
    else:
        minutes = str(maintenant.minute)
    if maintenant.second < 10:
        secondes = "0"+str(maintenant.second)
    else:
        secondes = str(maintenant.second)
    return annee+"-"+mois+"-"+ jour+"-"+ heure+"-"+ minutes+"-"+ secondes 

def dessiner_menu_des_choix(gain,proba,taille_fenetre):
    global win
    prop_x=taille_fenetre[0]/1530
    prop_y=taille_fenetre[1]/800
    image = visual.ImageStim(win, image="boitier.jpg",size=(0.5*prop_x,0.5*prop_y),pos=(0,0))    
    image.draw()
    text1 = visual.TextStim(win, text="1",pos=(-0.5*0.4*prop_x, 0.5*0.48*prop_y),color="yellow",height=0.15*prop_y)
    text1.draw()
    text2 = visual.TextStim(win, text=str(gain),pos=(0.5*0.4*prop_x, 0.5*0.48*prop_y),color="green",height=0.15*prop_y)
    text2.draw()
    text = visual.TextStim(win, text=str(100*proba)+"%",pos=(0, -0.1*prop_y),height=0.15*prop_y)
    text.draw()
    win.flip()

def draw_circle(proportions):
    global win
    cercle = visual.Circle(win, size=(0.5*proportions,0.5), lineColor='black', fillColor='grey')
    cercle.draw()
    win.flip()
    
def dessiner_carre(couleur,proportions):
    global win
    carre = visual.Rect(win=win, width=0.5*proportions, height=0.5)
    if couleur == "vert":
        carre.fillColor = "green"
    elif couleur == "rouge":
        carre.fillColor = "red"
    else:
        print("Couleur non prise en charge.")
    carre.draw()
    win.flip()

def draw_cross(proportions):
    global win
    cross_size = 0.1
    cross_thickness = 5
    cross_color = "white"    
    line1 = visual.Line(win, start=(-cross_size*proportions, 0), end=(cross_size*proportions, 0), lineColor=cross_color, lineWidth=cross_thickness) 
    line2 = visual.Line(win, start=(0, -cross_size), end=(0,cross_size), lineColor=cross_color, lineWidth=cross_thickness)    
    line1.draw()
    line2.draw()
    win.flip()
    
async def indication_callback(sender: int, data: bytearray):
    pass

async def notification_callback(sender: int, data: bytearray):
    global bpm
    global cadence
    if len(data) == 17:
        bpm = data[11]
    if len(data) == 15:
        byte1 = data[2]
        byte2 = data[3]
        cadence = byte2 << 8 | byte1
        cadence = cadence/2

def on_key_press(key):
    global keys
    keys.append(key)
        
async def modify_power(increment, increment_pct):
    global power
    global client
    power += increment
    power = math.floor(power*(1+increment_pct/100))
    hexadecimal_power = "{:02x}".format(power)
    hexadecimal_command = "05" + hexadecimal_power + "00"
    byte_array = bytearray.fromhex(f"{hexadecimal_command}")
    await client.write_gatt_char('00002ad9-0000-1000-8000-00805f9b34fb', byte_array, True)
    print("Modified power:", power)

async def EEfRT(nb_essais,nb_pauses,duree_croix,duree_proposition,duree_choix,duree_facile,duree_difficile,duree_carre,
                duree_messages,gains_possibles,probabilites,puissance_repos,puissance_facile,puissance_difficile,cadence_min,
                bpm_max,temps_depassement,nom_du_fichier,taille_fenetre):
    global win
    global client
    global power
    global bpm
    global exit
    global cadence
    global keys
    bpm = 89
    cadence = 70
    win = visual.Window(size=taille_fenetre, monitor='testMonitor')
    proportions = taille_fenetre[1]/taille_fenetre[0]
    keys=[]
    keys.clear()
    fichier_csv = nom_du_fichier + "_" + date() + '.csv'
    data = ["temps (s)","fréquence cardiaque (bpm)","puissance (W)","cadence (rpm)","argent"]
    with open(fichier_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, dialect='excel')
        writer.writerow(data)
    loop = asyncio.get_event_loop()
    power = 0 
    exit = False
    #scanner = BleakScanner()
    essai = 1
    argent = 0
    bpm_dangereux = False
    flux_info = StreamInfo(name='flux_stream', type='Markers', channel_count=1, channel_format='double64',source_id='flux_stream_001')
    flux_outlet = StreamOutlet(flux_info)
    scanner = BleakScanner()
    devices = await scanner.discover()
    await asyncio.sleep(3)
    ###
    for device in devices:
        if device.name == "Monark 86f1":
            print(f"Device found!: {device.address}")
            async with BleakClient(device.address) as client:
                await client.start_notify('00002ad9-0000-1000-8000-00805f9b34fb', indication_callback)
                await client.start_notify('00002ad2-0000-1000-8000-00805f9b34fb', notification_callback)
                print("Abonné aux notifications.")
                await client.write_gatt_char('00002ad9-0000-1000-8000-00805f9b34fb', b'\x00', True)
                await asyncio.sleep(0.5)
                print("Contrôle autorisé")
                chrono = loop.time()
                await modify_power(puissance_repos-power,0)
                while essai <= nb_essais:
                    for h in range(1,nb_pauses+1):
                        if essai == 1+h*(nb_essais/(nb_pauses+1)):
                            flux_outlet.push_sample([1])
                            text = visual.TextStim(win, text="appuyez sur p pour mettre fin à la pause")
                            text.draw()
                            win.flip()
                            keys.clear()
                            listener = keyboard.Listener(on_press=on_key_press)
                            listener.start()
                            while not (any(hasattr(key, 'char') and key.char == 'p' for key in keys)):
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                            listener.stop()
                    draw_cross(proportions)
                    temps = loop.time()
                    while loop.time() - temps < duree_croix:
                        data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                        with open(fichier_csv, 'a', newline='') as csv_file:
                            writer = csv.writer(csv_file, dialect='excel')
                            writer.writerow(data) 
                        await asyncio.sleep(1)
                    gain = random.choice(gains_possibles)
                    proba = random.choice(probabilites)
                    dessiner_menu_des_choix(gain,proba,taille_fenetre)                   
                    temps = loop.time()
                    while loop.time() - temps < duree_proposition:
                        data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                        with open(fichier_csv, 'a', newline='') as csv_file:
                            writer = csv.writer(csv_file, dialect='excel')
                            writer.writerow(data) 
                        await asyncio.sleep(1)
                    draw_circle(proportions)
                    choix = None
                    keys.clear()
                    listener = keyboard.Listener(on_press=on_key_press)
                    listener.start()
                    temps = loop.time()
                    while loop.time() - temps < duree_choix:
                        if bpm_dangereux == True:
                            bpm_dangereux = False
                            choix = "facile"
                            text = visual.TextStim(win, text="votre fréquence cardiaque est trop élevée, choix facile par défaut")
                            text.draw()
                            win.flip()
                            temps = loop.time()
                            while loop.time() - temps < duree_messages:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1) 
                            break
                        elif any(hasattr(key, 'char') and key.char == 'q' for key in keys):
                            flux_outlet.push_sample([float(str(21)+str(int(100*proba))+str(gain))])
                            choix = "facile"
                            text = visual.TextStim(win, text="vous avez fait le choix facile")
                            text.draw()
                            win.flip()
                            temps = loop.time()
                            while loop.time() - temps < duree_messages:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1) 
                            break
                        elif any(hasattr(key, 'char') and key.char == 'g' for key in keys):
                            flux_outlet.push_sample([float(str(22)+str(int(100*proba))+str(gain))])
                            choix = "difficile"
                            text = visual.TextStim(win, text="vous avez fait le choix difficile")
                            text.draw()
                            win.flip()
                            temps = loop.time()
                            while loop.time() - temps < duree_messages:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1) 
                            break
                        data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                        with open(fichier_csv, 'a', newline='') as csv_file:
                            writer = csv.writer(csv_file, dialect='excel')
                            writer.writerow(data) 
                        await asyncio.sleep(1)                     
                    listener.stop()
                    if choix == "facile":
                        resultat = "gagné"
                        await modify_power(puissance_facile-power,0)
                        temps = loop.time()
                        i=0
                        j=0
                        while (loop.time()-temps) < duree_facile:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data)
                            if cadence < cadence_min:
                                i+=1
                                text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_facile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="red",height=0.12*taille_fenetre[1]/800)
                                text1.draw()
                                text2.draw()
                                text3.draw()                        
                                win.flip()
                                if i>temps_depassement:
                                    resultat = "perdu"
                            if cadence >= cadence_min:
                                i=0
                                if cadence >= cadence_min+5:
                                    text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_facile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="green",height=0.12*taille_fenetre[1]/800)
                                    text1.draw()
                                    text2.draw()
                                    text3.draw()
                                    win.flip()
                                else:
                                    text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_facile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="orange",height=0.12*taille_fenetre[1]/800)
                                    text1.draw()
                                    text2.draw()
                                    text3.draw()
                                    win.flip()
                            if bpm > bpm_max:
                                j+=1
                                if j>temps_depassement:
                                    bpm_dangereux = True
                            if bpm <= bpm_max:
                                j=0
                            await asyncio.sleep(1)
                        await modify_power(puissance_repos-power,0)
                    elif choix == "difficile" :                      
                        resultat = "gagné"
                        await modify_power(puissance_difficile-power,0)
                        temps = loop.time()
                        i=0
                        j=0
                        while (loop.time()-temps) < duree_difficile:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data)
                            if cadence < cadence_min:
                                i+=1
                                text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_difficile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="red",height=0.12*taille_fenetre[1]/800)
                                text1.draw()
                                text2.draw()
                                text3.draw()
                                win.flip()
                                if i>=temps_depassement:
                                    resultat = "perdu"
                            if cadence >= cadence_min:
                                i=0
                                if cadence >= cadence_min+5:
                                    text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_difficile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="green",height=0.12*taille_fenetre[1]/800)
                                    text1.draw()
                                    text2.draw()
                                    text3.draw()
                                    win.flip()
                                else:
                                    text1 = visual.TextStim(win, text="temps restant: "+str(round(duree_difficile-(loop.time()-temps))),pos=(0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text2 = visual.TextStim(win, text="fréquence cardiaque: "+str(data[1]),pos=(-0.5*taille_fenetre[0]/1530,0.8*taille_fenetre[1]/800),height=0.12*taille_fenetre[1]/800)
                                    text3 = visual.TextStim(win, text="cadence: "+str(data[3]),color="orange",height=0.12*taille_fenetre[1]/800)
                                    text1.draw()
                                    text2.draw()
                                    text3.draw()
                                    win.flip()
                            if bpm > bpm_max:
                                j+=1
                                if j>temps_depassement:
                                    bpm_dangereux = True
                            if bpm <= bpm_max:
                                j=0
                            await asyncio.sleep(1)
                        await modify_power(puissance_repos-power,0)
                    else :
                        resultat = "perdu"
                    if resultat == "perdu":
                        draw_cross(proportions)
                        temps = loop.time()
                        while loop.time() - temps < duree_croix:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data) 
                            await asyncio.sleep(1)
                        if choix == "facile" or choix == "difficile":
                            dessiner_carre("rouge",proportions)
                            flux_outlet.push_sample([311])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                            text = visual.TextStim(win, text="perdu, cadence insuffisante")
                            text.draw()
                            win.flip()
                            temps = loop.time()
                            while loop.time() - temps < duree_messages:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                        else :
                            dessiner_carre("rouge",proportions)
                            flux_outlet.push_sample([312])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                            text = visual.TextStim(win, text="perdu, vous n'avez pas choisi à temps")
                            text.draw()
                            win.flip()
                            temps = loop.time()
                            while loop.time() - temps < duree_messages:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                    elif resultat == "gagné" and choix == "facile":
                        text = visual.TextStim(win, text="complété!")
                        text.draw()
                        win.flip()
                        temps = loop.time()
                        while loop.time() - temps < duree_messages:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data) 
                            await asyncio.sleep(1)
                        if random.random() <= proba:
                            tirage = "gagné"
                        else :
                            tirage = "perdu"
                        draw_cross(proportions)
                        temps = loop.time()
                        while loop.time() - temps < duree_croix:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data) 
                            await asyncio.sleep(1)
                        if tirage == "gagné":
                            argent+=1
                            dessiner_carre("vert",proportions)
                            flux_outlet.push_sample([float(str(32)+str(int(100*proba))+str(1))])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                        else:
                            dessiner_carre("rouge",proportions)
                            flux_outlet.push_sample([float(str(313)+str(int(100*proba))+str(1))])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                    else :
                        text = visual.TextStim(win, text="complété!")
                        text.draw()
                        win.flip()
                        temps = loop.time()
                        while loop.time() - temps < duree_messages:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data) 
                            await asyncio.sleep(1)
                        if random.random() <= proba:
                            tirage = "gagné"
                        else :
                            tirage = "perdu"
                        draw_cross(proportions)
                        temps = loop.time()
                        while loop.time() - temps < duree_croix:
                            data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                            with open(fichier_csv, 'a', newline='') as csv_file:
                                writer = csv.writer(csv_file, dialect='excel')
                                writer.writerow(data) 
                            await asyncio.sleep(1)
                        if tirage == "gagné":
                            argent+=gain
                            dessiner_carre("vert",proportions)
                            flux_outlet.push_sample([float(str(32)+str(int(100*proba))+str(gain))])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                        else:
                            dessiner_carre("rouge",proportions)
                            flux_outlet.push_sample([float(str(21)+str(int(100*proba))+str(gain))])
                            temps = loop.time()
                            while loop.time() - temps < duree_carre:
                                data = [round(loop.time()-chrono, 1),bpm,power,cadence,argent]
                                with open(fichier_csv, 'a', newline='') as csv_file:
                                    writer = csv.writer(csv_file, dialect='excel')
                                    writer.writerow(data) 
                                await asyncio.sleep(1)
                    essai +=1
             
                win.close()
                await client.stop_notify('00002ad9-0000-1000-8000-00805f9b34fb')
                await client.stop_notify('00002ad2-0000-1000-8000-00805f9b34fb')
                print("désabonné")
                
# Ouvrir le fichier texte
with open('arguments.txt', 'r') as file:
    # Lire les lignes du fichier
    lignes = file.readlines()
# Initialiser un dictionnaire pour stocker les arguments
arguments = {}
# Extraire les arguments du fichier texte
i = 0
while i < len(lignes):
    ligne = lignes[i].strip()
    if ligne.endswith(':'):
        # Extraire l'identifiant de l'argument
        identifiant = ligne[:-1].strip()
        # Extraire la valeur de l'argument
        valeur = lignes[i+1].strip()
        # Extraire la description de l'argument
        description = lignes[i+2].strip()
        # Ajouter l'argument au dictionnaire
        arguments[identifiant] = {'valeur': valeur, 'description': description}
        # Passer à l'argument suivant
        i += 4
    else:
        i += 1

# Appeler la fonction avec les arguments extraits
await EEfRT(int(arguments['nb_essais']['valeur']), int(arguments['nb_pauses']['valeur']), int(arguments['duree_croix']['valeur']), int(arguments['duree_proposition']['valeur']), int(arguments['duree_choix']['valeur']), int(arguments['duree_facile']['valeur']), int(arguments['duree_difficile']['valeur']), int(arguments['duree_carre']['valeur']), int(arguments['duree_messages']['valeur']), eval(arguments['gains_possibles']['valeur']), eval(arguments['probabilites']['valeur']), int(arguments['puissance_repos']['valeur']), int(arguments['puissance_facile']['valeur']), int(arguments['puissance_difficile']['valeur']), int(arguments['cadence_min']['valeur']), int(arguments['bpm_max']['valeur']), int(arguments['temps_depassement']['valeur']), arguments['nom_du_fichier']['valeur'], eval(arguments['taille_fenetre']['valeur']))
