#!/usr/bin/env python3

import csv
import datetime
from random import randint, shuffle, choice, sample
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

TEXT_COLOR = (0, .1, .5)
DEFAULT_FONT = 'Special Elite'

MONTHS = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

PROFESSIONS = [
    'Anthropologist',
    'Business Executive',
    'Computer Science',
    'Criminal',
    'Engineer',
    'Federal Agent',
    'Firefighter',
    'Foreign Service Officer',
    'Historian',
    'Intelligence Analyst',
    'Intelligence Case Officer',
    'Lawyer',
    'Marine',
    'Media Specialist',
    'Nurse',
    'Paramedic',
    'Physician',
    'Pilot',
    'Police Officer',
    'Program Manager',
    'Sailor',
    'Scientist',
    'Soldier',
    'Special Operator',
]

# Read names and places
with open('data/boys1986.txt') as f:
    MALES = f.read().splitlines()

with open('data/girls1986.txt') as f:
    FEMALES = f.read().splitlines()

with open('data/surnames.txt') as f:
    SURNAMES = f.read().splitlines()

with open('data/towns.txt') as f:
    TOWNS = f.read().splitlines()

DISTINGUISHING = {}
with open('data/distinguishing-features.csv') as distinguishing:
    for row in csv.DictReader(distinguishing):
        for value in range(int(row['from']), int(row['to']) + 1):
            DISTINGUISHING.setdefault(
                (row['statistic'], value), []).append(row['distinguishing'])

class Need2KnowCharacter(object):

    statpools = (
        [13, 13, 12, 12, 11, 11],
        [15, 14, 12, 11, 10, 10],
        [17, 14, 13, 10, 10, 8],
    )

    def __init__(self, gender='male', profession=''):

        # Hold all dictionary
        self.d = {}

        if gender == 'male':
            self.d['male'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(MALES)
        else:
            self.d['female'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(FEMALES)
        self.d['profession'] = profession
        self.d['nationality'] = '(U.S.A.) ' + choice(TOWNS)
        self.d['age'] = '%d    (%s %d)' % (randint(24, 55), choice(MONTHS),
            (randint(1, 28)))

        # Spend the Point Pool
        pool = choice(self.statpools)
        shuffle(pool)
        self.d['strength'] = pool[0]
        self.d['constitution'] = pool[1]
        self.d['dexterity'] = pool[2]
        self.d['intelligence'] = pool[3]
        self.d['power'] = pool[4]
        self.d['charisma'] = pool[5]

        # Derived Stats
        self.d['hitpoints'] = int(round((self.d['strength'] +
                                         self.d['constitution']) / 2.0))
        self.d['willpower'] = self.d['power']
        self.d['sanity'] = self.d['power'] * 5
        self.d['breaking point'] = self.d['power'] * 4
        self.d['damage bonus'] = 'DB=%d' % (((self.d['strength'] - 1) >> 2 ) - 2)
        # Default Skills
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
                ('archeology', 40),
                ('humint', 50),
                ('navigate', 50),
                ('ride', 50),
                ('search', 60),
                ('survival', 50),
            ])
            choice1, choice2 = sample(possible, 2)
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
                ('anthropology', 40),
                ('humint', 50),
                ('navigate', 50),
                ('ride', 50),
                ('search', 60),
                ('survival', 50),
            ])
            choice1, choice2 = sample(possible, 2)
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
                ('accounting', 50),
                ('bureaucracy', 50),
                ('craft4value', 40),
                ('language1', 40),
                ('heavy machinery', 50),
                ('law', 40),
                ('science3value', 40),
            ])
            choice1, choice2, choice3, choice4 = sample(possible, 4)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]
            self.d[choice3[0]] = choice3[1]
            self.d[choice4[0]] = choice4[1]

        if profession == 'Criminal':

            self.d['alertness'] = 50
            self.d['criminology'] = 60
            self.d['dodge'] = 40
            self.d['drive'] = 50
            self.d['firearms'] = 40
            self.d['law'] = 40
            self.d['melee weapons'] = 40
            self.d['persuade'] = 50
            self.d['stealth'] = 50
            self.d['unarmed combat'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['craft1label'] = 'locksmithing'
            possible = set([
                ('craft1value', 40),
                ('demolitions', 40),
                ('disguise', 50),
                ('language1', 40),
                ('humint', 50),
                ('navigate', 50),
                ('occult', 50),
                ('pharmacy', 40),
            ])
            choice1, choice2 = sample(possible, 2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

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
                ('accounting', 60),
                ('computer science', 50),
                ('language1', 50),
                ('heavy weapons', 50),
                ('pharmacy', 50),
            ])
            choice1 = sample(possible, 1)[0]
            self.d[choice1[0]] = choice1[1]

        if profession == 'Firefighter':

            self.d['alertness'] = 50
            self.d['athletics'] = 60
            self.d['craft1label'] = 'Electrician'
            self.d['craft1value'] = 40
            self.d['craft2label'] = 'Mechanic'
            self.d['craft2value'] = 40
            self.d['demolitions'] = 50
            self.d['drive'] = 50
            self.d['first aide'] = 50
            self.d['forensics'] = 40
            self.d['heavy machinery'] = 50
            self.d['navigate'] = 50
            self.d['search'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

        if profession == 'Foreign Service Officer':

            self.d['accounting'] = 40
            self.d['anthropology'] = 40
            self.d['bureaucracy'] = 60
            self.d['language1'] = 50
            self.d['language2'] = 50
            self.d['language3'] = 40
            self.d['history'] = 40
            self.d['humint'] = 50
            self.d['law'] = 40
            self.d['persuade'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

        if profession == 'Intelligence Analyst':

            self.d['anthropology'] = 40
            self.d['bureaucracy'] = 50
            self.d['computer science'] = 40
            self.d['criminology'] = 40
            self.d['language1'] = 50
            self.d['language2'] = 50
            self.d['language3'] = 40
            self.d['history'] = 40
            self.d['humint'] = 50
            self.d['sigint'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']

        if profession == 'Intelligence Case Officer':

            self.d['alertness'] = 50
            self.d['bureaucracy'] = 40
            self.d['criminology'] = 50
            self.d['disguise'] = 50
            self.d['drive'] = 40
            self.d['firearms'] = 40
            self.d['language1'] = 50
            self.d['language2'] = 40
            self.d['humint'] = 60
            self.d['sigint'] = 40
            self.d['stealth'] = 50
            self.d['unarmed combat'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']

        if profession == 'Lawyer' or profession == 'Business Executive':

            self.d['accounting'] = 50
            self.d['bureaucracy'] = 50
            self.d['humint'] = 40
            self.d['persuade'] = 60
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']
            possible = set([
                ('computer science', 50),
                ('criminology', 60),
                ('language1', 50),
                ('law', 50),
                ('pharmacy', 50),
            ])
            choice1, choice2, choice3, choice4 = sample(possible, 4)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]
            self.d[choice3[0]] = choice3[1]
            self.d[choice4[0]] = choice4[1]

        if profession == 'Media Specialist':

            self.d['art1'] = 60
            self.d['history'] = 40
            self.d['humint'] = 40
            self.d['persuade'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']
            possible = set([
                ('anthropology', 40),
                ('archeology', 40),
                ('art2', 40),
                ('bureaucracy', 50),
                ('computer science', 40),
                ('criminology', 50),
                ('language1', 40),
                ('law', 40),
                ('military science', 40),
                ('occult', 50),
                ('science1value', 40),
            ])
            choice1, choice2, choice3, choice4, choice5 = sample(possible, 5)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]
            self.d[choice3[0]] = choice3[1]
            self.d[choice4[0]] = choice4[1]
            self.d[choice5[0]] = choice5[1]

        if profession == 'Nurse' or profession == 'Paramedic':

            self.d['alertness'] = 40
            self.d['bureaucracy'] = 40
            self.d['first aide'] = 60
            self.d['humint'] = 40
            self.d['medicine'] = 40
            self.d['persuade'] = 40
            self.d['pharmacy'] = 40
            self.d['science1label'] = 'Biology'
            self.d['science1value'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']
            possible = set([
                ('drive', 60),
                ('forensics', 40),
                ('navigate', 50),
                ('psychotherapy', 50),
                ('search', 60),
            ])
            choice1, choice2 = sample(possible, 2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

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
                ('forensics', 50),
                ('psychotherapy', 60),
                ('science2value', 50),
                ('surgery', 50),
            ])
            choice1, choice2 = sample(possible, 2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

        if profession == 'Pilot' or profession == 'Sailor':

            self.d['alertness'] = 60
            self.d['bureaucracy'] = 30
            self.d['craft1label'] = 'Electrician'
            self.d['craft1value'] = 40
            self.d['craft2label'] = 'Mechanic'
            self.d['craft2value'] = 40
            self.d['navigate'] = 50
            self.d['pilot1'] = 60
            self.d['science1label'] = 'Meteorology'
            self.d['science1value'] = 40
            self.d['swim'] = 40
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            possible = set([
                ('language1', 50),
                ('pilot2', 50),
                ('heavy weapons', 50),
                ('military science', 50),
            ])
            choice1, choice2 = sample(possible, 2)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]

        if profession == 'Police Officer':

            self.d['alertness'] = 60
            self.d['bureaucracy'] = 40
            self.d['criminology'] = 50
            self.d['drive'] = 50
            self.d['firearms'] = 40
            self.d['first aide'] = 30
            self.d['humint'] = 50
            self.d['law'] = 30
            self.d['melee weapons'] = 50
            self.d['navigate'] = 40
            self.d['persuade'] = 40
            self.d['search'] = 50
            self.d['unarmed combat'] = 60
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            possible = set([
                ('forensics', 50),
                ('heavy machinery', 60),
                ('heavy weapons', 50),
                ('ride', 60),
            ])
            choice1 = sample(possible, 1)[0]
            self.d[choice1[0]] = choice1[1]

        if profession == 'Program Manager':

            self.d['accounting'] = 60
            self.d['bureaucracy'] = 60
            self.d['computer science'] = 50
            self.d['criminology'] = 30
            self.d['language1'] = 50
            self.d['history'] = 40
            self.d['law'] = 40
            self.d['persuade'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']
            possible = set([
                ('anthropology', 30),
                ('art1', 30),
                ('craft1value', 30),
                ('science1value', 30),
            ])
            choice1 = sample(possible, 1)[0]
            self.d[choice1[0]] = choice1[1]

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
                ('accounting', 50),
                ('craft1value', 40),
                ('language1', 40),
                ('forensics', 40),
                ('law', 40),
                ('pharmacy', 40),
            ])
            choice1, choice2, choice3 = sample(possible, 3)
            self.d[choice1[0]] = choice1[1]
            self.d[choice2[0]] = choice2[1]
            self.d[choice3[0]] = choice3[1]

        if profession == 'Soldier' or profession == 'Marine':

            self.d['alertness'] = 50
            self.d['athletics'] = 50
            self.d['bureaucracy'] = 30
            self.d['drive'] = 40
            self.d['firearms'] = 40
            self.d['first aide'] = 40
            self.d['military science'] = 40
            self.d['milsci label'] = 'Land'
            self.d['navigate'] = 40
            self.d['persuade'] = 30
            self.d['unarmed combat'] = 50
            self.d['bond1'] = self.d['charisma']
            self.d['bond2'] = self.d['charisma']
            self.d['bond3'] = self.d['charisma']
            self.d['bond4'] = self.d['charisma']
            possible = set([
                ('artillery', 40),
                ('computer science', 40),
                ('demolitions', 40),
                ('language1', 40),
                ('heavy machinery', 50),
                ('heavy weapons', 40),
                ('search', 60),
                ('sigint', 40),
                ('swim', 60),
            ])
            choice1, choice2, choice3 = sample(possible, 3)
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

        # bonus points

        possible = set([
            'accounting',
            'alertness',
            'anthropology',
            'archeology',
            'art1',
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
            'pilot1',
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
        bonus_skills = sample(possible, 8)
        for skill in bonus_skills:
            boost = self.d.get(skill, 0) + 20
            if boost > 80:
                boost = 80
            self.d[skill] = boost


class Need2KnowPDF(object):

    # Location of form fields in Points (1/72 inch). 0,0 is bottom-left
    field_xy = {
        # Personal Data
        'name': (75, 693),
        'profession': (343, 693),
        'nationality': (343, 665),
        'age': (185, 640),
        'birthday': (200, 640),
        'male': (98, 639),
        'female': (76, 639),

        # Statistical Data
        'strength': (136, 604),
        'damage bonus': (555, 200),
        'constitution': (136, 586),
        'dexterity': (136, 568),
        'intelligence': (136, 550),
        'power': (136, 532),
        'charisma': (136, 514),
        'hitpoints': (195, 482),
        'willpower': (195, 464),
        'sanity': (195, 446),
        'breaking point': (195, 428),
        'bond1': (512, 604),
        'bond2': (512, 586),
        'bond3': (512, 568),
        'bond4': (512, 550),

        # Applicable Skill Sets
        'accounting': (200, 361),
        'alertness': (200, 343),
        'anthropology': (200, 325),
        'archeology': (200, 307),
        'art1': (200, 289),
        'art2': (200, 281),
        'artillery': (200, 253),
        'athletics': (200, 235),
        'bureaucracy': (200, 217),
        'computer science': (200, 200),
        'craft1label': (90, 185),
        'craft1value': (200, 185),
        'craft2label': (90, 177),
        'craft2value': (200, 177),
        'craft3label': (90, 169),
        'craft3value': (200, 169),
        'craft4label': (90, 161),
        'craft4value': (200, 161),
        'criminology': (200, 145),
        'demolitions': (200, 127),
        'disguise': (200, 109),
        'dodge': (200, 91),
        'drive': (200, 73),
        'firearms': (200, 54),
        'first aide': (361, 361),
        'forensics': (361, 343),
        'heavy machinery': (361, 325),
        'heavy weapons': (361, 307),
        'history': (361, 289),
        'humint': (361, 270),
        'law': (361, 253),
        'medicine': (361, 235),
        'melee weapons': (361, 217),
        'military science': (361, 199),
        'milsci label': (327, 199),
        'navigate': (361, 163),
        'occult': (361, 145),
        'persuade': (361, 127),
        'pharmacy': (361, 109),
        'pilot1': (361, 91),
        'pilot2': (361, 83),
        'psychotherapy': (361, 54),
        'ride': (521, 361),
        'science1label': (442, 347),
        'science1value': (521, 347),
        'science2label': (442, 340),
        'science2value': (521, 340),
        'science3label': (442, 333),
        'science3value': (521, 333),
        'science4label': (442, 326),
        'science4value': (521, 326),
        'search': (521, 307),
        'sigint': (521, 289),
        'stealth': (521, 270),
        'surgery': (521, 253),
        'survival': (521, 235),
        'swim': (521, 217),
        'unarmed combat': (521, 200),
        'unnatural': (521, 181),
        'language1': (521, 145),
        'language2': (521, 127),
        'language3': (521, 109),
        'skill1': (521, 91),
        'skill2': (521, 73),
        'skill3': (521, 54),
    }

    # Fields that also get a multiplier
    x5_stats = ['strength', 'constitution', 'dexterity', 'intelligence',
                'power', 'charisma']

    def __init__(self, filename='out.pdf', profession_list=None, count_each=None):
        self.filename = filename
        self.c = canvas.Canvas(self.filename)
        # Set US Letter in points
        self.c.setPageSize((612, 792))
        self.c.setAuthor('https://github.com/jimstorch/DGGen')
        self.c.setTitle('Delta Green Agent Roster')
        self.c.setSubject('Pre-generated characters for the Delta Green RPG')
        # Register Custom Fonts
        pdfmetrics.registerFont(TTFont('Special Elite', 'data/SpecialElite.ttf'))
        pdfmetrics.registerFont(TTFont('OCRA', 'data/OCRA.ttf'))
        # If we're passed an optional list of professions
        # build a clickable Table of Contents on page 1
        if profession_list != None and count_each != None:
            self.bookmark('Table of Contents')
            self.c.setFillColorRGB(0, 0, 0)
            self.c.setFont("OCRA", 10)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            self.c.drawString(150, 712, 'DGGEN DTG ' + now)
            self.c.drawString(150, 700, 'CLASSIFIED/DG/NTK//')
            self.c.drawString(150, 688, 'SUBJ ROSTER/ACTIVE/NOCELL/CONUS//')
            top = 650
            count = 0
            for profession in profession_list:
                pagenum = (count * count_each) + 2
                chapter = '{:.<40}'.format(
                    profession) + '{:.>4}'.format(pagenum)
                self.c.drawString(150, top - count * 22, chapter)
                self.c.linkAbsolute(profession, profession,
                    (145, (top - 6) - (count * 22), 470, (top + 18) - (count * 22)))
                count += 1
            chapter = '{:.<40}'.format('Blank Character Sheet Second Page'
                ) + '{:.>4}'.format(pagenum + count_each)
            self.c.drawString(150, top - count * 22, chapter)
            self.c.linkAbsolute('Back Page', 'Back Page',
                (145, (top - 6) - (count * 22), 470, (top + 18) - (count * 22)))
            self.c.showPage()

    def bookmark(self, text):
        self.c.bookmarkPage(text)
        self.c.addOutlineEntry(text, text)

    def font_color(self, r, g, b):
        self.c.setFillColorRGB(r, g, b)

    def draw_string(self, x, y, text):
        self.c.drawString(x, y, str(text))

    def fill_field(self, field, value):
        x, y = self.field_xy[field]
        self.c.drawString(x, y, str(value))

        if field in self.x5_stats:
            self.draw_string(x + 36, y, str(value * 5))
            self.draw_string(x + 72, y, self.distinguishing(field, value))

    def distinguishing(self, field, value):
        return choice(DISTINGUISHING.get((field, value), [""]))

    def add_page(self, d):
        # Add background.  ReportLab will cache it for repeat
        self.c.setFont(DEFAULT_FONT, 11)
        self.font_color(*TEXT_COLOR)
        self.c.drawImage(
            'data/Character Sheet NO BACKGROUND FRONT.jpg', 0, 0, 612, 792)

        for key in d:
            self.fill_field(key, d[key])

        # Tell ReportLab we're done with current page
        self.c.showPage()

    def save_pdf(self):
        self.bookmark('Back Page')
        self.c.drawImage(
            'data/Character Sheet NO BACKGROUND BACK.jpg', 0, 0, 612, 792)
        self.c.showPage()
        self.c.save()


if __name__ == '__main__':

    p = Need2KnowPDF('DeltaGreenPregen.pdf', PROFESSIONS, 40)
    for profession in PROFESSIONS:
        p.bookmark(profession)
        for x in range(20):
            c = Need2KnowCharacter(gender='female', profession=profession)
            p.add_page(c.d)
            c = Need2KnowCharacter(gender='male', profession=profession)
            p.add_page(c.d)
    p.save_pdf()
