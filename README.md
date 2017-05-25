# DGGen

DGGen is a program written in Python to generate characters for the pen-and-paper roleplaying game Delta Green from Arc Dream Publishing.  It follows the character creations rules included in Delta Green:Need to Know and the Delta Green Agent's Handbook.  The Python Libraries PyPDF2 and ReportLab are required.  Characters are created one-per-page into a PDF.  The second-page of the character sheet is included as the final page in the PDF.  By default, forty characters of alternating genders are created in each of the following professions:

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

The following character sheet images were graciously provided by Simeon Cogswell, designer for Delta Green:
* Character Sheet NO BACKGROUND.pdf
* Character Sheet NO BACKGROUND BACK.jpg
* Character Sheet NO BACKGROUND FRONT.jpg

Big thank you to Simeon and the folks at Arc Dream Publishing for the support.


## Setting up a virtual environment

We use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to isolate our dependancies from any other projects that we might be working on.

    $ virtualenv -p python3 venv

We do this only once, when we need to create the virtual environment. We can activate an existing virtual environment with:

    * source venv/bin/activate

## Installing dependecies

    $ pip install -U -r requirements.txt
