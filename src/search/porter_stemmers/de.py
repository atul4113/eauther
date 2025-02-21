# -*- coding: utf-8 -*-
#   Eine Pythonimplementation des Porter-Stemmers für Deutsch (Orginal unter http://snowball.tartarus.org/texts/germanic.html)
#
#   Modifiziert/optimiert/gefixt von Waldemar Kornewald
#
#   Ersteller dieser Version: (c) by kristall 'ät' c-base.org       http://kristall.crew.c-base.org/porter_de.py
#
#   Der Algorithmus in (englischem) Prosa unter http://snowball.tartarus.org/algorithms/german/stemmer.html
#
#   Wikipedia zum Porter-Stemmer: http://de.wikipedia.org/wiki/Porter-Stemmer-Algorithmus
#
#   Lizenz: Diese Software steht unter der BSD License (siehe http://www.opensource.org/licenses/bsd-license.html).
#   Ursprünglicher Autor: (c) by Dr. Martin Porter 
#
#
###

#   Wer mit Strings arbeitet, sollte dieses Modul laden
import string

#   Die Stopliste; Wörter in dieser Liste werden nicht 'gestemmt', wenn stop  = 'True' an die Funktion übergeben wurde
stopliste = ('aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am', 'an', 'ander', 'andere', 'anderem',
        'anderen', 'anderer', 'anderes', 'anderm', 'andern', 'anders', 'auch', 'auf', 'aus', 'bei', 'bin', 'bis', 'bist',
        'da', 'damit', 'dann', 'der', 'den', 'des', 'dem', 'die', 'das', 'dass', 'daß', 'derselbe', 'derselben', 'denselben',
        'desselben', 'demselben', 'dieselbe', 'dieselben', 'dasselbe', 'dazu', 'dein', 'deine', 'deinem', 'deinen', 'deiner',
        'deines', 'denn', 'derer', 'dessen', 'dich', 'dir', 'du', 'dies', 'diese', 'diesem', 'diesen', 'dieser', 'dieses',
        'doch', 'dort', 'durch', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'einig', 'einige', 'einigem', 'einigen', 
        'einiger', 'einiges', 'einmal', 'er', 'ihn', 'ihm', 'es', 'etwas', 'euer', 'eure', 'eurem', 'euren', 'eurer', 'eures',
        'für', 'gegen', 'gewesen', 'hab', 'habe', 'haben', 'hat', 'hatte', 'hatten', 'hier', 'hin', 'hinter', 'ich', 'mich',
        'mir', 'ihr', 'ihre', 'ihrem', 'ihren', 'ihrer', 'ihres', 'euch', 'im', 'in', 'indem', 'ins', 'ist', 'jede', 'jedem',
        'jeden', 'jeder', 'jedes', 'jene', 'jenem', 'jenen', 'jener', 'jenes', 'jetzt', 'kann', 'kein', 'keine', 'keinem', 
        'keinen', 'keiner', 'keines', 'können', 'könnte', 'machen', 'man', 'manche', 'manchem', 'manchen', 'mancher', 
        'manches', 'mein', 'meine', 'meinem', 'meinen', 'meiner', 'meines', 'mit', 'muss', 'musste', 'muß', 'mußte', 'nach',
        'nicht', 'nichts', 'noch', 'nun', 'nur', 'ob', 'oder', 'ohne', 'sehr', 'sein', 'seine', 'seinem', 'seinen', 'seiner',
        'seines', 'selbst', 'sich', 'sie', 'ihnen', 'sind', 'so', 'solche', 'solchem', 'solchen', 'solcher', 'solches', 'soll',
        'sollte', 'sondern', 'sonst', 'über', 'um', 'und', 'uns', 'unse', 'unsem', 'unsen', 'unser', 'unses', 'unter', 'viel',
        'vom', 'von', 'vor', 'während', 'war', 'waren', 'warst', 'was', 'weg', 'weil', 'weiter', 'welche', 'welchem', 
        'welchen', 'welcher', 'welches', 'wenn', 'werde', 'werden', 'wie', 'wieder', 'will', 'wir', 'wird', 'wirst', 'wo',
        'wollem', 'wollte', 'würde', 'würden', 'zu', 'zum', 'zur', 'zwar', 'zwischen')

#   Die Funktion stem nimmt ein Wort und versucht dies durch Regelanwendung zu verkürzen. Wenn Stop auf 'True' gesetzt wird, werden Wörter in der Stopliste nicht 'gestemmt'.
def stem(wort, stop=True):
    #   ACHTUNG: für den Stemmer gilt 'y' als Vokal.
    vokale = 'aeiouyäüö'
    #   ACHTUNG: 'U' und 'Y' gelten als Konsonaten.
    konsonanten = 'bcdfghjklmnpqrstvwxzßUY'
    #   Konsonanten die vor einer 's'-Endung stehen dürfen.
    s_endung = 'bdfghklmnrt'
    #   Konsonanten die vor einer 'st'-Endung stehen dürfen.
    st_endung = 'bdfghklmnt'
    #   Zu r1 & r2 siehe http://snowball.tartarus.org/texts/r1r2.html, p1 & p2 sind die Start'p'ositionen von r1 & r2 im String
    r1 = ''
    p1 = 0
    r2 = ''
    p2 = 0
    #   Wortstämme werden klein geschrieben
    wort = wort.lower()
    #   Wenn 'stop' und Wort in Stopliste gib 'wort' zurück 
    if stop == True and wort in stopliste:
        return end_stemming(wort.replace('ß', 'ss'))
    # Ersetze alle 'ß' durch 'ss'
    wort = wort.replace('ß', 'ss')
    #   Schützenswerte 'u' bzw. 'y' werden durch 'U' bzw. 'Y' ersetzt
    for e in map(None, wort, list(range(len(wort)))):
        if e[1] == 0: continue
        if 'u' in e:
            try:
                if ((wort[(e[1]-1)] in vokale) and (wort[(e[1]+1)] in vokale)): wort = wort[:e[1]] + 'U' + wort[(e[1]+1):]
            except : pass
        if  'y' in e:
            try:
                if ((wort[(e[1]-1)] in vokale) and (wort[(e[1]+1)] in vokale)): wort = wort[:e[1]] + 'Y' + wort[(e[1]+1):]
            except: pass
    #   r1, r2, p1 & p2 werden mit Werten belegt
    try:
        Bedingung = False
        for e in map(None, wort, list(range(len(wort)))):
            if e[0] in vokale: Bedingung = True
            if ((e[0] in konsonanten) and (Bedingung)):
                p1 = e[1] + 1 
                r1 = wort[p1:]
                break
        Bedingung = False
        for e in map(None, r1, list(range(len(r1)))):
            if e[0] in vokale: Bedingung = True
            if ((e[0] in konsonanten) and (Bedingung)):
                p2 = e[1] + 1 
                r2 = r1[p2:]
                break
        if ((p1 < 3)and(p1 > 0)):
            p1 = 3
            r1 = wort[p1:]
        if p1 == 0:
            return end_stemming(wort)
    except: pass
    #   Die Schritte 1 bis 3 d) 'stemmen' das übergebene Wort. 
    #   Schritt 1
    eSuffixe_1 = ['e', 'em', 'en', 'ern', 'er', 'es']
    eSonst_1 = ['s']
    try:
        for e in eSuffixe_1:
            if e in r1[-(len(e)):]:
                wort = wort[:-(len(e))]
                r1 = r1[:-(len(e))]
                r2 = r2[:-(len(e))]
                break
        else:
            if r1[-1] in eSonst_1:
                if wort[-2] in s_endung:
                    wort = wort[:-1]
                    r1 = r1[:-1]
                    r2 = r2[:-1]
    except: pass
    #   Schritt 2
    eSuffixe_2 = ['est', 'er', 'en']
    eSonst_2 = ['st']
    try:
        for e in eSuffixe_2:
            if e in r1[-len(e):]:
                wort = wort[:-len(e)]
                r1 = r1[:-len(e)]
                r2 = r2[:-len(e)]
                break
        else:
            if r1[-2:] in eSonst_2:             
                if wort[-3] in st_endung:
                    if len(wort) > 5:
                        wort = wort[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]
    except:pass
    #   Schritt 3 a)
    dSuffixe_1 = ['end', 'ung']
    try:
        for e in dSuffixe_1:
            if e in r2[-(len(e)):]:
                if 'ig' in r2[-(len(e)+2):-(len(e))]:
                    if 'e' in wort[-(len(e)+3)]:
                        wort = wort[:-(len(e))]
                        r1 = r1[:-(len(e))]
                        r2 = r2[:-(len(e))]
                        break
                    else:
                        wort = wort[:-(len(e)+2)]
                        r2 = r2[:-(len(e)+2)]
                        r1 = r1[:-(len(e)+2)]
                        break
                else:
                    wort = wort[:-(len(e))]
                    r2 = r2[:-(len(e))]
                    r1 = r1[:-(len(e))]
                return end_stemming(wort)
    except: pass
    #   Schritt 3 b)
    dSuffixe_2 = ['ig', 'ik', 'isch']
    try:
        for e in dSuffixe_2:
            if e in r2[-(len(e)):]:
                if (('e' in wort[-(len(e)+1)])):
                    pass
                else:
                    wort = wort[:-(len(e))]
                    r2 = r2[:-(len(e))]
                    r1 = r1[:-(len(e))]
                    break
    except: pass
    #   Schritt 3 c)
    dSuffixe_3 = ['lich', 'heit']
    sonder_1 = ['er', 'en']
    try: 
        for e in dSuffixe_3:
            if e in r2[-(len(e)):]:
                for i in sonder_1:
                    if i in r1[-(len(e)+len(i)):-(len(e))]:
                        wort = wort[:-(len(e)+len(i))]
                        r1 = r1[:-(len(e)+len(i))]
                        r2 = r2[:-(len(e)+len(i))]
                        break
                else:
                    wort = wort[:-(len(e))]
                    r1 = r1[:-(len(e))]
                    r2 = r2[:-(len(e))]
                    break
                        
    except: pass
    #   Schritt 3 d)
    dSuffixe_4 = ['keit']
    sonder_2 = ['lich', 'ig']
    try:
        for e in dSuffixe_4:
            if e in r2[-(len(e)):]:
                for i in sonder_2:
                    if i in r2[-(len(e)+len(i)):-(len(e))]:
                        wort = wort[:-(len(e)+len(i))]
                        break
                else:
                    wort = wort[:-(len(e))]
                                    
    except: pass
    return end_stemming(wort)

#  end_stemming verwandelt u'ä', u'ö', u'ü' in den "Grundvokal" und macht 'U' bzw. 'Y' klein. 
def end_stemming(wort):
    return wort.replace('ä', 'a').replace('ö', 'o').replace(
        'ü', 'u').replace('U', 'u').replace('Y', 'y')
