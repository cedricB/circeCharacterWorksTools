circeCharacterWorksTools
========================

A set of tool for maya designed to handle character deformation effectively

Install
=======
-- extract or copy 'circeCharacterWorksTools' in a 'TargetDirectory'( called ccwLocation from now on )
-- change ccwLocation into maya.env( then copy this content into your local  scripts/maya.env file)

import sys, os
TargetDirectory = 'D:\GitHub'
if TargetDirectory not in sys.path:
    sys.path.append(TargetDirectory)

#You will then invoke this package with
import circeCharacterWorksTools as ccwLib
