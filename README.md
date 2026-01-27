# Dice_Tester
Tests how random my dice are.

# Notes on my setup
* [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
* I need to be able to import python scripts between directories - lots of frustrated reading later, it appears this is the widely accepted method [on stackoverflow](https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944).
  * One thing to note, the directory for the python files needs a `__init__.py` file.  This isn't showing in the stackoverflow comment.
* Folder Explanations
  * _Modeling_. I want all the files related to captureing video & images for the purpose of labeling and generated models to be stored here.
  * _Scripts_.  I want all the python scripts related to the project (outside of those required for modeling) to be found here.
* The Analog Discovery 2 is operated with the Waveforms SDK.  You can read more about it at their [website](https://digilent.com/reference/software/waveforms/waveforms-sdk/start).

# Notes to myself, because I forget things
* To activate the venv
  ```zsh
  source ./venv/bin/activate
  ```