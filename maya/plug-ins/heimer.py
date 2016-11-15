'''
########################################################################
#                                                                      #
#             heimer.py                                                #
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
        - compute an aim constraint without using any up vector
        - use quaternion to build a reliable  orientation

    I N S T A L L A T I O N:
        Copy the "heimer.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
 @author Cedric Bazillou <cedric.bazillou@digital-district.ca>
 @blog  http://circecharacterworks.wordpress.com/
 @note version 0.1.0
 @see  see statement goes here.
'''


import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "heimer"
kPluginNodeId = OpenMaya.MTypeId(0xAAC0F775) 
kPluginNodeAuthor = "Bazillou cedric2009"
kPluginNodeVersion = "1.0.1"


class heimer(OpenMayaMPx.MPxNode):
    referenceVector = OpenMaya.MVector(1,0,0)
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def computeLocalOrient(self,Data):
        worldToLocalValue = Data.inputValue(self.worldToLocal).asMatrix()
        targetPosition_Hdle = Data.inputValue(self.targetPosition)
        parentHandle = Data.outputValue(self.local)
        outputHandle = parentHandle.child(self.outRotate)

        inVec = targetPosition_Hdle.asVector()
        pointCnv = OpenMaya.MPoint(inVec)*worldToLocalValue.inverse()
        theTargetVector = OpenMaya.MVector(pointCnv).normal()
        aimQuaternion = self.referenceVector.rotateTo(theTargetVector)
        eulerRotationValue = aimQuaternion.asEulerRotation()

        outputHandle.set3Double( eulerRotationValue.x,eulerRotationValue.y,eulerRotationValue.z )                
        parentHandle.setClean()

    def computeWorldData(self,Data):
        worldToLocalValue   = Data.inputValue(self.worldToLocal).asMatrix()
        targetMatrixValue   = Data.inputValue(self.targetMatrix).asMatrix()

        parentHandle        = Data.outputValue(self.world)
        outRotate_DH        = parentHandle.child(self.rotate )
        outTranslate_DH     = parentHandle.child(self.translate)
        outMatrix_DH        = parentHandle.child(self.outMatrix)  
        
        convertWorldToLocal_Value = Data.inputValue(self.convertWorldToLocal).asBool()

        worldMat = worldToLocalValue.inverse()
        pointCnv = OpenMaya.MPoint()*targetMatrixValue*worldMat
        theTargetVector = OpenMaya.MVector(pointCnv).normal()            
        aimMatrix = self.referenceVector.rotateTo(theTargetVector).asMatrix()
        finalMat =  aimMatrix*worldToLocalValue
        
        if convertWorldToLocal_Value == True:
            finalMat =  aimMatrix
        
        matFn = OpenMaya.MTransformationMatrix(finalMat) 
        blendRot    = matFn.eulerRotation() 
        outRotate_DH.set3Double(blendRot.x,blendRot.y,blendRot.z)
        
        outPnt = OpenMaya.MPoint()*finalMat
        outTranslate_DH.set3Double(outPnt.x,outPnt.y,outPnt.z) 
        
        outMatrix_DH.setMMatrix(finalMat)
        parentHandle.setClean()

    def compute(self,Plug,Data):
        self.computeLocalOrient(Data)
        self.computeWorldData(Data)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(heimer())

def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()

    heimer.worldToLocal = matAttr.create("worldToLocal", "wtlMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setHidden(True)
    heimer.addAttribute(heimer.worldToLocal)
    
    heimer.targetMatrix = matAttr.create("targetMatrix", "trgMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setHidden(True)
    heimer.addAttribute(heimer.targetMatrix)

    heimer.targetPosition = nAttr.create( "targetPosition", "trgPos", OpenMaya.MFnNumericData.k3Double )
    nAttr.setStorable(0)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    heimer.addAttribute( heimer.targetPosition )

    defaultAngle = OpenMaya.MAngle ( 0.0, OpenMaya.MAngle.kDegrees )
    defaultDist  = OpenMaya.MDistance ( 0.0, OpenMaya.MDistance.kCentimeters )

    heimer.outRotateX = unitAttr.create( "outRotateX", "orx", defaultAngle)
    heimer.outRotateY = unitAttr.create( "outRotateY", "ory", defaultAngle)
    heimer.outRotateZ = unitAttr.create( "outRotateZ", "orz", defaultAngle)
    heimer.outRotate = nAttr.create( "outRotate", "or", heimer.outRotateX,heimer.outRotateY,heimer.outRotateZ)
    
    heimer.local = cAttr.create( "local", "lcl" )
    cAttr.addChild(heimer.outRotate)
    cAttr.setStorable(0)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    heimer.addAttribute(heimer.local) 
    
    heimer.translateX = unitAttr.create( "translateX", "tx", defaultDist)
    heimer.translateY = unitAttr.create( "translateY", "ty", defaultDist)
    heimer.translateZ = unitAttr.create( "translateZ", "tz", defaultDist)
    heimer.translate = nAttr.create( "translate", "t",heimer.translateX,heimer.translateY,heimer.translateZ)
    
    heimer.rotateX = unitAttr.create( "rotateX", "rx", defaultAngle)
    heimer.rotateY = unitAttr.create( "rotateY", "ry", defaultAngle)
    heimer.rotateZ = unitAttr.create( "rotateZ", "rz", defaultAngle)
    heimer.rotate = nAttr.create( "rotate", "r", heimer.rotateX,heimer.rotateY,heimer.rotateZ)
    
    heimer.outMatrix = matAttr.create("outMatrix", "oMat",OpenMaya.MFnMatrixAttribute.kDouble)
    heimer.outScale = nAttr.create( "outScale", "outS", OpenMaya.MFnNumericData.k3Double,1.0 )
    
    heimer.convertWorldToLocal = nAttr.create( "convertWorldToLocal", "cnv", OpenMaya.MFnNumericData.kBoolean,False )
    heimer.addAttribute(heimer.convertWorldToLocal) 
    
    heimer.world = cAttr.create( "world", "wrl" )
    cAttr.addChild(heimer.rotate)
    cAttr.addChild(heimer.translate)
    cAttr.addChild( heimer.outScale)
    cAttr.addChild(heimer.outMatrix)
    cAttr.setStorable(0)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    heimer.addAttribute(heimer.world) 

    heimer.attributeAffects( heimer.convertWorldToLocal , heimer.local )
    heimer.attributeAffects( heimer.targetPosition, heimer.local )
    heimer.attributeAffects( heimer.worldToLocal  , heimer.local )
    heimer.attributeAffects( heimer.targetMatrix  , heimer.local )

    heimer.attributeAffects( heimer.worldToLocal        , heimer.world )
    heimer.attributeAffects( heimer.targetMatrix        , heimer.world )
    heimer.attributeAffects( heimer.convertWorldToLocal , heimer.world )
    
    return
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





