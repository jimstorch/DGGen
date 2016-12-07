#!/usr/bin/env python3

# Modules
from random import randint, shuffle, choice, sample
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Global variables
TEXT_COLOR = (0, .1, .5)

DEFAULT_FONT = 'Special Elite'
pdfmetrics.registerFont(TTFont('Special Elite', 'data/SpecialElite.ttf'))

MONTHS = ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')

# Read names and places
with open('data/boys1986.txt') as f:
    MALES = f.read().splitlines() 

with open('data/girls1986.txt') as f:
    FEMALES = f.read().splitlines()

with open('data/surnames.txt') as f:
    SURNAMES = f.read().splitlines()  

with open('data/towns.txt') as f:
    TOWNS = f.read().splitlines() 

# Classes
class Need2KnowCharacter(object):

    statpools = (
        [13,13,12,12,11,11],
        [15,14,12,11,10,10],
        [17,14,13,10,10,8],
        )
  
    def __init__(self, gender='male', profession=''):

        ## Hold all dictionary
        self.d = {}

        if gender == 'male':
            self.d['male'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(MALES)
        else:
            self.d['female'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(FEMALES)
        self.d['profession'] = profession
        self.d['nationality'] = '(U.S.A.) ' + choice(TOWNS)
        self.d['age'] = '%d    (%s %d)' % (randint(24,55), choice(MONTHS),
                (randint(1,28)))

        ## Spend the Point Pool
        pool = choice(self.statpools)
        shuffle(pool)
        self.d['strength'] = pool[0]
        self.d['constitution'] = pool[1]
        self.d['dexterity'] = pool[2]
        self.d['intelligence'] = pool[3]
        self.d['power'] = pool[4]
        self.d['charisma'] = pool[5]

        ## Derived Stats
        self.d['hitpoints'] = int(round((self.d['strength'] +
            self.d['constitution']) / 2.0))
        self.d['willpower'] = self.d['power']
        self.d['sanity'] = self.d['power'] * 5
        self.d['breaking point'] = self.d['power'] * 4

        ## Default Skills
        self.d['accounting'] = 10
        self.d['alertness'] = 20
        self.d['athletics'] = 30
        self.d['bureaucracy'] = 10
        self.d['criminology'] = 10
        self.d['disguise'] = 10
        self.d['dodge'] = 30
        self.d['drive'] = 20
        self.d['firearms'] = 20
        self.d['first aide'] = 10
        self.d['heavy machinery'] = 10
        self.d['history'] = 10
        self.d['humint'] = 10
        self.d['melee weapons'] = 30
        self.d['navigate'] = 10
        self.d['occult'] = 10
        self.d['persuade'] = 20
        self.d['psychotherapy'] = 10
        self.d['ride'] = 10
        self.d['search'] = 20
        self.d['stealth'] = 10
        self.d['survival'] = 10
        self.d['swim'] = 20
        self.d['unarmed combat'] = 40

        if profession == 'Anthropologist':

            self.d['anthropology'] = 50
            self.d['bureaucracy'] = 40 
            self.d['language1'] = 50 
            self.d['language2'] = 30 
            self.d['history'] = 60 
            self.d['occult'] = 40 
            self.d['persuade'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']

            possible = set([
                ('archeology',40),
                ('humint',50),
                ('navigate',50),
                ('ride',50),
                ('search',60),
                ('survival',50),
                ])
            choice1, choice2 = sample(possible,2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

        if profession == 'Historian':

            self.d['archeology'] = 50
            self.d['bureaucracy'] = 40 
            self.d['language1'] = 50 
            self.d['language2'] = 30 
            self.d['history'] = 60 
            self.d['occult'] = 40 
            self.d['persuade'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma'] 

            possible = set([
                ('anthropology',40),
                ('humint',50),
                ('navigate',50),
                ('ride',50),
                ('search',60),
                ('survival',50),
                ])
            choice1, choice2 = sample(possible,2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

        if profession == 'Computer Science' or profession == 'Engineer':

            self.d['computer science'] = 60
            self.d['craft1label'] = 'Electrician'
            self.d['craft1value'] = 30
            self.d['craft2label'] = 'Mechanic'
            self.d['craft2value'] = 30
            self.d['craft3label'] = 'Microelectronics'
            self.d['craft3value'] = 40             
            self.d['science1label'] = 'Mathematics'
            self.d['science1value'] = 40
            self.d['sigint'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

            possible = set([
                ('accounting',50),
                ('bureaucracy',50),
                ('craft4value',40),
                ('language1',40),
                ('heavy machinery',50),
                ('law',40),
                ('science3value',40),
                ])
            choice1, choice2, choice3, choice4 = sample(possible,4)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]
            self.d[choice3[0]] = choice3[1]
            self.d[choice4[0]] = choice4[1]
           
        if profession == 'Federal Agent':

            self.d['alertness'] = 50
            self.d['bureaucracy'] = 40
            self.d['criminology'] = 50
            self.d['drive'] = 50
            self.d['firearms'] = 50
            self.d['forensics'] = 30
            self.d['humint'] = 60
            self.d['law'] = 30                
            self.d['persuade'] = 50  
            self.d['search'] = 50  
            self.d['unarmed combat'] = 60
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

            possible = set([
                ('accounting',60),
                ('computer science',50),
                ('language1',50),
                ('heavy weapons',50),
                ('pharmacy',50),
                ])
            choice1 = sample(possible,1)[0]
            self.d[choice1[0]] = choice1[1]

        if profession == 'Physician':

            self.d['bureaucracy'] = 50
            self.d['first aide'] = 60
            self.d['medicine'] = 60
            self.d['persuade'] = 40
            self.d['pharmacy'] = 50
            self.d['science1label'] = 'Biology'
            self.d['science1value'] = 60
            self.d['search'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

            possible = set([
                ('forensics',50),
                ('psychotherapy',60),
                ('science2value',50),
                ('surgery',50),
                ])
            choice1, choice2 = sample(possible,2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

        if profession == 'Scientist':

            self.d['bureaucracy'] = 40
            self.d['computer science'] = 40
            self.d['science1value'] = 60
            self.d['science2value'] = 50
            self.d['science3value'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']

            possible = set([
                ('accounting',50),
                ('craft1value',40),
                ('language1',40),
                ('forensics',40),
                ('law',40),
                ('pharmacy',40),
                ])
            choice1, choice2, choice3 = sample(possible,3)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]     
            self.d[choice3[0]] = choice3[1]   

        if profession == 'Special Operator':

            self.d['alertness'] = 60
            self.d['athletics'] = 60
            self.d['demolitions'] = 40
            self.d['firearms'] = 60
            self.d['heavy weapons'] = 50
            self.d['melee weapons'] = 50
            self.d['military science'] = 60
            self.d['navigate'] = 50
            self.d['stealth'] = 50
            self.d['survival'] = 50
            self.d['swim'] = 50
            self.d['unarmed combat'] = 60
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']

        ## bonus points

        possible = set([
            'accounting',
            'alertness',
            'anthropology',
            'archeology',
            'art',
            'artillery',
            'athletics',
            'bureaucracy',
            'computer science',
            'craft1value',
            'criminology',
            'demolitions',
            'disguise',
            'dodge',
            'drive',
            'firearms',
            'first aide',
            'forensics',
            'heavy machinery',
            'heavy weapons',
            'history',
            'humint',
            'law',
            'medicine',
            'melee weapons',
            'military science',
            'navigate',
            'occult',
            'persuade',
            'pharmacy',
            'pilot',
            'psychotherapy',
            'ride',
            'science1value',
            'search',
            'sigint',
            'stealth',
            'surgery',
            'survival',
            'swim',
            'unarmed combat',
            'language1',
        ])

        bonus_skills = sample(possible,8)
        for skill in bonus_skills:
            boost = self.d.get(skill,0) + 20
            if boost > 80:
                boost = 80
            self.d[skill] = boost

class Need2KnowPDF(object):

    ## Location of form fields in Points (1/72 inch). 0,0 is bottom-left

    field_xy = {
        ## Personal Data
        'name':(100,693),
        'profession':(368,693),
        'nationality':(368,665),
        'age':(210,640),
        'birthday':(225,640),
        'male':(121,639),
        'female':(99,639),

        ## Statistical Data
        'strength':(164,604),
        'constitution':(164,586),
        'dexterity':(164,568),
        'intelligence':(164,550),
        'power':(164,532),
        'charisma':(164,514),
        'hitpoints':(223,482),
        'willpower':(223,464),
        'sanity':(223,446),
        'breaking point':(223,428),
        'bond1':(543,604),
        'bond2':(543,586),
        'bond3':(543,568),
        'bond4':(543,550),

        ## Applicable Skill Sets
        'accounting':(226,361),
        'alertness':(226,343),
        'anthropology':(226,325),
        'archeology':(226,307),
        'art':(226,289),
        'artillery':(226,253),
        'athletics':(226,235),
        'bureaucracy':(226,217),
        'computer science':(226,200),
        'craft1label':(118,185),
        'craft1value':(226,185),
        'craft2label':(118,177),
        'craft2value':(226,177),
        'craft3label':(118,169),
        'craft3value':(226,169),
        'craft4label':(118,161),
        'craft4value':(226,161),
        'criminology':(226,145),
        'demolitions':(226,127),
        'disguise':(226,109),
        'dodge':(226,91),
        'drive':(226,73),
        'firearms':(226,54),
        'first aide':(388,361),
        'forensics':(388,343),
        'heavy machinery':(388,325),
        'heavy weapons':(388,307),
        'history':(388,289),
        'humint':(388,270),
        'law':(388,253),
        'medicine':(388,235),
        'melee weapons':(388,217),
        'military science':(388,199),
        'navigate':(388,163),
        'occult':(388,145),
        'persuade':(388,127),
        'pharmacy':(388,109),
        'pilot':(388,91),
        'psychotherapy':(388,54),
        'ride':(548,361),
        'science1label':(470,347),
        'science1value':(548,347),
        'science2label':(470,340),
        'science2value':(548,340),
        'science3label':(470,333),
        'science3value':(548,333),
        'science4label':(470,326),
        'science4value':(548,326),
        'search':(548,307),
        'sigint':(548,289),
        'stealth':(548,270),
        'surgery':(548,253),
        'survival':(548,235),
        'swim':(548,217),
        'unarmed combat':(548,200),
        'unnatural':(548,181),
        'language1':(548,145),
        'language2':(548,127),
        'language3':(548,109),
        'skill1':(548,91),
        'skill2':(548,73),
        'skill3':(548,54),
    }

    ## Fields that also get a multiplier
    x5_stats = ['strength','constitution','dexterity','intelligence',
            'power','charisma']

    def __init__(self, width=612, height=792):
        self.c = canvas.Canvas('random_delta_green_characters.pdf')
        self.c.setPageSize((width, height))

    def save_pdf(self):
        self.c.save()

    def font_color(self, r,g,b):
        self.c.setFillColorRGB(r,g,b)

    def draw_string(self, x, y, text):
        self.c.drawString(x,y,str(text))
 
    def fill_field(self,field,value):
        x,y = self.field_xy[field]
        self.c.drawString(x,y,str(value))

        if field in self.x5_stats:
            self.draw_string(x+36, y,str(value * 5))

    def add_page(self, d):
        ## Add background.  ReportLab will cache it for repeat
        self.c.setFont(DEFAULT_FONT,11)
        self.font_color(*TEXT_COLOR)
        self.c.drawImage('data/dg_print.png',0,0,612,792)

        for key in d:
            self.fill_field(key,d[key])

        ## Tell ReportLab we're done with current page
        self.c.showPage()

# Generating characters
num_char_per_class = 8
classes =  ['Anthropologist', 'Computer Science' 'Engineer', 'Federal Agent',
        'Historian', 'Physician', 'Scientist', 'Special Operator']

p = Need2KnowPDF()

for the_class in classes:
    for x in range(num_char_per_class):
        c=Need2KnowCharacter(gender='male',profession=the_class)
        p.add_page(c.d)
        c=Need2KnowCharacter(gender='female',profession=the_class)
        p.add_page(c.d)

p.save_pdf()
