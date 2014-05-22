'''
########################################################################
#                                                                      #
#             recipe.py                                                #
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

__plug_in__Version = "0.13"
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
    gAttr       = OpenMaya.MFnGenericAttribute()
    cAttr       = OpenMaya.MFnCompoundAttribute()
    typed_Attr  = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    
    recipe.inputGrp = nAttr.create( "inputGrp", "inGr", OpenMaya.MFnNumericData.kDouble  )
    nAttr.setStorable(0)
    nAttr.setHidden(0)
    recipe.addAttribute(recipe.inputGrp)

    recipe.outputGrp = nAttr.create( "outputGrp", "outGr", OpenMaya.MFnNumericData.kDouble  )
    nAttr.setStorable(0)
    nAttr.setHidden(0)
    recipe.addAttribute(recipe.outputGrp)
    
    recipe.version = typed_Attr.create( "version", "vrs",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(0)
    recipe.addAttribute(recipe.version)

    recipe.foodType = typed_Attr.create( "foodType", "fdtp",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(0)
    recipe.addAttribute(recipe.foodType)
    
    recipe.author = typed_Attr.create( "author", "aut",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(0)
    recipe.addAttribute(recipe.author)
    
    recipe.gitSource = typed_Attr.create( "gitSource", "gtS",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(0)
    recipe.addAttribute(recipe.gitSource)
    
    recipe.releaseDate = typed_Attr.create( "releaseDate", "rls",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(0)
    recipe.addAttribute(recipe.releaseDate)

    recipe.inlink = gAttr.create( "inlink", "ilk" )
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

    recipe.inLabel = typed_Attr.create( "inLabel", "ilb",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    
    recipe.inWidgetID = typed_Attr.create( "inWidgetID", "iwID",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)

    recipe.input_useParentHub = nAttr.create( "input_useParentHub", "inHB", OpenMaya.MFnNumericData.kBoolean,False  )
    nAttr.setStorable(1)
    nAttr.setHidden(1)

    recipe.input = cAttr.create( "input", "in" )
    cAttr.addChild(recipe.inlink)
    cAttr.addChild(recipe.inLabel)
    cAttr.addChild(recipe.inWidgetID)
    cAttr.addChild(recipe.input_useParentHub)

    cAttr.setArray(1)
    recipe.addAttribute(recipe.input)

    recipe.outLink = gAttr.create( "outLink", "oLk" )
    gAttr.setStorable(0)
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
    
    recipe.outLabel = typed_Attr.create( "outLabel", "olb",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)

    recipe.outWidgetID = typed_Attr.create( "outWidgetID", "owID",  OpenMaya.MFnData.kString ) 
    typed_Attr.setStorable(1)
    
    recipe.output_useParentHub = nAttr.create( "output_useParentHub", "outHB", OpenMaya.MFnNumericData.kBoolean,False  )
    nAttr.setStorable(1)
    nAttr.setHidden(1)

    recipe.output = cAttr.create( "output", "out" )
    cAttr.addChild(recipe.outLink)
    cAttr.addChild(recipe.outLabel)
    cAttr.addChild(recipe.outWidgetID)
    cAttr.addChild(recipe.output_useParentHub)
    cAttr.setArray(1)
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