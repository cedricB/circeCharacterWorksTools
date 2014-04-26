'''
########################################################################
#                                                                      #
#             heimer.py                                                #
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
        Copy the "heimer.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''


import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "heimer"
kPluginNodeId = OpenMaya.MTypeId(0xAAC0F775) 
kPluginNodeAuthor = "Bazillou cedric2009"
kPluginNodeVersion = "1.0.0"

referenceVector = OpenMaya.MVector(1,0,0)
class heimer(OpenMayaMPx.MPxNode):
    targetPosition  = OpenMaya.MObject()
    rotate          = OpenMaya.MObject() 
 
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def computeLocalOrient(self,Data):
            targetPosition_Hdle = Data.inputValue(self.targetPosition)
            mat_HdleValue       = Data.inputValue(self.worldToLocal).asMatrix()
            parentHandle = Data.outputValue(self.local )
            outputHandle = parentHandle.child(self.outRotate )

            inVec = targetPosition_Hdle.asVector()
            pointCnv = OpenMaya.MPoint(inVec)*mat_HdleValue
            theTargetVector = OpenMaya.MVector(pointCnv).normal()
            aimQuaternion = referenceVector.rotateTo(theTargetVector)
            eulerRotationValue = aimQuaternion.asEulerRotation()

            outputHandle.set3Double( eulerRotationValue.x,eulerRotationValue.y,eulerRotationValue.z )                
            parentHandle.setClean()
            return
    def computeWorldData(self,Data):
            worldToLocalValue   = Data.inputValue(self.worldToLocal).asMatrix()
            targetMatrixValue   = Data.inputValue(self.targetMatrix).asMatrix()
            parentHandle        = Data.outputValue(self.world )
            outRotate_DH        = parentHandle.child(self.rotate )
            outTranslate_DH     = parentHandle.child(self.translate)
            outMatrix_DH        = parentHandle.child(self.outMatrix)   

            worldMat = worldToLocalValue.inverse()
            pointCnv = OpenMaya.MPoint()*targetMatrixValue*worldToLocalValue
            theTargetVector = OpenMaya.MVector(pointCnv).normal()            
            aimMatrix = referenceVector.rotateTo(theTargetVector).asMatrix()
            finalMat =  aimMatrix*worldMat
            
            matFn = OpenMaya.MTransformationMatrix(finalMat) 
            blendRot    = matFn.eulerRotation() 
            outRotate_DH.set3Double(blendRot.x,blendRot.y,blendRot.z)
            
            outPnt = OpenMaya.MPoint()*finalMat
            outTranslate_DH.set3Double(outPnt.x,outPnt.y,outPnt.z) 
            
            outMatrix_DH.setMMatrix(finalMat)
            parentHandle.setClean()
    def trigger_from_output_attributes(self,Plug):
        attribuleList = [self.local,self.world]
        trigger = 0
        idxList = []
        
        for k in range(len(attribuleList)):
            if Plug.parent()  == attribuleList[k]:
                trigger += 1
                idxList.append(k)
        
        return [trigger,idxList]
    def compute(self,Plug,Data):
        triggerData = self.trigger_from_output_attributes(Plug)
        triggerState = triggerData[0]
        
        if triggerState == 0 :
            return
        else:
            if 0 in  triggerData[1] :
                self.computeLocalOrient( Data)
            if 1 in  triggerData[1] :
                self.computeWorldData( Data)
            return 
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
    
    heimer.world = cAttr.create( "world", "wrl" )
    cAttr.addChild(heimer.rotate)
    cAttr.addChild(heimer.translate)
    cAttr.addChild( heimer.outScale)
    cAttr.addChild(heimer.outMatrix)
    cAttr.setStorable(0)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    heimer.addAttribute(heimer.world) 

    heimer.attributeAffects( heimer.targetPosition, heimer.local )
    heimer.attributeAffects( heimer.worldToLocal, heimer.local )
    

    heimer.attributeAffects( heimer.worldToLocal, heimer.world )
    heimer.attributeAffects( heimer.targetMatrix, heimer.world )
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





