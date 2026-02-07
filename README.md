# Dice_Tester
Tests how random my dice are.

# Notes on my setup
* [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
* I need to be able to import python scripts between directories - lots of frustrated reading later, it appears this is the widely accepted method [on stackoverflow](https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944).
  * This linek is going to disappear, I guarantee it.
    * Make sure all the python files/folders all fall under a parent folder.  In this case, it's Dice_Tester.
    * Create the pyproject.toml file
    * Make the virtual environment: `python3 -m venv venv` (you can specify what version using `python3.10` or whatever)
      * When you realize you need to delet your venv: `sudo rm -rf venv`
    * Activate the virtual environment: `source ./venv/bin/activate`
      * You can deactivate with by typing: `deactivate`
    * Install all the stuff using `pip install -e .` (Do I need to use `pip3`?)
      * Be sure you have pip --version >= 21.3 (`pip install --upgrade pip`)

  * One thing to note, the directory for the python files needs a `__init__.py` file.  This isn't showing in the stackoverflow comment.
* Folder Explanations
  * _Modeling_. I want all the files related to captureing video & images for the purpose of labeling and generated models to be stored here.
  * _Scripts_.  I want all the python scripts related to the project (outside of those required for modeling) to be found here.
* The Analog Discovery 2 is operated with the Waveforms SDK.  You can read more about it at their [website](https://digilent.com/reference/software/waveforms/waveforms-sdk/start).
* It seems that the [Chi-square test](https://en.wikipedia.org/wiki/Chi-squared_test) is what people use to determine how random your dice are.
* While this isn't a direct project dependency, if you need to make cusom models, label-studio was fantastic for me.  I found the initial setup and labeling to be easy, with the only downside being that applied filters don't affect what is exported - so I learned that I need to do a different project for training and validation.  I didn't include it in the pyproject.toml file, but I thought it was worth mentioning it here.
  * If you have issues with installation via pip (which I did, unexpectedly), follow their instructions for installing via homebrew. 
* If you aren't sure what your webcam's fps is and you can't find or be bothered to look for the documentation, I used [webcamtests](https://webcamtests.com/fps) to figure out the FPS.  It was super fast, I did 0 work on figuring out if it was safe.

# Notes to myself, because I forget things
* To activate the venv
  ```zsh
  source ./venv/bin/activate
  ```
* When you get `ModuleNotFoundError: No module named 'Scripts'`, do this: `pip install -e .`