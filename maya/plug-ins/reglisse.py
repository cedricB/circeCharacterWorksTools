'''
########################################################################
#                                                                      #
#             reglisse.py                                              #
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
            - The user uses the same type of license
            - credit the original author
            - does not claim patent nor copyright from the original work

    P U R P O S E:
        Sample u data from multiple type of input

    I N S T A L L A T I O N:
        Copy the "reglisse.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "reglisse"
kPluginNodeId = OpenMaya.MTypeId(0xBAC7443) 
kPluginNodeAuthor = "Bazillou2012"
kPluginNodeVersion =  "1.35"

class reglisse(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_curve_surface_plugs(self,actionData,objAttr):
        inputNurbsConnected = False
        nodeObj = self.thisMObject()
        
        depFn = OpenMaya.MFnDependencyNode(nodeObj)
        inPlug = depFn.findPlug(objAttr,False) 
        if inPlug.isConnected() == False:
            return inputNurbsConnected
        if actionData.isNull() == False :
            inputNurbsConnected = True
        return inputNurbsConnected
    def collect_samplePoints(self,input_Hdle):
        knotCount = input_Hdle.elementCount() 
        knotPointList = OpenMaya.MPointArray(knotCount,OpenMaya.MPoint())
        
        for k in range(knotCount):
            currentPnt = OpenMaya.MPoint()*input_Hdle.inputValue().asMatrix()

            knotPointList.set(currentPnt,k)
            if k != knotCount-1:
                input_Hdle.next()
        
        return knotPointList

    def compute(self,Plug,Data): 
        if Plug == self.uParameters :
            #Layout necessary output / input handle to gather data      
            inputCurveObj       = Data.inputValue( self.sampleCurve  ).asNurbsCurveTransformed()            
            curveChck           = self.check_curve_surface_plugs(inputCurveObj,'sampleCurve' )
            uParameters_handle  =  Data.outputValue(self.uParameters )

            if curveChck == False:
                return  
            else:
                inputMatrix_Hdle    = Data.inputArrayValue(self.inputMatrix)
                inMeshObj           = Data.inputValue( self.inMesh  ).asMeshTransformed()
                inMeshChck           = self.check_curve_surface_plugs(inMeshObj,'inMesh' )

                knotPointList = OpenMaya.MPointArray()
                knotCount = 0

                if inMeshChck == True:
                    mshFn   = OpenMaya.MFnMesh(inMeshObj)                
                    mshFn.getPoints(knotPointList,OpenMaya.MSpace.kObject)
                    knotCount = knotPointList.length()
                    
                else:
                    knotCount = inputMatrix_Hdle.elementCount()    
                    knotPointList = self.collect_samplePoints(inputMatrix_Hdle )
                
                if knotCount == 0:
                    return  
                else:                  
                    nrbMFn = OpenMaya.MFnNurbsCurve( inputCurveObj )

                    ulist = OpenMaya.MDoubleArray(knotCount,0.0)
                    clstPnt = OpenMaya.MPoint()

                    uParam = OpenMaya.MScriptUtil()
                    uParam.createFromDouble(0)
                    uParamPtr = uParam.asDoublePtr()

                    sortList_val = Data.inputValue( self.sortList  ).asBool()
                    for k in range(knotCount):
                        nrbMFn.closestPoint (knotPointList[k], uParamPtr, 0.0000001, OpenMaya.MSpace.kObject )
                        uValue = OpenMaya.MScriptUtil(uParamPtr).asDouble()
                        ulist.set(uValue,k)

                    if sortList_val == True:
                        u_InAscendingOrder = sorted(ulist)
                        for index, uValue in enumerate(u_InAscendingOrder):
                            ulist.set(uValue,index)

                    DoubleArrayFn   = OpenMaya.MFnDoubleArrayData()
                    outArray        = DoubleArrayFn.create(ulist)
                    uParameters_handle.setMObject(outArray)
                    uParameters_handle.setClean() 

        if Plug == self.segmentParameters   :   #SEGMENT defines unifom division
            segmentParameters_handle  = Data.outputValue(self.segmentParameters ) 
            inputCurveObj       = Data.inputValue( self.sampleCurve  ).asNurbsCurve()
            curveChck           = self.check_curve_surface_plugs(inputCurveObj,'sampleCurve')

            if curveChck == True :
                divVal = Data.inputValue( self.division  ).asInt()
                nrbMFn  = OpenMaya.MFnNurbsCurve( inputCurveObj )

                lenVal = nrbMFn.length (0.0001)
                fDiv    = divVal*1.0                
                ratio   = lenVal/fDiv

                uParameters =  OpenMaya.MDoubleArray(divVal+1)
                for k in range(divVal+1):
                    tmpLEN = nrbMFn.findParamFromLength (k*ratio ) 
                    uParameters.set(tmpLEN,k)

                DoubleArrayFn   = OpenMaya.MFnDoubleArrayData()
                outArray        = DoubleArrayFn.create(uParameters)
                segmentParameters_handle.setMObject(outArray)
                segmentParameters_handle.setClean()    

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(reglisse())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
  
    #General curve input
    reglisse.sampleCurve = typed_Attr.create( "sampleCurve", "sCrv", OpenMaya.MFnNurbsCurveData.kNurbsCurve )
    typed_Attr.setHidden(1)
    reglisse.addAttribute(reglisse.sampleCurve)   
    #---------------------------------------------------------------------------- Input Attributes for U value mode


    reglisse.inputMatrix = matAttr.create("inputMatrix", "inMat",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setArray(1)
    matAttr.setStorable(0)
    matAttr.setKeyable(0)
    matAttr.setHidden(True)
    matAttr.setDisconnectBehavior(OpenMaya.MFnAttribute.kDelete)
    reglisse.addAttribute(reglisse.inputMatrix)
    
    reglisse.inMesh = typed_Attr.create( "inMesh", "inMs", OpenMaya.MFnMeshData.kMesh )
    typed_Attr.setHidden(1)
    reglisse.addAttribute(reglisse.inMesh)   

    reglisse.sortList = nAttr.create( "sortList", "sL", OpenMaya.MFnNumericData.kBoolean,0)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    reglisse.addAttribute(reglisse.sortList )

    #---------------------------------------------------------------------------- Output Attributes
    
    reglisse.uParameters = typed_Attr.create( "uParameters", "uuPrm", OpenMaya.MFnData.kDoubleArray)
    typed_Attr.setHidden(1)
    reglisse.addAttribute(reglisse.uParameters)
    
    reglisse.attributeAffects(reglisse.sampleCurve, reglisse.uParameters)
    reglisse.attributeAffects(reglisse.inputMatrix, reglisse.uParameters)
    reglisse.attributeAffects(reglisse.sortList,    reglisse.uParameters)
    reglisse.attributeAffects(reglisse.inMesh,      reglisse.uParameters)

    # segment mode--------------------------------------------------------------------------------------    
    reglisse.division = nAttr.create( "division", "div", OpenMaya.MFnNumericData.kInt,2)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setSoftMin(2)
    nAttr.setSoftMax(500)
    reglisse.addAttribute(reglisse.division )

    reglisse.segmentParameters = typed_Attr.create( "segmentParameters", "sgPrm", OpenMaya.MFnData.kDoubleArray)
    typed_Attr.setHidden(1)
    reglisse.addAttribute(reglisse.segmentParameters)
    reglisse.attributeAffects(reglisse.sampleCurve, reglisse.segmentParameters)
    reglisse.attributeAffects(reglisse.division, reglisse.segmentParameters) 

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject,kPluginNodeAuthor, kPluginNodeVersion, "Any")
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