'''
Install
=======
-- extract or copy 'circeCharacterWorksTools' in a 'TargetDirectory'( called ccwLocation from now on )
-- change ccwLocation into maya.env( then copy this content into your local  scripts/maya.env file)
'''

#------------------------ copy paste this code in your script editor
import sys, os
TargetDirectory = 'D:\GitHub'
if TargetDirectory not in sys.path:
    sys.path.append(TargetDirectory)

#You will then invoke this package with
import circeCharacterWorksTools as ccwLib