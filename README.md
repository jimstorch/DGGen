# DGGen

## Setting up a virtual environment

We use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to isolate our dependancies from any other projects that we might be working on.

    $ virtualenv -p python3 venv

We do this only once, when we need to create the virtual environment. We can activate an existing virtual environment with:

    * source venv/bin/activate

## Installing dependecies

    $ pip install -U -r requirements.txt
