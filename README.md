# DGGen

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

(Edit [data/professions.json](`data/professions.json`) to alter the professions generated, or the number of characters
generated per profession.)

The following character sheet images were graciously provided by Simeon Cogswell, designer for Delta Green:
* Character Sheet NO BACKGROUND.pdf
* Character Sheet NO BACKGROUND BACK.jpg
* Character Sheet NO BACKGROUND FRONT.jpg

Big thank you to Simeon and the folks at Arc Dream Publishing for the support.

## Setting up a virtual environment

We use [venv](https://docs.python.org/3/library/venv.html) to isolate our dependancies from any other projects that we might be working on.

    $ python3 -m venv venv

We do this only once, when we need to create the virtual environment. We can activate an existing virtual environment with:

    $ source venv/bin/activate

## Installing dependecies

    $ pip install -U -r requirements.txt

## Generating characters

To generate characters, run:

    $ ./generator.py

If you need a more targeted set of characters, all of a specific profession, you can generate one as per these examples:

    $ ./generator.py --type soldier --label "Green Beret" --employer "United States Army" --count 24 --output "Bravo Company.pdf"
    
    $ ./generator.py --type police --employer "NYPD" --output "The 17th Precinct.pdf"
    
    $ ./generator.py --type criminal --label "Thug" --employer "Fat Tony" --count 12 --output "Tony's Enforcers.pdf"

By default, the generator uses data from [data/professions.json](`data/professions.json`) to define professions.
Different sets of professions can be used with the `--professions` flag.
See [data/professions-fbi.json](`data/professions-fbi.json`)
as an example, or you can create your own.

    $ ./generator.py --professions data/professions-fbi.json -o "FBI Field Office.pdf"

    $ ./generator.py --professions data/professions-cia.json -o "CIA London Station.pdf"

Pre-built examples include [data/professions-fbi.json](`data/professions-fbi.json`) and
[data/professions-fbi.json](`data/professions-fbi.json`), and you can of course create your own.

To see what options you have available, run:

    $ ./generator.py -h

## License

DDGen is licensed under the Apache 2.0 Open Source License. Please see the /data folder for font licenses. The
intellectual property known as Delta Green is ™ and © the Delta Green Partnership (http://www.delta-green.com).

## Contact

    import codecs; codecs.encode('wvzfgbepu@tznvy.pbz', 'rot13')
