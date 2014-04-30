'''
########################################################################
#                                                                      #
#             numToString.py                                            #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        Copyright (c) 2013 Cedric BAZILLOU All rights reserved.
        
        Permission is hereby granted to Normanstudios/ mikros / onyx films companies to
            -to modify the file
            -distribute
            -share
            -do derivative work  

        The above copyright notice and this permission notice shall be included in all copies of the Software 
        and is subject to the following conditions:
            - These 3 companies uses the same type of license
            - credit the original author
            - does not claim patent nor copyright from the original work
            - this plugin is not sold to third parties

    P U R P O S E:
        Control a rear or frond quadruped leg
        - compact several nodes and parameter in one place

    I N S T A L L A T I O N:
        Copy the "numToString.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''


import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "numToString"
kPluginNodeId = OpenMaya.MTypeId(0x24BCD179) 

class numToString(OpenMayaMPx.MPxNode):
    labelStr = OpenMaya.MObject()
    inputNum   = OpenMaya.MObject()
    output  = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
        
    def compute(self,Plug,Data):
        if Plug == self.output:
            labelStr_Hdle = Data.inputValue(self.labelStr)    
            inputNum_Hdle = Data.inputValue(self.inputNum)
            output_Handle = Data.outputValue(self.output)        
            
            inDouble = inputNum_Hdle.asDouble()
            inlabel = labelStr_Hdle.asString()
            resStream = inlabel + '_' + str(round( inDouble , 3))
            if len ( inlabel ) == 0:
                resStream = str(round( inDouble , 3))
                
            output_Handle.setString( resStream )        
            output_Handle.setClean()            
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(numToString())

def nodeInitializer():

    labelStr_Attr =  OpenMaya.MFnTypedAttribute()
    numToString.labelStr = labelStr_Attr.create( "labelStr", "lss", OpenMaya.MFnData.kString  )
    labelStr_Attr.setStorable(1)
    labelStr_Attr.setKeyable(0)
    labelStr_Attr.setHidden(False)
    numToString.addAttribute( numToString.labelStr  )

    
    inputShape_Attr =  OpenMaya.MFnNumericAttribute()    
    numToString.inputNum = inputShape_Attr.create( "inputNum", "num", OpenMaya.MFnNumericData.kDouble  )
    inputShape_Attr.setStorable(0)
    inputShape_Attr.setKeyable(0)
    inputShape_Attr.setHidden(0)        
    numToString.addAttribute( numToString.inputNum )

    output_Attr =  OpenMaya.MFnTypedAttribute()
    numToString.output = output_Attr.create( "output", "out", OpenMaya.MFnData.kString  )
    output_Attr.setStorable(0)
    output_Attr.setKeyable(0)
    output_Attr.setHidden(False)
    numToString.addAttribute( numToString.output)

    numToString.attributeAffects( numToString.inputNum , numToString.output )        
    numToString.attributeAffects( numToString.labelStr  , numToString.output )             
    
    
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Bazillou2010", "1.0", "Any")
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





