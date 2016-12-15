# DGGen

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
