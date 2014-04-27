'''
########################################################################
#                                                                      #
#             toggleArray.py                                           #
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

        The above copyright notice and this permission notice shall be included in all copies of the Software 
        and is subject to the following conditions:
            - Te user uses the same type of license
            - credit the original author
            - does not claim patent nor copyright from the original work

    P U R P O S E:
        toggleArray weights for space switching, visibility, blendshape etc

    I N S T A L L A T I O N:
        Copy the "toggleArray.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "toggleArray"
kPluginNodeId = OpenMaya.MTypeId(0xACC1246) 
kPluginNodeAuthor = "Bazillou cedric2009"
kPluginNodeVersion = "1.0.0"


class toggleArray(OpenMayaMPx.MPxNode):
    def compute(self,Plug,Data):
        #data handles Layout
        numberofOutput_Val        = Data.inputValue(self.numberofOutput ).asInt()
        activeIndex_Val  = Data.inputValue(self.activeIndex ).asInt()
        outState_handle  = Data.outputArrayValue(self.outState ) 
        activeValue_Val        = Data.inputValue(self.activeValue ).asInt()
        disableValue_Val       = Data.inputValue(self.disableValue ).asInt()
        #FoolProof check
        if activeIndex_Val > (numberofOutput_Val - 1):
            activeIndex_Val = numberofOutput_Val - 1
        ThsNde = self.thisMObject()

        self.write_ouputState( outState_handle,numberofOutput_Val,activeIndex_Val,ThsNde,activeValue_Val,disableValue_Val )
    def write_ouputState(self,outState_handle,numberofOutput_Val,activeIndex_Val,ThsNde ,activeValue_Val,disableValue_Val):
        cBuilder = outState_handle.builder()

        stateList = []
        stateList = [ disableValue_Val for k in range(numberofOutput_Val) ]
        stateList[activeIndex_Val] = activeValue_Val
        
        currentDH = OpenMaya.MDataHandle()
        for n in range(0,numberofOutput_Val):
            currentDH = cBuilder.addElement(n)
            currentDH.setInt(stateList[n])
            
        bldChck = cBuilder.elementCount()
        # prune unwanted index --> equivalent to removeMultiInstance...
        if bldChck>numberofOutput_Val:
            depFn = OpenMaya.MFnDependencyNode( ThsNde )
            curvePointsPlug = depFn.findPlug('outState')            
            outName = curvePointsPlug.info()
            for k in range(bldChck-1,numberofOutput_Val-1,-1):
                try:
                    cBuilder.removeElement(k)
                except:
                    # --> a bit dirty but it help when node is not connected yet we have access to the correct number of output attribute
                    # when node is connected this fallback is not needed anymore
                    cmds.removeMultiInstance( '%s[%s]'%(outName,k), b=True ) 
        outState_handle.set(cBuilder)
        outState_handle.setAllClean()
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(toggleArray())
def link_relashionShip( DriverList, driven_Attribute ):
    for driver in DriverList:
        toggleArray.attributeAffects(driver,driven_Attribute)
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()

    #----------------------------------------------------------------------------------------------- Input Attributes

    toggleArray.numberofOutput = nAttr.create( "numberOfOutput", "cn", OpenMaya.MFnNumericData.kInt,1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(1)
    nAttr.setSoftMax(16)
    toggleArray.addAttribute( toggleArray.numberofOutput )
    
    toggleArray.activeIndex = nAttr.create( "activeIndex", "aID", OpenMaya.MFnNumericData.kInt,0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0)
    toggleArray.addAttribute( toggleArray.activeIndex )
    
    toggleArray.activeValue = nAttr.create( "activeValue", "aVle", OpenMaya.MFnNumericData.kInt,1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0)
    toggleArray.addAttribute( toggleArray.activeValue )
    
    toggleArray.disableValue = nAttr.create( "disableValue", "dVle", OpenMaya.MFnNumericData.kInt,0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    toggleArray.addAttribute( toggleArray.disableValue )

    toggleArray.outState = nAttr.create( "outState", "oSt", OpenMaya.MFnNumericData.kInt)
    nAttr.setStorable(1)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)
    nAttr.setArray(1)
    nAttr.setUsesArrayDataBuilder(1)    
    toggleArray.addAttribute( toggleArray.outState )

    DriverList = [ toggleArray.numberofOutput, toggleArray.activeIndex, toggleArray.activeValue , toggleArray.disableValue  ]
    link_relashionShip(DriverList,toggleArray.outState )

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, kPluginNodeAuthor, kPluginNodeVersion, "Any")
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