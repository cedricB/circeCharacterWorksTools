'''
########################################################################
#                                                                      #
#             yakisoba.py                                              #
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
        Control several twist joint based on their place along a curve at bind time.
        --> allow non linear distribution along the spline 
        --> compute the correct twist value and output translate/rotate values in a predefined space 

    I N S T A L L A T I O N:
        Copy the "yakisoba.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''


import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "yakisoba"
kPluginNodeId = OpenMaya.MTypeId(0xB5C41127) 

__plug_in__Version = "0.52"
__author = "Bazillou2013"

class yakisoba(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_curve_surface_plugs(self,argList):
        actionData          = argList[0]
        inputNurbsConnected = False

        if actionData.isNull() == False :
            inputNurbsConnected = True
        return inputNurbsConnected
    def update_output_storage(self,uValue_Hdle,output_handle):
        curveParameterCount = uValue_Hdle.elementCount()
        curveParameterList = []
        idxList = []
        #extract parameter value 
        for k in range(curveParameterCount):
            curveParameterList.append(uValue_Hdle.inputValue().asDouble())
            
            idx = uValue_Hdle.elementIndex()
            idxList.append(idx)
            if k != curveParameterCount-1:
                uValue_Hdle.next()
                
        #how many entry do we need add to the current output list?
        cBuilder = output_handle.builder()
        bldChck = cBuilder.elementCount()
        growVal = curveParameterCount-bldChck
        if growVal>0:    
            cBuilder.growArray ( growVal )

        return [curveParameterList, idxList]
    def compute_matrix_from_2_vectors_and_u_Point(self,trX_Mat,trY_Mat,u_Point):
        trZ_Mat = (trX_Mat^trY_Mat).normal();

        matrixValueList = [ trX_Mat.x, trX_Mat.y, trX_Mat.z, 0.0,
        trY_Mat.x, trY_Mat.y, trY_Mat.z, 0.0,
        trZ_Mat.x, trZ_Mat.y, trZ_Mat.z, 0.0,
        u_Point.x,u_Point.y,u_Point.z,u_Point.w ]  

        rotMatrix = OpenMaya.MMatrix()
        utilB = OpenMaya.MScriptUtil()
        utilB.createMatrixFromList( matrixValueList, rotMatrix )

        return rotMatrix.homogenize()
    def compute(self,Plug,Data):
        if Plug.parent() == self.output :
            inputCurveObj           = Data.inputValue( self.inputCurve ).asNurbsCurveTransformed()
            inputRibbonObj          = Data.inputValue( self.inputRibbon ).asNurbsSurfaceTransformed()
            output_handle           = Data.outputArrayValue(self.output)
            
            uValue_Hdle             = Data.inputArrayValue(self.uValue)
            twist_Value             = Data.inputValue(self.twist).asDouble()
            disableRotation_val     = Data.inputValue(self.disableRotation).asBool()

            cBuilder = output_handle.builder()

            InputNurbsConnected = self.check_curve_surface_plugs([inputCurveObj])
            InputRibbonConnected = self.check_curve_surface_plugs([inputRibbonObj])
            if InputNurbsConnected == True and InputRibbonConnected  == True and uValue_Hdle.elementCount() > 0 :
                nrbMFn = OpenMaya.MFnNurbsCurve( inputCurveObj )
                curveLen = nrbMFn.length(0.0001)
                surfMFn = OpenMaya.MFnNurbsSurface( inputRibbonObj )

                start_util = OpenMaya.MScriptUtil()
                start_util.createFromDouble(0.0)
                startPtr = start_util.asDoublePtr()  

                end_util = OpenMaya.MScriptUtil()
                end_util.createFromDouble(0.0)
                endPtr = end_util.asDoublePtr()  
                
                nrbMFn.getKnotDomain(startPtr,endPtr)
                strVal = OpenMaya.MScriptUtil().getDouble(startPtr)
                endVal = OpenMaya.MScriptUtil().getDouble(endPtr)

                locSpace = OpenMaya.MSpace.kObject

                smplePnt = OpenMaya.MPoint()
                
                cvRange =  endVal - strVal
                
                paramData = self.update_output_storage( uValue_Hdle,output_handle)
                idxList   = paramData[1]
                paramList = paramData[0]
                curveParameterCount = len(paramList)
                neutralAim = OpenMaya.MVector.xAxis

                for n in range(0,curveParameterCount):
                    currentDH       = cBuilder.addElement(idxList[n])
                    outRotate_DH    = currentDH.child(self.outRotate)
                    outTranslate_DH = currentDH.child(self.outTranslate)   
                    outMatrix_DH    = currentDH.child(self.outMatrix)   
                    outScale_DH    = currentDH.child(self.outScale)   

                    paramValue = 0.0
                    dif_value = 0.0
                    if paramList[n] < strVal:
                        paramValue = strVal
                        dif_value = paramList[n]
                    elif paramList[n] > endVal:
                        paramValue = endVal
                        dif_value = paramList[n]-endVal
                    else:
                        paramValue = paramList[n]

                    nrbMFn.getPointAtParam(paramValue,smplePnt,locSpace)
                    
                    if disableRotation_val == False:
                        #get Twist percentage
                        localTwist = ((paramValue-strVal) /cvRange) * twist_Value                
                        
                        currentTwist = math.radians(localTwist )
                        twistMat = OpenMaya.MEulerRotation(currentTwist,0,0, 0).asMatrix()
    
                        # compute rotational value :
                        aimVector       = nrbMFn.tangent(paramValue,locSpace) 
                        normalUP_vector = surfMFn.normal(0.5,paramValue,locSpace) 
                        rotMat = self.compute_matrix_from_2_vectors_and_u_Point(aimVector,normalUP_vector,smplePnt)
                        
                        finalMat = twistMat*rotMat
                        outMatrix_DH.setMMatrix(finalMat)
                        matFn = OpenMaya.MTransformationMatrix(finalMat) 
    
                        blendRot    = matFn.eulerRotation() 
                        outRotate_DH.set3Double(blendRot.x,blendRot.y,blendRot.z)
                        outRotate_DH.setClean()

                    if dif_value != 0.0:
                        offset = OpenMaya.MPoint(dif_value,0,0)*rotMat
                        outTranslate_DH.set3Double(offset.x,offset.y,offset.z) 
                        outTranslate_DH.setClean()
                    else:
                        outTranslate_DH.set3Double(smplePnt.x,smplePnt.y,smplePnt.z) 
                        outTranslate_DH.setClean()
                output_handle.set(cBuilder)
                output_handle.setAllClean()
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(yakisoba())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()

    #input worldMesh curve
    yakisoba.inputCurve = typed_Attr.create( "inputCurve", "inCv", OpenMaya.MFnNurbsCurveData.kNurbsCurve )
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    yakisoba.addAttribute( yakisoba.inputCurve )
    
    yakisoba.inputRibbon = typed_Attr.create( "inputRibbon", "inrb", OpenMaya.MFnNurbsCurveData.kNurbsSurface )
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    yakisoba.addAttribute( yakisoba.inputRibbon )
    
    yakisoba.uValue = nAttr.create( "uValue", "uVl", OpenMaya.MFnNumericData.kDouble,0 )
    nAttr.setArray(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)
    nAttr.setMin(0.0)
    yakisoba.addAttribute( yakisoba.uValue )
    
    yakisoba.disableRotation = nAttr.create( "disableRotation", "dRot", OpenMaya.MFnNumericData.kBoolean,0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    yakisoba.addAttribute( yakisoba.disableRotation )
    
    yakisoba.twist = nAttr.create( "twist", "tw", OpenMaya.MFnNumericData.kDouble,0 )
    nAttr.setKeyable(1)
    yakisoba.addAttribute( yakisoba.twist) 

    #---------------------------------------------------------------------------- Output Attributes
    defaultAngle = OpenMaya.MAngle ( 0.0, OpenMaya.MAngle.kDegrees )
    defaultDist  = OpenMaya.MDistance ( 0.0, OpenMaya.MDistance.kCentimeters )
    
    yakisoba.outRotateX = unitAttr.create( "outRotateX", "orx", defaultAngle)
    yakisoba.outRotateY = unitAttr.create( "outRotateY", "ory", defaultAngle)
    yakisoba.outRotateZ = unitAttr.create( "outRotateZ", "orz", defaultAngle)
    yakisoba.outRotate = nAttr.create( "outRotate", "oRot",yakisoba.outRotateX,yakisoba.outRotateY,yakisoba.outRotateZ)

    yakisoba.outTranslateX = unitAttr.create( "outTranslateX", "otx", defaultDist)
    yakisoba.outTranslateY = unitAttr.create( "outTranslateY", "oty", defaultDist)
    yakisoba.outTranslateZ = unitAttr.create( "outTranslateZ", "otz", defaultDist)
    yakisoba.outTranslate = nAttr.create( "outTranslate", "oTrn",yakisoba.outTranslateX,yakisoba.outTranslateY,yakisoba.outTranslateZ)

    yakisoba.outMatrix = matAttr.create("outMatrix", "oMat",OpenMaya.MFnMatrixAttribute.kDouble)
    yakisoba.outScale = nAttr.create( "outScale", "outS", OpenMaya.MFnNumericData.k3Double,1.0 )

    yakisoba.output = cAttr.create( "output", "out" )
    cAttr.addChild(yakisoba.outRotate)
    cAttr.addChild(yakisoba.outTranslate)
    cAttr.addChild(yakisoba.outMatrix)
    cAttr.addChild( yakisoba.outScale)

    cAttr.setArray(1)
    cAttr.setStorable(1)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    cAttr.setUsesArrayDataBuilder(1)
    yakisoba.addAttribute(yakisoba.output) 

    yakisoba.attributeAffects( yakisoba.inputCurve , yakisoba.output )
    yakisoba.attributeAffects( yakisoba.inputRibbon , yakisoba.output)
    yakisoba.attributeAffects( yakisoba.uValue , yakisoba.output)
    yakisoba.attributeAffects( yakisoba.twist , yakisoba.output)
    yakisoba.attributeAffects( yakisoba.disableRotation , yakisoba.output)
    
    yakisoba.uParameters = typed_Attr.create( "uParameters", "uuPrm", OpenMaya.MFnData.kDoubleArray)
    typed_Attr.setStorable(1)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(1)
    yakisoba.addAttribute(yakisoba.uParameters) 
    
    yakisoba.splineMatrix = typed_Attr.create( "splineMatrix", "sMat", OpenMaya.MFnData.kVectorArray)
    typed_Attr.setStorable(1)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(1)
    yakisoba.addAttribute(yakisoba.splineMatrix) 
    
    yakisoba.attributeAffects( yakisoba.inputCurve  , yakisoba.splineMatrix )
    yakisoba.attributeAffects( yakisoba.inputRibbon , yakisoba.splineMatrix )
    yakisoba.attributeAffects( yakisoba.uParameters , yakisoba.splineMatrix )
    yakisoba.attributeAffects( yakisoba.twist       , yakisoba.splineMatrix )


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