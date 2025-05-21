Sarka

- in MML_Stimulus_Presentation_LSL.py , you use absolute path of your directory. This will not work for anyone else then you. 
Use relative path by getting the working directory of this script and navigate from there
- in VIDEO, there are two camera scripts, why? If you dont use the test.py script, just delete it
- Is the MML video script having the updates from Pascal? (@Wim)
- I am missing a general README of overview of these scripts, plus also what to turn on when, on the same pc or differently? Also, if we want to have this in Quarto, 
.py scripts are not ideal. So either we just link them but don't really go through them in notebook manner, or we put chunks of the code into jupyter notebook
just to explain what is happening, or this part of Lab Setup is not covered in Quarto at all. I think essentially it doesn't have to be there in form of the code,
but somehow you want to make it accessible so perhaps some guide through the scripts in form of notebook would not be bad. If I go directly to this folder as a naive
user, I don't really know what to do
- are in folders Phisiology supposed to be also scripts? If not I would not make folders that have only manuals. Then I would rather make folder Manuals (same for what is LSL) - these things should be rather in
the paper or in the Quarto book, but I feel they are here just occupying space. But if there are still going to be scripts then ignore this
