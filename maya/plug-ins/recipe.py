'''
########################################################################
#                                                                      #
#             recipe.py                                              #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        Copyright (c) 2013 Cedric BAZILLOU All rights reserved.
        
        Permission is hereby granted
            -to modify the file
            -distribute
            -share
            -do derivative work  

    P U R P O S E:
        Compute twist on a per segment level --> we expect normalize u values....
    I N S T A L L A T I O N:
        Copy the "recipe.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

__plug_in__Version = "0.1"
__author = "Bazillou2013"

import math 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "recipe"
kPluginNodeId = OpenMaya.MTypeId(0xBCB7155) 

       


class recipe(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def compute(self,Plug,Data):
        return

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(recipe())
def nodeInitializer():
    typed_Attr  = OpenMaya.MFnTypedAttribute()
    gAttr       = OpenMaya.MFnGenericAttribute()

    recipe.input = gAttr.create( "input", "in" )
    gAttr.setStorable(0)
    gAttr.setHidden(1)
    gAttr.addDataAccept ( OpenMaya.MFnData.kAny )
    gAttr.addDataAccept ( OpenMaya.MFnData.kString )
    gAttr.addDataAccept ( OpenMaya.MFnData.kMatrix  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kStringArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kDoubleArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kIntArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kPointArray )
    gAttr.addDataAccept ( OpenMaya.MFnData.kVectorArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kMesh  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kLattice   )
    gAttr.addDataAccept ( OpenMaya.MFnData.kNurbsCurve    )
    gAttr.addDataAccept ( OpenMaya.MFnData.kNurbsSurface     )
    gAttr.setArray(1)
    recipe.addAttribute(recipe.input)

    recipe.output = gAttr.create( "output", "out" )
    gAttr.setStorable(0)
    gAttr.setHidden(1)
    gAttr.addDataAccept ( OpenMaya.MFnData.kAny )
    gAttr.addDataAccept ( OpenMaya.MFnData.kString )
    gAttr.addDataAccept ( OpenMaya.MFnData.kMatrix  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kStringArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kDoubleArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kIntArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kPointArray )
    gAttr.addDataAccept ( OpenMaya.MFnData.kVectorArray  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kMesh  )
    gAttr.addDataAccept ( OpenMaya.MFnData.kLattice   )
    gAttr.addDataAccept ( OpenMaya.MFnData.kNurbsCurve    )
    gAttr.addDataAccept ( OpenMaya.MFnData.kNurbsSurface     )
    gAttr.setArray(1)
    recipe.addAttribute(recipe.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, __author, __plug_in__Version, "Any")
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeName ); raise
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName ); raise