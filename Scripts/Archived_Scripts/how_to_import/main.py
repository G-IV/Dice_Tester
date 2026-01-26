import helper
from sibling_a import sib_a
from sibling_b import sib_b

helper.ping()
sib_a.ping()
sib_b.ping()

'''
What I've learned: don't split python into sibling directories for this project.  Keep helper files in one child directory.
'''