# Tatoeba Groupie
## Multilingual Tatoeba Scraper

Tatoeba.org allows anyone to search for translations from one language to another, and Tatoeba Groupie allows anyone to specify a list of languages and find groups of mutually translated sentences where every language indicated is present. Once these "groupies" are located, they can then be exported to plain text, which is compatible for import into Anki.

## How to get Tatoeba Groupie up and running

This version of Tatoeba Groupie is written in python (version 3.3), using a snapshot of the wxPython Phoenix project for the user interface. It is not an executable; it needs to be run from a command prompt. If you are not familiar with command prompts, do a [search](https://www.google.com/search?q=how+to+browse+to+a+different+directory+from+the+command+prompt) and that will give you the basics. If your system is easily supported, the following steps will get you up and running:

- Install a version of python 3 (3.3 recommended simply due to its use during coding) from https://www.python.org/downloads/  These are executables you can run directoly.

- Install pip if you don't already have it. Instructions are available here: https://pip.pypa.io/en/latest/installing.html  You need to use a command prompt to have python run the install file. If you get complaints about python not recognized as a command, you can either switch to the directory where python.exe is located, or [add python to your path](https://www.google.com/search?q=how+to+add+python+to+your+path)

- Then use pip (from the command line) to install a wxPython Phoenix snapshot. Pip will be in the scripts folder of your python installation (or it may already be on your path). Run the following command:

```
pip install -U --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix
```

If pip doesn't work, try pip3 and/or pip3.3.

- Download all of the Tatoeba Groupie files into a folder on your system, and run the file named tgui.py from python using the command line. The command "python tgui.py" must be run from the folder containing tgui.py, or you can give a full path to the file such as "python c:\TatoebaGroupie\tgui.py".

If it works you're good. If not, keep your eyes open for a Java version of Tatoeba Groupie.