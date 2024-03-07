#!/usr/bin/env python3
import argparse
import csv
import json
import logging
import os
import sys
import warnings
from collections import defaultdict
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from itertools import islice, cycle, chain
from math import floor
from random import randint, shuffle, choice, sample, choices
from textwrap import shorten, wrap
from typing import List, Any, Dict, Tuple

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

script_name = os.path.basename(sys.argv[0])
description = """
Generate characters for the Delta Green pen-and-paper roleplaying game from Arc Dream Publishing.
"""
__version__ = "1.4"

logger = logging.getLogger(script_name)

TEXT_COLOR = (0, 0.1, 0.5)
DEFAULT_FONT = "Special Elite"

MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
SUGGESTED_BONUS_CHANCE = 75


def main():
    options = get_options()
    init_logger(options.verbosity)
    logger.debug(options)

    data = load_data(options)

    pages_per_sheet = 2 if options.equip else 1
    professions = [data.professions[options.type]] if options.type else data.professions.values()
    p = Need2KnowPDF(options.output, professions, pages_per_sheet=pages_per_sheet)

    ## TODO: Maybe an option to skip cover, especially for single sheets
    p.add_cover()
    ## Moved TOC here instead of Need2KnowPDF.init() so cover could precede it
    if len(professions) > 1:
        p.generate_toc(professions, pages_per_sheet)

    for profession in professions:
        label = generate_label(profession)
        p.bookmark(label)
        for sex in islice(
            cycle(["female", "male"]), options.count or profession["number_to_generate"]
        ):
            c = Need2KnowCharacter(
                data=data,
                sex=sex,
                profession=profession,
                label_override=options.label,
                employer_override=options.employer,
                min_age=options.min_age,
                max_age=options.max_age,
                veterancy=options.veterancy,
                damaged=options.damaged,
            )
            if options.equip:
                c.equip(profession.get("equipment-kit", None))
            c.print_footnotes()

            p.add_page(c.d)
            if pages_per_sheet >= 2:
                p.add_page_2(c.e)

    p.save_pdf()
    logger.info("Wrote %s", options.output)


class Need2KnowCharacter(object):
    PHYSICAL_STATS = ["strength", "constitution", "dexterity"]
    STATS = PHYSICAL_STATS + ["intelligence", "power", "charisma"]

    stat_pools = [
        [13, 13, 12, 12, 11, 11],
        [15, 14, 12, 11, 10, 10],
        [17, 14, 13, 10, 10, 8],
    ]

    DEFAULT_SKILLS = {
        "accounting": 10,
        "alertness": 20,
        "athletics": 30,
        "bureaucracy": 10,
        "criminology": 10,
        "disguise": 10,
        "dodge": 30,
        "drive": 20,
        "firearms": 20,
        "first aid": 10,
        "heavy machinery": 10,
        "history": 10,
        "humint": 10,
        "melee weapons": 30,
        "navigate": 10,
        "occult": 10,
        "persuade": 20,
        "psychotherapy": 10,
        "ride": 10,
        "search": 20,
        "stealth": 10,
        "survival": 10,
        "swim": 20,
        "unarmed combat": 40,
    }

    ALL_BONUS = [
        "accounting",
        "alertness",
        "anthropology",
        "archeology",
        "art1",
        "artillery",
        "athletics",
        "bureaucracy",
        "computer science",
        "craft1value",
        "criminology",
        "demolitions",
        "disguise",
        "dodge",
        "drive",
        "firearms",
        "first aid",
        "forensics",
        "heavy machinery",
        "heavy weapons",
        "history",
        "humint",
        "law",
        "medicine",
        "melee weapons",
        "militaryscience1value",
        "navigate",
        "occult",
        "persuade",
        "pharmacy",
        "pilot1value",
        "psychotherapy",
        "ride",
        "science1value",
        "search",
        "sigint",
        "stealth",
        "surgery",
        "survival",
        "swim",
        "unarmed combat",
        "language1",
    ]

    def __init__(self,
                 data,
                 sex,
                 profession,
                 label_override=None,
                 employer_override=None,
                 min_age=24,
                 max_age=55,
                 veterancy=True,
                 damaged=True,
        ):
        self.data = data
        self.profession = profession
        self.sex = sex

        # Hold all dictionaries
        self.d = {}
        self.e = {}

        self.footnotes = defaultdict(
            iter(
                ["*", "†", "‡", "§", "¶", "**", "††", "‡‡", "§§", "¶¶", "***", "†††", "‡‡‡", "§§§"]
            ).__next__
        )

        self.bonus_skills = []

        self.generate_demographics(label_override, employer_override, min_age, max_age)
        self.generate_stats()
        self.generate_skills()
        if veterancy:
            self.veterancy(damaged)
        self.generate_derived_attributes()

    def generate_demographics(self, label_override, employer_override, min_age, max_age):
        if self.sex == "male":
            self.d["male"] = "X"
            self.d["name"] = (
                choice(self.data.family_names).upper() + ", " + choice(self.data.male_given_names)
            )
        else:
            self.d["female"] = "X"
            self.d["name"] = (
                choice(self.data.family_names).upper() + ", " + choice(self.data.female_given_names)
            )
        self.d["profession"] = label_override or self.profession["label"]
        self.d["employer"] = employer_override or ", ".join(
            e
            for e in [self.profession.get("employer", ""), self.profession.get("division", "")]
            if e
        )
        self.d["nationality"] = "(U.S.A.) " + choice(self.data.towns)
        self.age = randint(min_age, max_age)
        self.d["age"] = "%d    (%s %d)" % (self.age, choice(MONTHS), (randint(1, 28)))

    def generate_stats(self):
        rolled = [[sum(sorted([randint(1, 6) for _ in range(4)])[1:]) for _ in range(6)]]
        pool = choice(self.stat_pools + rolled)
        shuffle(pool)
        for score, stat in zip(pool, self.STATS):
            self.d[stat] = score

    def generate_derived_attributes(self):
        self.d["hitpoints"] = int(round((self.d["strength"] + self.d["constitution"]) / 2.0))
        self.d["willpower"] = self.d["power"]
        self.d["sanity"] = (self.d["power"] * 5) - getattr(self, "san_loss", 0)
        self.d["breaking point"] = self.d["sanity"] - self.d["power"]
        self.damage_bonus = ((self.d["strength"] - 1) >> 2) - 2
        self.d["damage bonus"] = "DB=%d" % self.damage_bonus
        for stat in self.STATS:
            score = self.d[stat]
            self.d[f"{stat}_x5"] = score * 5
            self.d[f"{stat}_distinguishing"] = self.distinguishing(stat, score)
        self.d["violence"] = "  ".join("X" for _ in range(getattr(self, "adapted_to_violence", 0)))
        self.d["helplessness"] = "  ".join("X" for _ in range(getattr(self, "adapted_to_helplessness", 0)))

    def generate_skills(self):
        # Default skills
        self.d.update(self.DEFAULT_SKILLS)

        # Professional skills
        self.d.update(self.profession["skills"]["fixed"])
        for skill, score in sample(
            list(self.profession["skills"].get("possible", {}).items()),
            self.profession["skills"].get("possible-count", 0),
        ):
            self.d[skill] = score
        for i in range(self.profession["bonds"]):
            self.d[f"bond{i}"] = self.d["charisma"]

        # Bonus skills
        self.generate_bonus_skills()

    def generate_bonus_skills(self):
        potential_bonus_skills = [
            s
            for s in self.profession["skills"].get("bonus", [])
            if randint(1, 100) <= SUGGESTED_BONUS_CHANCE
        ] + sample(self.ALL_BONUS, len(self.ALL_BONUS))
        self.apply_bonuses(potential_bonus_skills, 8, 80)

    def apply_bonuses(self, potential_bonus_skills, number_to_boost, max_level):
        bonuses_applied = 0
        while bonuses_applied < number_to_boost:
            skill = potential_bonus_skills.pop(0)
            boosted = self.d.get(skill, 0) + 20
            if boosted <= max_level:
                self.d[skill] = boosted
                bonuses_applied += 1
                self.bonus_skills.append(skill)
                logger.debug("%s, boosted %s to %s", self, skill, boosted)
            else:
                logger.debug(
                    "%s, Skipped boost - %s already at %s", self, skill, self.d.get(skill, 0)
                )

    def veterancy(self, damaged):
        self.veterancy_skill_boosts()
        self.veterancy_stat_losses()
        if damaged:
            self.damaged_veteran_changes()

    @staticmethod
    def skill_checks_at_age(age, earned_at_start=4, start_age=25, halve_rate=10):
        return earned_at_start * (1 / 2 ** ((age - start_age) / halve_rate))

    def veterancy_skill_boosts(self):
        skills_to_check = set(list(self.profession['skills']['fixed'].keys()) +
                              list(self.profession['skills'].get('possible', {}).keys()) +
                              # list(self.DEFAULT_SKILLS.keys()) +
                              self.bonus_skills)
        skill_checks = floor(sum(self.skill_checks_at_age(y) for y in range(25, self.age + 1)))
        for skill in skills_to_check:
            if isinstance(self.d.get(skill, 0), int) and self.d.get(skill, 0) > 0:
                original = self.d[skill]
                for _ in range(skill_checks):
                    current = self.d[skill]
                    roll = randint(1, 100)
                    if roll > current or roll == 100:
                        self.d[skill] += 1
                logger.debug("%s, boosted %s from %s to %s by veterancy", self, skill, original, self.d[skill])

    def veterancy_stat_losses(self):
        losses = 0
        if 40 <= self.age <= 49: losses = 1
        elif 50 <= self.age <= 59: losses = 2
        elif 60 <= self.age <= 69: losses = 4
        elif 70 <= self.age <= 79: losses = 8
        elif 80 <= self.age <= 89: losses = 16
        elif 80 <= self.age: losses = 32
        while losses and not all(self.d[stat] <= 1 for stat in self.PHYSICAL_STATS):
            target = choice(self.PHYSICAL_STATS)
            if self.d[target] > 1:
                self.d[target] -= 1
                losses -= 1
                logger.debug("%s, %s decreased to %s by veterancy", self, target, self.d[target])

    def damaged_veteran_changes(self):
        damage_count = choices(range(5), weights=[80, 10, 5, 4, 1])[0]
        if damage_count:
            damage_methods = sample(
                [self.extreme_violence_changes,
                 self.captivity_or_imprisonment_changes,
                 self.hard_experience_changes,
                 self.things_man_was_not_meant_to_know_changes],
                k=damage_count
            )
            damage = ["Damaged Veteran:"]
            for method in damage_methods:
                method(damage)
            for i, description in enumerate(damage):
                self.e[f"detail{i}"] = description

    def extreme_violence_changes(self, damage):
        damage.append("• Extreme Violence")
        self.d["occult"] += 10
        self.san_loss = getattr(self, "san_loss", 0) + 5
        self.d["charisma"] -= 3
        for i in range(self.profession["bonds"]):
            if f"bond{i}" in self.d:
                self.d[f"bond{i}"] -= 3
        self.adapted_to_violence = 3

    def captivity_or_imprisonment_changes(self, damage):
        damage.append("• Captivity or Imprisonment")
        self.d["occult"] += 10
        self.san_loss = getattr(self, "san_loss", 0) + 5
        self.d["power"] -= 3
        self.adapted_to_helplessness = 3

    def hard_experience_changes(self, damage):
        damage.append("• Hard Experience")
        self.d["occult"] += 10
        potential_bonus_skills = sample(self.ALL_BONUS, len(self.ALL_BONUS))
        self.apply_bonuses(potential_bonus_skills, 5, 90)
        self.san_loss = getattr(self, "san_loss", 0) + 5
        del self.d[f"bond{self.profession['bonds']-1}"]

    def things_man_was_not_meant_to_know_changes(self, damage):
        damage.append("• Things Man Was Not Meant to Know")
        self.d["unnatural"] = self.d.get("unnatural", 0) + 10
        self.d["occult"] += 20
        self.san_loss = getattr(self, "san_loss", 0) + self.d["power"]
        self.d["disorder0"] = "Disorder: " + choice(
            ["Amnesia",
             "Depersonalization",
             "Depression",
             "Dissociative Identity",
             "Fugues",
             "Megalomania",
             "Paranoia",
             "Sleep Disorder",
             ])
    def potential_bonus_skills(self, profession):
        return [
            s
            for s in profession["skills"].get("bonus", [])
            if randint(1, 100) <= SUGGESTED_BONUS_CHANCE
        ] + sample(self.ALL_BONUS, len(self.ALL_BONUS))

    def __str__(self):
        return ", ".join(
            [
                self.d.get(i)
                for i in ("name", "profession", "employer", "department")
                if self.d.get(i)
            ]
        )

    def distinguishing(self, field, value):
        return choice(self.data.distinguishing.get((field, value), [""]))

    def equip(self, kit_name=None):
        weapons = [self.data.weapons["unarmed"]]
        if kit_name:
            kit = self.data.kits[kit_name]
            weapons += self.build_weapon_list(kit["weapons"])

            gear = []
            for item in kit["armour"] + kit["gear"]:
                if item.get("chance", 100) < randint(1, 100):
                    continue
                notes = (
                    (" ".join(self.store_footnote(n) for n in item["notes"]) + " ")
                    if "notes" in item
                    else ""
                )
                text = notes + (self.data.armour[item["type"]] if "type" in item else item["text"])
                gear.append(text)

            wrapped_gear = list(chain(*[wrap(item, 55, subsequent_indent="  ") for item in gear]))
            if len(wrapped_gear) > 22:
                logger.warning("Too much gear - truncated.")
            for i, line in enumerate(wrapped_gear):
                self.e[f"gear{i}"] = line

        if len(weapons) > 7:
            logger.warning("Too many weapons %s - truncated.", weapons)
        for i, weapon in enumerate(weapons[:7]):
            self.equip_weapon(i, weapon)

    def build_weapon_list(self, weapons_to_add):
        result = []
        for weapon_to_add in weapons_to_add:
            if "type" in weapon_to_add:
                weapon = copy(self.data.weapons.get(weapon_to_add["type"], None))
                if weapon:
                    if "notes" in weapon_to_add:
                        weapon["notes"] = weapon_to_add["notes"]
                    result += (
                        [weapon]
                        if "chance" not in weapon_to_add
                        or weapon_to_add["chance"] >= randint(1, 100)
                        else []
                    )
                else:
                    logger.error("Unknown weapon type %s", weapon_to_add["type"])
            elif "one-of" in weapon_to_add:
                result += (self.build_weapon_list([choice(weapon_to_add["one-of"])])
                           if "chance" not in weapon_to_add
                              or weapon_to_add["chance"] >= randint(1, 100)
                           else [])
            elif "both" in weapon_to_add:
                result += self.build_weapon_list(w for w in weapon_to_add["both"])
            else:
                logger.error("Don't understand weapon %r", weapon_to_add)
        return result

    def equip_weapon(self, slot, weapon):
        self.e[f"weapon{slot}"] = shorten(weapon["name"], 15, placeholder="…")
        roll = int(self.d.get(weapon["skill"], 0) + (weapon["bonus"] if "bonus" in weapon else 0))
        self.e[f"weapon{slot}_roll"] = f"{roll}%"
        if "base-range" in weapon:
            self.e[f"weapon{slot}_range"] = weapon["base-range"]
        if "ap" in weapon:
            self.e[f"weapon{slot}_ap"] = f"{weapon['ap']}"
        if "lethality" in weapon:
            lethality = weapon["lethality"]
            lethality_note_indicator = (
                self.store_footnote(lethality["special"]) if "special" in lethality else None
            )
            self.e[f"weapon{slot}_lethality"] = (
                f"{lethality['rating']}%" if lethality["rating"] else ""
            ) + (f" {lethality_note_indicator}" if lethality_note_indicator else "")

        if "ammo" in weapon:
            self.e[f"weapon{slot}_ammo"] = f"{weapon['ammo']}"
        if "kill-radius" in weapon:
            self.e[f"weapon{slot}_kill_radius"] = f"{weapon['kill-radius']}"

        if "notes" in weapon:
            self.e[f"weapon{slot}_note"] = " ".join(self.store_footnote(n) for n in weapon["notes"])

        if "damage" in weapon:
            damage = weapon["damage"]
            damage_note_indicator = (
                self.store_footnote(damage["special"]) if "special" in damage else None
            )

            if "dice" in damage:
                damage_modifier = (damage["modifier"] if "modifier" in damage else 0) + (
                    self.damage_bonus if "db-applies" in damage and damage["db-applies"] else 0
                )
                damage_roll = f"{damage['dice']}D{damage['die-type']}" + (
                    f"{damage_modifier:+d}" if damage_modifier else ""
                )
            else:
                damage_roll = ""

            self.e[f"weapon{slot}_damage"] = damage_roll + (
                f" {damage_note_indicator}" if damage_note_indicator else ""
            )

    def store_footnote(self, note):
        """Returns indicator character"""
        return self.footnotes[note] if note else None

    def print_footnotes(self):
        notes = list(
            chain(
                *[
                    wrap(f"{pointer} {note}", 40, subsequent_indent="  ")
                    for (note, pointer) in list(self.footnotes.items())
                ]
            )
        )

        if len(notes) > 12:
            logger.warning("Too many footnotes - truncated.")
        for i, note in enumerate(notes[:12]):
            self.e[f"note{i}"] = note

    def __str__(self):
        return ", ".join(
            [
                self.d.get(i)
                for i in ("name", "profession", "employer", "department", "age")
                if self.d.get(i)
            ]
        )


class Need2KnowPDF(object):
    # Location of form fields in Points (1/72 inch) -  0,0 is bottom-left - and font size
    field_xys = {
        # Personal Data
        "name": (75, 693, 11),
        "profession": (343, 693, 11),
        "employer": (75, 665, 11),
        "nationality": (343, 665, 11),
        "age": (185, 640, 11),
        "birthday": (200, 640, 11),
        "male": (98, 639, 11),
        "female": (76, 639, 11),
        # Statistical Data
        "strength": (136, 604, 11),
        "constitution": (136, 586, 11),
        "dexterity": (136, 568, 11),
        "intelligence": (136, 550, 11),
        "power": (136, 532, 11),
        "charisma": (136, 514, 11),
        "strength_x5": (172, 604, 11),
        "constitution_x5": (172, 586, 11),
        "dexterity_x5": (172, 568, 11),
        "intelligence_x5": (172, 550, 11),
        "power_x5": (172, 532, 11),
        "charisma_x5": (172, 514, 11),
        "strength_distinguishing": (208, 604, 11),
        "constitution_distinguishing": (208, 586, 11),
        "dexterity_distinguishing": (208, 568, 11),
        "intelligence_distinguishing": (208, 550, 11),
        "power_distinguishing": (208, 532, 11),
        "charisma_distinguishing": (208, 514, 11),
        "damage bonus": (555, 200, 11),
        "hitpoints": (195, 482, 11),
        "willpower": (195, 464, 11),
        "sanity": (195, 446, 11),
        "breaking point": (195, 428, 11),
        "bond0": (512, 604, 11),
        "bond1": (512, 586, 11),
        "bond2": (512, 568, 11),
        "bond3": (512, 550, 11),
        "disorder0": (340, 482, 11),
        "violence": (372, 384, 10),
        "helplessness": (486, 384, 10),
        # Applicable Skill Sets
        "accounting": (200, 361, 11),
        "alertness": (200, 343, 11),
        "anthropology": (200, 325, 11),
        "archeology": (200, 307, 11),
        "art1": (200, 289, 11),
        "art2": (200, 281, 11),
        "artillery": (200, 253, 11),
        "athletics": (200, 235, 11),
        "bureaucracy": (200, 217, 11),
        "computer science": (200, 200, 11),
        "craft1label": (90, 185, 9),
        "craft1value": (200, 185, 9),
        "craft2label": (90, 177, 9),
        "craft2value": (200, 177, 9),
        "craft3label": (90, 169, 9),
        "craft3value": (200, 169, 9),
        "craft4label": (90, 161, 9),
        "craft4value": (200, 161, 9),
        "criminology": (200, 145, 11),
        "demolitions": (200, 127, 11),
        "disguise": (200, 109, 11),
        "dodge": (200, 91, 11),
        "drive": (200, 73, 11),
        "firearms": (200, 54, 11),
        "first aid": (361, 361, 11),
        "forensics": (361, 343, 11),
        "heavy machinery": (361, 325, 11),
        "heavy weapons": (361, 307, 11),
        "history": (361, 289, 11),
        "humint": (361, 270, 11),
        "law": (361, 253, 11),
        "medicine": (361, 235, 11),
        "melee weapons": (361, 217, 11),
        "militaryscience1value": (361, 199, 11),
        "militaryscience1label": (327, 199, 11),
        "militaryscience2value": (361, 186, 11),
        "militaryscience2label": (327, 186, 11),
        "navigate": (361, 163, 11),
        "occult": (361, 145, 11),
        "persuade": (361, 127, 11),
        "pharmacy": (361, 109, 11),
        "pilot1value": (361, 91, 9),
        "pilot1label": (290, 91, 9),
        "pilot2value": (361, 83, 9),
        "pilot2label": (290, 83, 9),
        "psychotherapy": (361, 54, 11),
        "ride": (521, 361, 11),
        "science1label": (442, 347, 9),
        "science1value": (521, 347, 9),
        "science2label": (442, 340, 9),
        "science2value": (521, 340, 9),
        "science3label": (442, 333, 9),
        "science3value": (521, 333, 9),
        "science4label": (442, 326, 9),
        "science4value": (521, 326, 9),
        "search": (521, 307, 11),
        "sigint": (521, 289, 11),
        "stealth": (521, 270, 11),
        "surgery": (521, 253, 11),
        "survival": (521, 235, 11),
        "swim": (521, 217, 11),
        "unarmed combat": (521, 200, 11),
        "unnatural": (521, 181, 11),
        "language1": (521, 145, 11),
        "language2": (521, 127, 11),
        "language3": (521, 109, 11),
        "skill1": (521, 91, 11),
        "skill2": (521, 73, 11),
        "skill3": (521, 54, 11),
        # 2nd page
        "weapon0": (85, 480, 11),
        "weapon0_roll": (175, 480, 11),
        "weapon0_range": (215, 480, 11),
        "weapon0_damage": (270, 480, 11),
        "weapon0_ap": (345, 480, 11),
        "weapon0_lethality": (410, 480, 11),
        "weapon0_kill_radius": (462, 480, 11),
        "weapon0_ammo": (525, 480, 11),
        "weapon0_note": (560, 480, 11),
        "weapon1": (85, 461, 11),
        "weapon1_roll": (175, 461, 11),
        "weapon1_range": (215, 461, 11),
        "weapon1_damage": (270, 461, 11),
        "weapon1_ap": (345, 461, 11),
        "weapon1_lethality": (410, 461, 11),
        "weapon1_kill_radius": (462, 461, 11),
        "weapon1_ammo": (525, 461, 11),
        "weapon1_note": (560, 461, 11),
        "weapon2": (85, 442, 11),
        "weapon2_roll": (175, 442, 11),
        "weapon2_range": (215, 442, 11),
        "weapon2_damage": (270, 442, 11),
        "weapon2_ap": (345, 442, 11),
        "weapon2_lethality": (410, 442, 11),
        "weapon2_kill_radius": (462, 442, 11),
        "weapon2_ammo": (525, 442, 11),
        "weapon2_note": (560, 442, 11),
        "weapon3": (85, 423, 11),
        "weapon3_roll": (175, 423, 11),
        "weapon3_range": (215, 423, 11),
        "weapon3_damage": (270, 423, 11),
        "weapon3_ap": (345, 423, 11),
        "weapon3_lethality": (410, 423, 11),
        "weapon3_kill_radius": (462, 423, 11),
        "weapon3_ammo": (525, 423, 11),
        "weapon3_note": (560, 423, 11),
        "weapon4": (85, 404, 11),
        "weapon4_roll": (175, 404, 11),
        "weapon4_range": (215, 404, 11),
        "weapon4_damage": (270, 404, 11),
        "weapon4_ap": (345, 404, 11),
        "weapon4_lethality": (410, 404, 11),
        "weapon4_kill_radius": (462, 404, 11),
        "weapon4_ammo": (525, 404, 11),
        "weapon4_note": (560, 404, 11),
        "weapon5": (85, 385, 11),
        "weapon5_roll": (175, 385, 11),
        "weapon5_range": (215, 385, 11),
        "weapon5_damage": (270, 385, 11),
        "weapon5_ap": (345, 385, 11),
        "weapon5_lethality": (410, 385, 11),
        "weapon5_kill_radius": (462, 385, 11),
        "weapon5_ammo": (525, 385, 11),
        "weapon5_note": (560, 385, 11),
        "weapon6": (85, 366, 11),
        "weapon6_roll": (175, 366, 11),
        "weapon6_range": (215, 366, 11),
        "weapon6_damage": (270, 366, 11),
        "weapon6_ap": (345, 366, 11),
        "weapon6_lethality": (410, 366, 11),
        "weapon6_kill_radius": (465, 366, 11),
        "weapon6_ammo": (525, 366, 11),
        "weapon6_note": (560, 366, 11),
        "gear0": (75, 628, 8),
        "gear1": (75, 618, 8),
        "gear2": (75, 608, 8),
        "gear3": (75, 598, 8),
        "gear4": (75, 588, 8),
        "gear5": (75, 578, 8),
        "gear6": (75, 568, 8),
        "gear7": (75, 558, 8),
        "gear8": (75, 548, 8),
        "gear9": (75, 538, 8),
        "gear10": (75, 528, 8),
        "gear11": (323, 628, 8),
        "gear12": (323, 618, 8),
        "gear13": (323, 608, 8),
        "gear14": (323, 598, 8),
        "gear15": (323, 588, 8),
        "gear16": (323, 578, 8),
        "gear17": (323, 568, 8),
        "gear18": (323, 558, 8),
        "gear19": (323, 548, 8),
        "gear20": (323, 538, 8),
        "gear21": (323, 528, 8),
        "note0": (50, 40, 8),
        "note1": (50, 30, 8),
        "note2": (50, 20, 8),
        "note3": (50, 10, 8),
        "note4": (240, 40, 8),
        "note5": (240, 30, 8),
        "note6": (240, 20, 8),
        "note7": (240, 10, 8),
        "note8": (410, 40, 8),
        "note9": (410, 30, 8),
        "note10": (410, 20, 8),
        "note11": (410, 10, 8),
        "detail0": (75, 338, 8),
        "detail1": (75, 328, 8),
        "detail2": (75, 318, 8),
        "detail3": (75, 308, 8),
        "detail4": (75, 298, 8),
        "detail5": (75, 288, 8),
    }

    # Fields that also get a multiplier
    x5_stats = ["strength", "constitution", "dexterity", "intelligence", "power", "charisma"]

    def __init__(self, filename, professions, pages_per_sheet=1):
        self.filename = filename
        self.pages_per_sheet = pages_per_sheet
        self.c = canvas.Canvas(self.filename)
        # Set US Letter in points
        self.c.setPageSize((612, 792))
        self.c.setAuthor("https://github.com/jimstorch/DGGen")
        self.c.setTitle("Delta Green Agent Roster")
        self.c.setSubject("Pre-generated characters for the Delta Green RPG")
        # Register Custom Fonts
        pdfmetrics.registerFont(TTFont("Special Elite", "data/SpecialElite.ttf"))
        pdfmetrics.registerFont(TTFont("OCRA", "data/OCRA.ttf"))

    def generate_toc(self, professions, pages_per_sheet):
        """Build a clickable Table of Contents on page 1"""
        self.bookmark("Table of Contents")
        self.c.setFillColorRGB(0, 0, 0)
        self.c.setFont("OCRA", 10)
        #now = datetime.now().isoformat() + "Z"
        #self.c.drawString(150, 712, "DGGEN DTG " + now)
        #self.c.drawString(150, 700, "CLASSIFIED/DG/NTK//")
        #self.c.drawString(150, 688, "SUBJ ROSTER/ACTIVE/NOCELL/CONUS//")
        top = 650
        pagenum = 2
        for count, profession in enumerate(professions):
            label = generate_label(profession)
            chapter = "{:.<40}".format(shorten(label, 37, placeholder="")) + "{:.>4}".format(
                pagenum
            )
            self.c.drawString(150, top - self.line_drop(count), chapter)
            self.c.linkAbsolute(
                label,
                label,
                (145, (top - 6) - self.line_drop(count), 470, (top + 18) - self.line_drop(count)),
            )
            pagenum += profession["number_to_generate"] * pages_per_sheet
        if pages_per_sheet == 1:
            chapter = "{:.<40}".format("Blank Character Sheet Second Page") + "{:.>4}".format(
                pagenum + profession["number_to_generate"]
            )
            self.c.drawString(150, top - self.line_drop(pagenum), chapter)
            self.c.linkAbsolute(
                "Back Page",
                "Back Page",
                (
                    145,
                    (top - 6) - self.line_drop(pagenum),
                    470,
                    (top + 18) - self.line_drop(pagenum),
                ),
            )
        self.c.showPage()

    @staticmethod
    def line_drop(count, linesize=22):
        return count * linesize

    def bookmark(self, text):
        self.c.bookmarkPage(text)
        self.c.addOutlineEntry(text, text)

    def draw_string(self, x, y, size, text):
        self.c.setFont(DEFAULT_FONT, size)
        self.c.setFillColorRGB(*TEXT_COLOR)
        self.c.drawString(x, y, str(text))

    def fill_field(self, field, value):
        try:
            x, y, s = self.field_xys[field]
            self.draw_string(x, y, s, str(value))
        except KeyError:
            logger.error("Unknown field %s", field)

    def add_cover(self):
        self.c.drawImage("data/front_cover.jpg", 0, 0, 612, 792)
        self.c.setFillColorRGB(255,255,255)
        self.c.setFont("OCRA", 24)
        now = datetime.now().strftime("%Y-%m-%dT%H:%MZ")
        self.c.drawString(20, 85, "DGGEN DTG " + now)
        self.c.drawString(20, 55, "CLASSIFIED/DG/NTK//")
        self.c.drawString(20, 25, "SUBJ ROSTER/ACTIVE/NOCELL/CONUS//")
        self.c.showPage()
        self.c.drawImage("data/inside_cover.jpg", 0, 0, 612, 792)
        self.c.showPage()

    def add_page(self, d):
        # Add background.  ReportLab will cache it for repeat
        self.c.drawImage("data/Character Sheet NO BACKGROUND FRONT.jpg", 0, 0, 612, 792)

        for key in d:
            self.fill_field(key, d[key])

        # Tell ReportLab we're done with current page
        self.c.showPage()

    def add_page_2(self, e):
        # Add background.  ReportLab will cache it for repeat
        self.c.drawImage("data/Character Sheet NO BACKGROUND BACK.jpg", 0, 0, 612, 792)

        for key in e:
            self.fill_field(key, e[key])

        # Tell ReportLab we're done with current page
        self.c.showPage()

    def save_pdf(self):
        if self.pages_per_sheet == 1:
            self.bookmark("Back Page")
            self.c.drawImage("data/Character Sheet NO BACKGROUND BACK.jpg", 0, 0, 612, 792)
            self.c.showPage()
        self.c.save()


def generate_label(profession):
    return ", ".join(
        e
        for e in [
            profession.get("label", ""),
            profession.get("employer", ""),
            profession.get("division", ""),
        ]
        if e
    )


def get_options():
    """Get options and arguments from argv string."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="specify up to three times to increase verbosity, "
        "i.e. -v to see warnings, -vv for information messages, or -vvv for debug messages.",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        default=f"DeltaGreenPregen-{datetime.now():%Y-%m-%d-%H-%M}.pdf",
        help="Output PDF file. Defaults to %(default)s.",
    )
    parser.add_argument(
        "-t", "--type", action="store", help=f"Select single profession to generate."
    )
    parser.add_argument("-l", "--label", action="store", help="Override profession label.")
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        action="store",
        help="Generate this many characters of each profession.",
    )
    parser.add_argument(
        "-e", "--employer", action="store", help="Set employer for all generated characters."
    )
    parser.add_argument(
        "-u",
        "--unequipped",
        action="store_false",
        dest="equip",
        help="Don't generate equipment.",
        default=True,
    )

    data = parser.add_argument_group(title="Data", description="Data file locations")
    data.add_argument(
        "--professions",
        action="store",
        default="data/professions.json",
        help="Data file for professions - defaults to %(default)s",
    )
    parser.add_argument(
        "-a",
        "--min-age",
        action="store",
        type=int,
        help="Minimum age of characters - defaults to %(default)s.",
        default=25
    )
    parser.add_argument(
        "-A",
        "--max-age",
        action="store",
        type=int,
        help="Maximum age of characters - defaults to %(default)s.",
        default=55,
    )
    parser.add_argument(
        "--veterancy",
        action="store_true",
        dest="veterancy",
        help="Grant additional experience due to age.",
        default=False,
    )
    parser.add_argument(
        "--no-damaged",
        action="store_false",
        dest="damaged",
        help="Don't generate damaged veterans.",
        default=True,
    )

    return parser.parse_args()


@dataclass
class Data:
    male_given_names: List[str]
    female_given_names: List[str]
    family_names: List[str]
    towns: List[str]
    professions: Dict[str, Any]
    kits: Dict[str, Any]
    weapons: Dict[str, Any]
    armour: Dict[str, Any]
    distinguishing: Dict[Tuple[str, int], List[str]]


def load_data(options):
    with open("data/boys1986.txt") as f:
        male_given_names = f.read().splitlines()
    with open("data/girls1986.txt") as f:
        female_given_names = f.read().splitlines()
    with open("data/surnames.txt") as f:
        family_names = f.read().splitlines()
    with open("data/towns.txt") as f:
        towns = f.read().splitlines()
    with open(options.professions) as f:
        professions = json.load(f)
    with open("data/equipment.json") as f:
        equipment = json.load(f)
        kits = equipment["kits"]
        weapons = equipment["weapons"]
        armour = equipment["armour"]

    distinguishing = {}
    with open("data/distinguishing-features.csv") as f:
        for row in csv.DictReader(f):
            for value in range(int(row["from"]), int(row["to"]) + 1):
                distinguishing.setdefault((row["statistic"], value), []).append(
                    row["distinguishing"]
                )

    data = Data(
        male_given_names=male_given_names,
        female_given_names=female_given_names,
        family_names=family_names,
        towns=towns,
        professions=professions,
        kits=kits,
        weapons=weapons,
        armour=armour,
        distinguishing=distinguishing,
    )
    return data


def init_logger(verbosity, stream=sys.stdout):
    """Initialize logger and warnings according to verbosity argument.
    Verbosity levels of 0-3 supported."""
    is_not_debug = verbosity <= 2
    level = (
        [logging.ERROR, logging.WARNING, logging.INFO][verbosity] if is_not_debug else logging.DEBUG
    )
    log_format = (
        "%(message)s"
        if is_not_debug
        else "%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s"
    )
    logging.basicConfig(level=level, format=log_format, stream=stream)
    if is_not_debug:
        warnings.filterwarnings("ignore")


if __name__ == "__main__":
    sys.exit(main())
