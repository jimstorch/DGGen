#!/usr/bin/env python3

import csv
import datetime
import json
import logging
import optparse
import os
import sys
import warnings
from itertools import islice, cycle
from random import randint, shuffle, choice, sample

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

script_name = os.path.basename(sys.argv[0])
usage = script_name + ' [options] args'
description = '''
Generate characters for the Delta Green pen-and-paper roleplaying game from Arc Dream Publishing.
'''
__version__ = "1.0"

logger = logging.getLogger(script_name)

TEXT_COLOR = (0, .1, .5)
DEFAULT_FONT = 'Special Elite'

MONTHS = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

# Read names and places
with open('data/boys1986.txt') as f:
    MALES = f.read().splitlines()

with open('data/girls1986.txt') as f:
    FEMALES = f.read().splitlines()

with open('data/surnames.txt') as f:
    SURNAMES = f.read().splitlines()

with open('data/towns.txt') as f:
    TOWNS = f.read().splitlines()

with open('data/professions.json') as f:
    PROFESSIONS = json.load(f)

DISTINGUISHING = {}
with open('data/distinguishing-features.csv') as distinguishing:
    for row in csv.DictReader(distinguishing):
        for value in range(int(row['from']), int(row['to']) + 1):
            DISTINGUISHING.setdefault(
                (row['statistic'], value), []).append(row['distinguishing'])


def main(*argv):
    options, script, args, help = get_options(argv)
    init_logger(options.verbosity)
    logger.debug(options)

    p = Need2KnowPDF(options.output, PROFESSIONS)
    for profession, profession_options in PROFESSIONS.items():
        p.bookmark(profession)
        for sex in islice(cycle(['female', 'male']), profession_options['number_to_generate']):
            c = Need2KnowCharacter(sex=sex, profession=profession, profession_options=profession_options)
            p.add_page(c.d)
    p.save_pdf()
    logger.info("Wrote %s", options.output)


class Need2KnowCharacter(object):
    statpools = [
        [13, 13, 12, 12, 11, 11],
        [15, 14, 12, 11, 10, 10],
        [17, 14, 13, 10, 10, 8],
    ]

    DEFAULT_SKILLS = {
        'accounting': 10,
        'alertness': 20,
        'athletics': 30,
        'bureaucracy': 10,
        'criminology': 10,
        'disguise': 10,
        'dodge': 30,
        'drive': 20,
        'firearms': 20,
        'first aide': 10,
        'heavy machinery': 10,
        'history': 10,
        'humint': 10,
        'melee weapons': 30,
        'navigate': 10,
        'occult': 10,
        'persuade': 20,
        'psychotherapy': 10,
        'ride': 10,
        'search': 20,
        'stealth': 10,
        'survival': 10,
        'swim': 20,
        'unarmed combat': 40,
    }

    BONUS = [
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
    ]

    def __init__(self, sex, profession, profession_options):

        # Hold all dictionary
        self.d = {}

        if sex == 'male':
            self.d['male'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(MALES)
        else:
            self.d['female'] = 'X'
            self.d['name'] = choice(SURNAMES).upper() + ', ' + choice(FEMALES)
        self.d['profession'] = profession
        self.d['nationality'] = '(U.S.A.) ' + choice(TOWNS)
        self.d['age'] = '%d    (%s %d)' % (randint(24, 55), choice(MONTHS),
            (randint(1, 28)))

        # Stats
        rolled = [[sum(sorted([randint(1, 6) for _ in range(4)])[1:]) for _ in range(6)]]
        pool = choice(self.statpools + rolled)
        shuffle(pool)
        self.d['strength'] = pool[0]
        self.d['constitution'] = pool[1]
        self.d['dexterity'] = pool[2]
        self.d['intelligence'] = pool[3]
        self.d['power'] = pool[4]
        self.d['charisma'] = pool[5]

        # Derived attributes
        self.d['hitpoints'] = int(round((self.d['strength'] +
                                         self.d['constitution']) / 2.0))
        self.d['willpower'] = self.d['power']
        self.d['sanity'] = self.d['power'] * 5
        self.d['breaking point'] = self.d['power'] * 4
        self.d['damage bonus'] = 'DB=%d' % (((self.d['strength'] - 1) >> 2) - 2)

        # Default skills
        self.d.update(self.DEFAULT_SKILLS)

        # Professional skills
        self.d.update(profession_options['skills']['fixed'])
        for skill, score in sample(profession_options['skills']['possible'].items(),
                                   profession_options['skills']['possible-count']):
            self.d[skill] = score
        for i in range(profession_options['bonds']):
            self.d[f'bond{i}'] = self.d['charisma']

        # Bonus skills
        bonus_skills = sample(self.BONUS, 8)
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
        'bond0': (512, 604),
        'bond1': (512, 586),
        'bond2': (512, 568),
        'bond3': (512, 550),

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

    def __init__(self, filename='out.pdf', professions=None):
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
        self.generate_toc(professions)

    def generate_toc(self, professions):
        """If we're passed an optional list of professions,
        build a clickable Table of Contents on page 1"""
        if professions:
            self.bookmark('Table of Contents')
            self.c.setFillColorRGB(0, 0, 0)
            self.c.setFont("OCRA", 10)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            self.c.drawString(150, 712, 'DGGEN DTG ' + now)
            self.c.drawString(150, 700, 'CLASSIFIED/DG/NTK//')
            self.c.drawString(150, 688, 'SUBJ ROSTER/ACTIVE/NOCELL/CONUS//')
            top = 650
            pagenum = 2
            for count, (profession, profession_options) in enumerate(professions.items()):
                chapter = '{:.<40}'.format(profession) + '{:.>4}'.format(pagenum)
                self.c.drawString(150, top - self.line_drop(count), chapter)
                self.c.linkAbsolute(profession, profession,
                                    (145, (top - 6) - self.line_drop(count), 470, (top + 18) - self.line_drop(count)))
                pagenum += profession_options['number_to_generate']
            chapter = '{:.<40}'.format('Blank Character Sheet Second Page') + '{:.>4}'.format(
                pagenum + profession_options['number_to_generate'])
            self.c.drawString(150, top - self.line_drop(pagenum), chapter)
            self.c.linkAbsolute('Back Page', 'Back Page',
                                (145, (top - 6) - self.line_drop(pagenum), 470, (top + 18) - self.line_drop(pagenum)))
            self.c.showPage()

    @staticmethod
    def line_drop(count, linesize=22):
        return count * linesize

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

    @staticmethod
    def distinguishing(field, value):
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


def get_options(argv):
    """Get options and arguments from argv string."""
    parser = optparse.OptionParser(usage=usage, version=__version__)
    parser.description = description
    parser.add_option("-v", "--verbosity", action="count", default=0,
                      help="Specify up to three times to increase verbosity, i.e. -v to see warnings, -vv for "
                           "information messages, or -vvv for debug messages.")
    parser.add_option("-o", "--output", action="store",
                      default=f'DeltaGreenPregen-{datetime.datetime.now() :%Y-%m-%d-%H:%M}.pdf',
                      help="Output PDF file. Defaults to %default.")

    options, args = parser.parse_args(list(argv))
    script, args = args[0], args[1:]
    return options, script, args, parser.format_help()


def init_logger(verbosity, stream=sys.stdout):
    """Initialize logger and warnings according to verbosity argument.
    Verbosity levels of 0-3 supported."""
    is_not_debug = verbosity <= 2
    level = [logging.ERROR, logging.WARNING, logging.INFO][verbosity] if is_not_debug else logging.DEBUG
    log_format = '%(message)s' if is_not_debug \
        else '%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s'
    logging.basicConfig(level=level, format=log_format, stream=stream)
    if is_not_debug: warnings.filterwarnings('ignore')


if __name__ == '__main__':
    sys.exit(main(*sys.argv))
