# HELPFUL INFO

- You may want to right-click edit the "Tatoeba Groupie.bat" file. it's a quicker way to start than using the command prompt directly.

- The export files are not in an order that is generally predictable. You will need to open the exported file (notepad works fine for me) if you need to tell other software (such as Anki) the order of the fields. The final field is some tags about whether the sentences are short, or have exactly one and only one sentence per each language.

- Many "groupies" are actually not very useful --- groupies group indirect translations to any level of depth, so by the time they are all captured into one "groupie", you often end up with a game of tranlational telephone. In other words, many of the sentences are nothing alike, and it's not very useful to consider them as a mutual translation ~groupie~.

- The language selection dialog tends to put the descriptions following a comma, so "Old English" becomes "English, Old". If it sounds like an adjective, it may be put afterwards. Also, the final entry, Éwé, seems out of order compared to general expectation.

- You can select no languages from the choices and you will get a list of ~all~ groupies, but they can't be exported due to the variability of languages in each groupie. However, it would allow you to look up a particular groupie, which would give you access to the IDs of the sentences and their links to Tatoeba.org, in case you wish to reference the original online.

- This version of Tatoeba Groupie is hardcoded to a dataset that was available sometime late December 2014. To get it out the door quicker, I removed the ability to parse a freshly downloaded dataset from Tatoeba groupie. That feature may return shortly, but half a million groupies now is likely sufficient for most anyone! If it's important, I could update to a newer dataset fairly easily.

- I'm expecting to put out other versions of Tatoeba Groupie, perhaps a Java version, maybe even an Android version.But who knows.

- Release versions of Tatoeba Groupie come with a few other files which seem kind of "magic" since Tatoeba Groupie is open source and they are weird binary files. They are actually generated with code found in the python files that was commented out to speed up release, but cost the ability to generate/parse new database files from Tatoeba on the fly. If the code is your concern, prego, it's in there.