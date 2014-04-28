'''
########################################################################
#                                                                      #
#             twistKnot.py                                             #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        Copyright (c) 2014 Cedric BAZILLOU All rights reserved.
        
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
        - compute an aim constraint without using any up vector
        - use quaternion to build a reliable  orientation

    I N S T A L L A T I O N:
        Copy the "twistKnot.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''
__plug_in__Version = "0.15.2"
__author = "Bazillou2013"

import math 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "twistKnot"
kPluginNodeId = OpenMaya.MTypeId(0x1CB7131) 

       


class twistKnot(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self,Plug,Data):
        refMatrixValue          = Data.inputValue(self.refMatrix).asMatrix()
        driverMatrixValue       = Data.inputValue(self.driverMatrix).asMatrix()
        
        aimVector = (OpenMaya.MVector(1,0,0)*driverMatrixValue*refMatrixValue.inverse()).normal()
        referenceVector = OpenMaya.MVector(1,0,0)

        aimQuaternion = OpenMaya.MQuaternion()
        aimMat = referenceVector.rotateTo(aimVector).asMatrix() 
        
        newMat = aimMat #*refMatrixValue
        eulerRotationValue = OpenMaya.MTransformationMatrix(newMat).eulerRotation()
        
        outputHandle = Data.outputValue(self.outRotate )
        outputHandle.set3Double( eulerRotationValue.x,eulerRotationValue.y,eulerRotationValue.z )
            
        Data.setClean(Plug)
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(twistKnot())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()

    
    twistKnot.refMatrix = matAttr.create("refMatrix", "rMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setStorable(1)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    twistKnot.addAttribute(twistKnot.refMatrix)

    twistKnot.driverMatrix = matAttr.create("driverMatrix", "drMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setStorable(1)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    twistKnot.addAttribute(twistKnot.driverMatrix)

    #---------------------------------------------------------------------------- Output Attributes
    defaultAngle = OpenMaya.MAngle ( 0.0, OpenMaya.MAngle.kDegrees )
    twistKnot.outRotateX = unitAttr.create( "outRotateX", "orx", defaultAngle)
    twistKnot.outRotateY = unitAttr.create( "outRotateY", "ory", defaultAngle)
    twistKnot.outRotateZ = unitAttr.create( "outRotateZ", "orz", defaultAngle)
    twistKnot.outRotate = nAttr.create( "outRotate", "or", twistKnot.outRotateX,twistKnot.outRotateY,twistKnot.outRotateZ)
    nAttr.setStorable(1)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)
    twistKnot.addAttribute( twistKnot.outRotate )

    twistKnot.attributeAffects( twistKnot.refMatrix, twistKnot.outRotate)
    twistKnot.attributeAffects( twistKnot.driverMatrix, twistKnot.outRotate)

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