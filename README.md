circeCharacterWorksTools
========================

A set of tool for maya designed to handle character deformation effectively

* ..Current Features *
|Feature                          |Description  |
|:--------------------------------|:-----------:|
|Template based                   | All aspect of deformation organized into a logical unit  : a dish . |
|Highly optimized                 | Each dish covers a simple task  by using a custom foodNode |
|Faster rig and smaller files     | A foodNode is node baking lot of operations inside a black box, we interact with maya with nodes and need less scripting |

### Installing

1. Download a [release][]
2. Unpack into a target folder

### maya environment variable
```
ccwLocation = D:\GitHub
MAYA_PLUG_IN_PATH = %ccwLocation%\circeCharacterWorksTools\maya\plug-ins
```
1. copy the above lines into your local maya.env text file
2. modify ccwLocation by your target folder

### USE
1. in your script editor
```
import maya.cmds as mc
import sys, os
TargetDirectory = 'D:\GitHub'
if TargetDirectory not in sys.path:
    sys.path.append(TargetDirectory)

import circeCharacterWorksTools.maya.rig.dish.Tool as bento
bento.Tool().show()
```
