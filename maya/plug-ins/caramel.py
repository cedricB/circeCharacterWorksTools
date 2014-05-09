'''
########################################################################
#                                                                      #
#             caramel.py                                        #
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
        Trigger an array of pose space helper/blendshape

    I N S T A L L A T I O N:
        Copy the "caramel.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "caramel"
kPluginNodeId = OpenMaya.MTypeId(0xF1C473) 
kPluginVersion = "1.285"
kPluginAuthor = "Bazillou2012"


outFn = OpenMaya.MFnNurbsSurface()
surfDataFn = OpenMaya.MFnNurbsSurfaceData()

class caramel(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_curve_surface_plugs(self,argList):
        actionData          = argList[0]
        inputNurbsConnected = False

        if actionData.isNull() == False :
            inputNurbsConnected = True
        return inputNurbsConnected
    def compute_knotData(self,input_Hdle,size_Value ):
        knotMatrixList = []
        knotSmoothList = OpenMaya.MDoubleArray()
        hdleSizeList = []
        aimMatB = 0
        knotCount = input_Hdle.elementCount() 
        for k in range(knotCount):
            knotMatrix_value = input_Hdle.inputValue().asMatrix()
            knotMatrixList.append(knotMatrix_value )
            if k != knotCount-1:
                input_Hdle.next()
        return knotMatrixList
    def computKnotList (self,degreeN ,vertLen):
        #degree N with M span
        #The number of knots required for a curve is M + 2N - 1
        
        path_knots = OpenMaya.MDoubleArray()

        spansM  = float(vertLen-degreeN)
        ispans = vertLen-degreeN

        for k in range(degreeN-1):
            path_knots.append(0.0)

        for k in range(ispans +1) :
            path_knots.append(k)
            
        for k in range(degreeN-1):
            path_knots.append(spansM)


        return path_knots
    def compute(self,Plug,Data):
        if Plug == self.output or  Plug == self.outputCurve or Plug == self.profil:
            #Layout necessary output / input handle to gather data
            input_Hdle                  = Data.inputArrayValue(self.input)

            knotCount = input_Hdle.elementCount()            
            if knotCount > 0:
                output_handle               = Data.outputValue(self.output)
                size_Value                  = Data.inputValue(self.size).asDouble()
                width_Value                 = Data.inputValue(self.width).asDouble()
                curveDegree_Value           = Data.inputValue(self.curveDegree).asInt()
                outputCurveDegree_Value     = curveDegree_Value

                knotMatrixList = self.compute_knotData(input_Hdle,size_Value )                

                neutralPoint = OpenMaya.MPoint(0,0,0)
                PointA = OpenMaya.MPoint(0,0,width_Value)
                PointB = OpenMaya.MPoint(0,0,-width_Value)
                
                pointListA = OpenMaya.MPointArray()
                pointListB = OpenMaya.MPointArray()
                if len(knotMatrixList) > 1: 
                    pointListA.append(PointA*knotMatrixList[0])
                    pointListB.append(PointB*knotMatrixList[0])
                    
                    if len(knotMatrixList) > 2:
                        for k in range(1,len(knotMatrixList)):
                            pointListA.append(PointA*knotMatrixList[k])
                            pointListB.append(PointB*knotMatrixList[k])
                knotList = self.computKnotList(outputCurveDegree_Value,pointListA.length())

                newOutputObj = surfDataFn.create()  
                
                uKnotSequences = OpenMaya.MDoubleArray()
                vKnotSequences = OpenMaya.MDoubleArray()
                
                uKnotSequences.append(0.0)
                uKnotSequences.append(1.0)

                controlVertices = OpenMaya.MPointArray()
                
                for k in range(pointListB.length()):
                    controlVertices.append(pointListB[k])
                for k in range(pointListA.length()):
                    controlVertices.append(pointListA[k])

                outDegree = curveDegree_Value
                if Plug == self.output :
                    for k in range(knotList.length()):
                        vKnotSequences.append(knotList[k])
    
    
                    outFn.create ( controlVertices, uKnotSequences,vKnotSequences,     1, outDegree,
                    OpenMaya.MFnNurbsSurface.kOpen , OpenMaya.MFnNurbsSurface.kOpen ,True,    newOutputObj)
                    
                    
                    output_handle.setMObject(newOutputObj)
                    output_handle.setClean()
                if Plug == self.outputCurve:
                    output_Handle = Data.outputValue(self.outputCurve)
                    
                    outputCurveFn = OpenMaya.MFnNurbsCurve()
                    crvDatStock = OpenMaya.MFnNurbsCurveData()
                    crbOBJ = crvDatStock.create()
                    outputCurveFn = OpenMaya.MFnNurbsCurve()
                    
                    cv_pointList = OpenMaya.MPointArray(pointListA.length())
                    for k in range(pointListA.length()):
                        cv_pointList.set(pointListA[k] + (pointListB[k] - pointListA[k])*0.5, k)


                    outputCurveFn.create( cv_pointList , knotList, outDegree,OpenMaya.MFnNurbsCurve.kOpen, False, False,  crbOBJ )
                    output_Handle.setMObject(crbOBJ)
                    output_Handle.setClean()  
                #------------------------------------------------------------------------------------------------------
                if Plug == self.profil:
                    aimMat = OpenMaya.MMatrix()
                    if orientHandle_Value == True:
                        neutralPnt = OpenMaya.MPoint()
                        pointA = neutralPnt*knotMatrixList[0]
                        pointB = neutralPnt*knotMatrixList[1]
                        
                        offsetVecB = pointB*knotMatrixList[0].inverse() - pointA*knotMatrixList[0].inverse()
                
                        theTargetVector = offsetVecB.normal()
                        referenceVector = OpenMaya.MVector(1,0,0)
                
                        aimQuaternion = referenceVector.rotateTo(theTargetVector)
                        neutralQuat = OpenMaya.MQuaternion()
                        
                        
                        aimMat = aimQuaternion.asMatrix()                      

                    output_Handle = Data.outputValue(self.profil)
                    
                    outputCurveFn = OpenMaya.MFnNurbsCurve()
                    crvDatStock = OpenMaya.MFnNurbsCurveData()
                    crbOBJ = crvDatStock.create()
                    outputCurveFn = OpenMaya.MFnNurbsCurve()
                    
                    cv_pointList = OpenMaya.MPointArray()
                    cv_pointList.append(OpenMaya.MPoint(0,0,width_Value*-0.5)*aimMat )
                    cv_pointList.append(OpenMaya.MPoint(0,0,width_Value*0.5)*aimMat )
                    outputCurveFn.createWithEditPoints(cv_pointList , 1,OpenMaya.MFnNurbsCurve.kOpen, False, False, True, crbOBJ )
                    output_Handle.setMObject(crbOBJ)
                    output_Handle.setClean()  
            else:
                return 

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(caramel())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    
    #---------------------------------------------------------------------------- Input Attributes


    caramel.input = matAttr.create("input", "in",OpenMaya.MFnMatrixAttribute.kDouble)
    matAttr.setArray(1)
    matAttr.setStorable(0)
    matAttr.setKeyable(0)
    matAttr.setHidden(1)
    caramel.addAttribute(caramel.input)
    
    caramel.width = nAttr.create("width","wdt", OpenMaya.MFnNumericData.kDouble,0.2)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setReadable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0.001)
    nAttr.setSoftMax(20.0)
    caramel.addAttribute(caramel.width)
    
    caramel.curveDegree = nAttr.create("curveDegree","cDg", OpenMaya.MFnNumericData.kInt,2)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setReadable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(1)
    nAttr.setMax(3)
    caramel.addAttribute(caramel.curveDegree)
    
    caramel.size = nAttr.create("size","sz", OpenMaya.MFnNumericData.kDouble,1.0)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setReadable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0.001)
    nAttr.setSoftMax(2.0)
    caramel.addAttribute(caramel.size)

    #---------------------------------------------------------------------------- Output Attributes
    caramel.output = typed_Attr.create( "output", "out", OpenMaya.MFnData.kNurbsSurface)
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    caramel.addAttribute(caramel.output) 

    caramel.attributeAffects( caramel.input               , caramel.output )
    caramel.attributeAffects( caramel.width               , caramel.output )
    caramel.attributeAffects( caramel.size                , caramel.output )
    caramel.attributeAffects( caramel.curveDegree        , caramel.output )

    #---------------------------------------------------------------------------- Output Attributes
    caramel.outputCurve = typed_Attr.create( "outputCurve", "outCrv", OpenMaya.MFnData.kNurbsCurve)
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    caramel.addAttribute(caramel.outputCurve) 

    caramel.attributeAffects( caramel.input               , caramel.outputCurve )
    caramel.attributeAffects( caramel.width               , caramel.outputCurve )
    caramel.attributeAffects( caramel.size                , caramel.outputCurve )
    caramel.attributeAffects( caramel.curveDegree        , caramel.outputCurve )

    caramel.profil = typed_Attr.create( "profil", "prf", OpenMaya.MFnNurbsCurveData.kNurbsCurve )
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    caramel.addAttribute( caramel.profil )

    caramel.attributeAffects( caramel.input               , caramel.profil )
    caramel.attributeAffects( caramel.width               , caramel.profil )
    caramel.attributeAffects( caramel.size                , caramel.profil )
    caramel.attributeAffects( caramel.curveDegree        , caramel.profil )
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, kPluginAuthor , kPluginVersion  , "Any")
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