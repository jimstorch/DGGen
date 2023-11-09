# DGGen

## Just want the characters?

Some pregenerated sets of characters can be found [here](https://drive.google.com/drive/folders/1lHiAymWByYFx5UiZciZhvyIONHVra2JS).

## Introduction

DGGen is a program written in Python to generate characters for the pen-and-paper roleplaying game Delta Green from Arc
Dream Publishing. It follows the character creations rules included in Delta Green:Need to Know and the Delta Green
Agent's Handbook. The [ReportLab](https://www.reportlab.com/dev/opensource/) library is required. Characters are created
one-per-page (if unequipped) or two-per-page into a PDF.  (The second-page of the character sheet is included as the
final page in the PDF if characters are generated unequipped.) By default, characters of alternating genders are created
in each of the following professions:

* Anthropologist
* Business Executive
* Computer Science
* Criminal
* Engineer
* Federal Agent
* Firefighter
* Foreign Service Officer
* Historian
* Intelligence Analyst
* Intelligence Case Officer
* Lawyer
* Marine
* Media Specialist
* Nurse
* Paramedic
* Physician
* Pilot
* Police Officer
* Program Manager
* Sailor
* Scientist
* Soldier
* Special Operator

## Customising

(Edit [`data/professions.json`](data/professions.json) to alter the professions generated, or the number of characters
generated per profession.)

By default, the generator uses data from [`data/professions.json`](data/professions.json) to define professions, and 
the number of characters generated for each. Different sets of professions can be used with the `--professions` flag.
See [`data/professions-fbi.json`](data/professions-fbi.json) as an example, or you can create your own.

Pre-built examples include [`data/professions-fbi.json`](data/professions-fbi.json),
[`data/professions-cia.json`](data/professions-cia.json), [`data/professions-dea.json`](data/professions-dea.json), and
[`data/professions-socom.json`](data/professions-socom.json).

The following character sheet images were graciously provided by Simeon Cogswell, designer for Delta Green:
* Character Sheet NO BACKGROUND.pdf
* Character Sheet NO BACKGROUND BACK.jpg
* Character Sheet NO BACKGROUND FRONT.jpg

Big thank you to Simeon and the folks at Arc Dream Publishing for the support.

## Tasks

### venv

Set up a virtual environment

We use [venv](https://docs.python.org/3/library/venv.html) to isolate our dependencies from any other Python projects that we might be working on. We only need to do this once.

```sh
python3 -m venv .venv
```

### activate

Activate an existing virtual environment.

```sh
source .venv/bin/activate
```

### dependecies

Install dependencies

```sh
pip install -U -r requirements.txt
```

### generate

Generate standard characters.

```sh
./generator.py
```

### generate-soldiers

Generate a group of Green Berets.

```sh
./generator.py --type soldier --label "Green Beret" --employer "United States Army" --count 24 --output "Bravo Company.pdf"
```

### generate-police

Generate a group of Police.

```sh
./generator.py --type police --employer "NYPD" --output "The 17th Precinct.pdf"
```

### generate-criminals

Generate a group of criminals.

```sh
./generator.py --type criminal --label "Thug" --employer "Fat Tony" --count 12 --output "Tony's Enforcers.pdf"
```

### generate-fbi

Generate a group of FBI Agents.

```sh
./generator.py --professions data/professions-fbi.json -o "FBI Field Office.pdf"
```

### generate-cia

Generate a group of CIA Agents.

```sh
./generator.py --professions data/professions-cia.json -o "CIA London Station.pdf"
```

### generate-socom

Generate a group of special forces soldiers.

```sh
./generator.py --professions data/professions-socom.json -o "SOCOM Camp Echo.pdf"
```

Generate a group of DEA Agents.

### generate-dea

```sh
./generator.py --professions data/professions-dea.json -o "DEA Field Office.pdf"
```

### generate-seals

Generate a group of Navy SEALS.

```sh
./generator.py --professions data/professions-socom.json --type seal --count 12 -o "Operation ROOKHAVEN.pdf"
```

### help

To see what options you have available, run:

```sh
./generator.py -h
```

## License

DDGen is licensed under the Apache 2.0 Open Source License. Please see the /data folder for font licenses. The
intellectual property known as Delta Green is ™ and © the Delta Green Partnership (http://www.delta-green.com).

## Contact

    import codecs; codecs.encode('wvzfgbepu@tznvy.pbz', 'rot13')
