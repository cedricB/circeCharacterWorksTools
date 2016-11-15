'''
########################################################################
#                                                                      #
#             twistReader.py                                           #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        1. The MIT License (MIT)
        Copyright (c) 2009-2015 Cedric BAZILLOU cedricbazillou@gmail.com
        Permission is hereby granted, free of charge, to any person obtaining a copy of this software
        and associated documentation files (the "Software"), to deal in the Software without restriction,
        including without limitation the rights to use, copy, modify, merge, publish, distribute,
        sub-license, and/or sell copies of the Software, and to permit persons
        to whom the Software is furnished to do so, subject to the following conditions:
            The above copyright notice and this permission notice shall be included in all copies	     
            or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
        INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,TORT OR OTHERWISE,
        ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    P U R P O S E:
        - use quaternion to build a reliable reference space
        - this space will be use against a target matrix to extract a signed  twist values

    I N S T A L L A T I O N:
        Copy the "twistReader.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''
__plug_in__Version = "0.15.2"
__author = "Bazillou2013"

import math 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "twistReader"
kPluginNodeId = OpenMaya.MTypeId(0x1CB7138) 


class twistReader(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def extract_plane_twist(self, aimMatrix):
        twist_Normal = OpenMaya.MVector.yAxis*aimMatrix
        angleOutput = OpenMaya.MVector.yAxis.angle(twist_Normal)

        if twist_Normal.z > 0.0:
            angleOutput *= -1.0

        return math.degrees(angleOutput)

    def compute(self,Plug,Data):
        refMatrixValue = Data.inputValue(self.refMatrix).asMatrix()
        driverMatrixValue = Data.inputValue(self.driverMatrix).asMatrix()
        spaceMode = int(Data.inputValue(self.aimSpace).asShort())

        refMatrixRotValue = OpenMaya.MTransformationMatrix(refMatrixValue).asRotateMatrix() 
        driverMatrixRotValue = OpenMaya.MTransformationMatrix(driverMatrixValue).asRotateMatrix() 

        aimVector = (OpenMaya.MVector(1,0,0)*driverMatrixRotValue*refMatrixRotValue.inverse()).normal()
        referenceVector = OpenMaya.MVector(1,0,0)

        aimQuaternion = OpenMaya.MQuaternion()
        aimMatrix = referenceVector.rotateTo(aimVector).asMatrix()
        aimMatrixInWorldSpace = aimMatrix * refMatrixValue

        twistValue = self.extract_plane_twist(aimMatrixInWorldSpace * driverMatrixValue.inverse())

        if spaceMode == 0:
            eulerRotationValue = OpenMaya.MTransformationMatrix(aimMatrixInWorldSpace).eulerRotation()
        elif spaceMode == 1:
            eulerRotationValue = OpenMaya.MTransformationMatrix(aimMatrix).eulerRotation()
        elif spaceMode == 2:
            eulerRotationValue = OpenMaya.MEulerRotation(-math.radians(twistValue),0,0)

        outputHandle = Data.outputValue(self.outRotate)
        outputHandle.set3Double(eulerRotationValue.x,
                                eulerRotationValue.y,
                                eulerRotationValue.z)

        outputTwistHandle = Data.outputValue(self.outTwist)
        outputTwistHandle.setDouble(twistValue)

        outputTwistHandle.setClean()
        outputHandle.setClean()

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(twistReader())


def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    mode_Attr =  OpenMaya.MFnEnumAttribute()

    twistReader.aimSpace = mode_Attr.create( "aimSpace", "aim",  0)
    mode_Attr.addField("world",0)
    mode_Attr.addField("reference",1)
    mode_Attr.addField("driver",2)
    mode_Attr.setKeyable(1)
    mode_Attr.setHidden(0)
    twistReader.addAttribute(twistReader.aimSpace)


    twistReader.parentMatrix = matAttr.create("parentMatrix", "pMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setStorable(1)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    twistReader.addAttribute(twistReader.parentMatrix)

    defaultAngle = OpenMaya.MAngle(0.0, OpenMaya.MAngle.kDegrees)

    twistReader.inRotateX = unitAttr.create("inRotateX", "irx", defaultAngle)
    twistReader.inRotateY = unitAttr.create("inRotateY", "iry", defaultAngle)
    twistReader.inRotateZ = unitAttr.create("inRotateZ", "irz", defaultAngle)

    twistReader.inRotate = nAttr.create("inRotate", 
                                        "ir", 
                                        twistReader.inRotateX,
                                        twistReader.inRotateY,
                                        twistReader.inRotateZ)

    twistReader.refMatrix = matAttr.create("refMatrix", "rMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setStorable(0)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    matAttr.setAffectsWorldSpace(True)
    twistReader.addAttribute(twistReader.refMatrix)

    twistReader.driverMatrix = matAttr.create("driverMatrix", "drMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setStorable(0)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    matAttr.setAffectsWorldSpace(True)
    twistReader.addAttribute(twistReader.driverMatrix)

    #---------------------------------------------------------------------------- Output Attributes

    twistReader.outRotateX = unitAttr.create("outRotateX", "orx", defaultAngle)
    twistReader.outRotateY = unitAttr.create("outRotateY", "ory", defaultAngle)
    twistReader.outRotateZ = unitAttr.create("outRotateZ", "orz", defaultAngle)

    twistReader.outRotate = nAttr.create("outRotate",  
                                         "or",
                                         twistReader.outRotateX, 
                                         twistReader.outRotateY, 
                                         twistReader.outRotateZ)

    nAttr.setStorable(1)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)   
    #nAttr.setWritable(0) 
    twistReader.addAttribute(twistReader.outRotate )

    twistReader.attributeAffects(twistReader.refMatrix, twistReader.outRotate)
    twistReader.attributeAffects(twistReader.driverMatrix, twistReader.outRotate)
    twistReader.attributeAffects(twistReader.parentMatrix, twistReader.outRotate)
    twistReader.attributeAffects(twistReader.aimSpace, twistReader.outRotate)

    twistReader.outTwist = nAttr.create("outTwist", "oTw", OpenMaya.MFnNumericData.kDouble, 0.0 )
    nAttr.setStorable(1)
    nAttr.setHidden(0)
    #nAttr.setWritable(0) 
    twistReader.addAttribute( twistReader.outTwist)

    twistReader.attributeAffects(twistReader.refMatrix, twistReader.outTwist)
    twistReader.attributeAffects(twistReader.driverMatrix, twistReader.outTwist)
    twistReader.attributeAffects(twistReader.parentMatrix, twistReader.outTwist)
    twistReader.attributeAffects(twistReader.aimSpace, twistReader.outTwist)

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, __author, __plug_in__Version, "Any")
    try:
        mplugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeName ); raise


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName ); raise