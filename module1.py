from random import randint, choice, shuffle

#Genere un pnj shadowrun
def pnj_shadowrun():
    nombre = randint(1,100)
    if nombre <= 60:
        
        metatype = "humain(e)"
    elif nombre <= 74:
        metatype = "elfe"
        
    elif nombre <= 90:
        metatype = "ork"
        
    elif nombre <= 95:
        metatype = "nain(e)"

    elif nombre <= 99:
        metatype = "troll"

    else:
        metatype = choice(["natarki", "dryade", "gnome", "hanuman", "satyr", "ogre", "minotaure", "clyclop", "wakambi"])

    genre = choice(["Un", "Une"])
    
    #Age
    age = choice(["très jeune", "jeune", "jeune", "adulte", "adulte", "adulte", "vieux"])
    
    if age == "vieux" and genre == "Une":
        age = "vieille"

    #Ethenie
    ethenie = choice(["blanc", "noir", "métis", "asiatique"])
    if ethenie == "blanc" and genre == "Une":
        ethenie = "blanche"
        
    elif ethenie == "noir" and genre == "Une":
        ethenie = "noire"

    #Muscle
    muscle = choice([None, None, None, None, None, None, None,
                     "musclé(e)", "musclé(e)",
                     "très musclé(e)"])
    
    #Generation de la description
    if age == "adulte":
        description = " ".join((genre, metatype, "adulte", ethenie))
    else:
        description = " ".join((genre, age, metatype, ethenie))

    if muscle != None:
        description += " et " + muscle
        
    #Implant
    nombre_cyber_membre = randint(-3,8)-5
    
    if nombre_cyber_membre >= 1:
        liste_implant = ["deux cyber-bras", "une paire de cyber-jambes",
                         "un cyber-bras", "un cyber-bras", 
                         "des yeux cybernétiques", "des yeux cybernétiques",
                         "des cyber oreils", "des cyber oreils",
                         "un tatoo-led"]
        
        shuffle(liste_implant)

        implants = liste_implant[:nombre_cyber_membre]

        for i in implants[:]:
            if implants.count(i) > 1:
                implants.remove(i)
                
        description += " avec "+", ".join((implants))
    
    return description
