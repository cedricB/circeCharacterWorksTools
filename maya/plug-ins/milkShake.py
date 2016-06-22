'''
########################################################################
#                                                                      #
#             milkShake.py                                             #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        Copyright (c) 2013 Cedric BAZILLOU All rights reserved.
        
        Permission is hereby granted   to
            -to modify the file
            -distribute
            -share
            -do derivative work  

        The above copyright notice and this permission notice shall be included in all copies of the Software 
        and is subject to the following conditions:
            - These user uses the same type of license
            - credit the original author
            - does not claim patent nor copyright from the original work
            - this plugin is not sold to third parties

    P U R P O S E:
        pairBlend behavior on entire joint hierarchy

    I N S T A L L A T I O N:
        Copy the "milkShake.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''
import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds

kPluginNodeName = "milkShake"
kPluginNodeId = OpenMaya.MTypeId(0xFCB3945) 

__plug_in__Version = "0.18"
__author = "Bazillou2013"

class milkShake(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def slerp(self,a, b, t):
        # slerp from python_in_maya google group
        cos = self.quaternionDot(a, b)
        if cos < 0.0:
            cos = self.quaternionDot(a, b.negateIt())
        theta = math.acos(cos)
        sin = math.sin(theta)

        if sin > 0.001:
            w1 = math.sin((1.0 - t) * theta) / sin
            w2 = math.sin(t * theta) / sin
        else:
            w1 = 1.0 - t
            w2 = t
        aa = OpenMaya.MQuaternion(a)
        bb = OpenMaya.MQuaternion(b)
        aa.scaleIt(w1)
        bb.scaleIt(w2)

        return aa + bb
    def quaternionDot(self,q1, q2):
        return (q1.x * q2.x) + (q1.y * q2.y) + (q1.z * q2.z) + (q1.w * q2.w)
    def blendWithOffset(self,offsetValue,controlValue,scaleMode=False):
        if scaleMode == False:
            blendvalue = [0,0,0]           
            
            for k in range(3):
                blendvalue[k] =  offsetValue[k]+controlValue[k]
            
            return blendvalue
        
        else:
            blendvalue = [1,1,1]           
            
            for k in range(3):
                blendvalue[k] = offsetValue[k] * controlValue[k] 
            
            return blendvalue
    def computeOffsetOrientation(self,offsetValue,controlValue,rotationOrder):
        blendvalue      = [0,0,0]         
        
        offsetMatrix  = OpenMaya.MEulerRotation (offsetValue[0] ,offsetValue[1] ,offsetValue[2] , 0 ).asMatrix()
        controlMatrix = OpenMaya.MEulerRotation (controlValue[0],controlValue[1],controlValue[2], rotationOrder ).asMatrix()

        blendMatrix = controlMatrix*offsetMatrix
        matFn = OpenMaya.MTransformationMatrix(blendMatrix)
        blendRot    = matFn.eulerRotation() 

        blendvalue[0] = blendRot.x
        blendvalue[1] = blendRot.y
        blendvalue[2] = blendRot.z
        
        return blendvalue
    def extractMixValues(self           ,
                         input_handle   ,
                         posResults     ,
                         rotResults     ,
                         sclResults     ,
                         matResults     ,
                         blendCount     ,   
                         Data           ):

        posVector = OpenMaya.MVector()
        rotVector = OpenMaya.MVector()
        sclVector = OpenMaya.MVector()
        
        weight_Val          = Data.inputValue(self.weight).asFloat()
        rotInterpolationVal = Data.inputValue(self.rotInterpolation).asShort()
        weightToApply       = weight_Val
        
        outMat = OpenMaya.MMatrix()
        tempMatrices = OpenMaya.MMatrixArray(blendCount)

        for n in range(0,blendCount):
            #input DATA links
            input_handle.jumpToArrayElement(n)

            input1_Translate_VL         = input_handle.inputValue().child(self.input1_Translate).asFloat3()
            input2_Translate_VL         = input_handle.inputValue().child(self.input2_Translate).asFloat3()  
            input1_Rotate_DH            = input_handle.inputValue().child(self.input1_Rotate)
            input2_Rotate_DH            = input_handle.inputValue().child(self.input2_Rotate)         
            inputScale1_VL              = input_handle.inputValue().child(self.inputScale1).asFloat3()   
            inputScale2_VL              = input_handle.inputValue().child(self.inputScale2).asFloat3()
            
            input1_TranslateOffset_VL         = input_handle.inputValue().child(self.input1_TranslateOffset).asFloat3()
            input2_TranslateOffset_VL         = input_handle.inputValue().child(self.input2_TranslateOffset).asFloat3()
            
            inputScaleOffset1_VL         = input_handle.inputValue().child(self.inputScaleOffset1).asFloat3()
            inputScaleOffset2_VL         = input_handle.inputValue().child(self.inputScaleOffset2).asFloat3()

            input1_RotateOffset_DH            = input_handle.inputValue().child(self.input1_RotateOffset)
            input2_RotateOffset_DH            = input_handle.inputValue().child(self.input2_RotateOffset)
            
            order1  = input_handle.inputValue().child(self.inRotationOrder1).asShort()
            order2  = input_handle.inputValue().child(self.inRotationOrder2).asShort()
            
            #Compute Rotate DATA
            childList1   = [self.input1_RotateX,self.input1_RotateY,self.input1_RotateZ ]
            childList2   = [self.input2_RotateX,self.input2_RotateY,self.input2_RotateZ ]
            
            offset_childList1   = [self.input1_RotateOffsetX,self.input1_RotateOffsetY,self.input1_RotateOffsetZ ]
            offset_childList2   = [self.input2_RotateOffsetX,self.input2_RotateOffsetY,self.input2_RotateOffsetZ ]

            
            offsetValue1     = [input1_RotateOffset_DH.child(offset_childList1[0]).asAngle().value() ,
                                input1_RotateOffset_DH.child(offset_childList1[1]).asAngle().value() ,
                                input1_RotateOffset_DH.child(offset_childList1[2]).asAngle().value() ] 

            controlValue1    = [input1_Rotate_DH.child(childList1[0]).asAngle().value() ,
                                input1_Rotate_DH.child(childList1[1]).asAngle().value() ,
                                input1_Rotate_DH.child(childList1[2]).asAngle().value() ] 

            offsetValue2     = [input2_RotateOffset_DH.child(offset_childList2[0]).asAngle().value() ,
                                input2_RotateOffset_DH.child(offset_childList2[1]).asAngle().value() ,
                                input2_RotateOffset_DH.child(offset_childList2[2]).asAngle().value() ] 

            controlValue2    = [input2_Rotate_DH.child(childList2[0]).asAngle().value() ,
                                input2_Rotate_DH.child(childList2[1]).asAngle().value() ,
                                input2_Rotate_DH.child(childList2[2]).asAngle().value() ] 
        
            
            startRotation = self.computeOffsetOrientation(offsetValue1,controlValue1,order1)
            endRotation   = self.computeOffsetOrientation(offsetValue2,controlValue2,order2)

            blendRotationValues = self. blendOrient(    startRotation       ,
                                                        endRotation         ,
                                                        weight_Val          , 
                                                        rotInterpolationVal )
            
            rotVector.x = blendRotationValues[0]
            rotVector.y = blendRotationValues[1]
            rotVector.z = blendRotationValues[2]     
       
            rotResults.set( rotVector , n )

            #Compute Translate DATA   
            PositionData1 = self.blendWithOffset( input1_TranslateOffset_VL ,input1_Translate_VL)
            PositionData2 = self.blendWithOffset( input2_TranslateOffset_VL ,input2_Translate_VL)   

            blendPositionValues = self. blendposition(  PositionData1 ,
                                                        PositionData2 ,
                                                        weight_Val    )
            
            posVector.x = blendPositionValues[0]
            posVector.y = blendPositionValues[1]
            posVector.z = blendPositionValues[2]                
            posResults.set( posVector , n )
            
            #Compute scale DATA              
            ScaleData1 = self.blendWithOffset( inputScaleOffset1_VL ,inputScale1_VL,scaleMode=True)
            ScaleData2 = self.blendWithOffset( inputScaleOffset2_VL ,inputScale2_VL,scaleMode=True)
       
            blendScaleValues    = self. blendscale( ScaleData1  ,
                                                    ScaleData2  ,
                                                    weight_Val  )
            
            sclVector.x = blendScaleValues[0]
            sclVector.y = blendScaleValues[1]
            sclVector.z = blendScaleValues[2]                
            sclResults.set( sclVector , n )
            

            outMat = OpenMaya.MEulerRotation(rotVector.x, rotVector.y, rotVector.z,0 ).asMatrix()
            matFn = OpenMaya.MTransformationMatrix(outMat)
            matFn.setTranslation(  posVector,OpenMaya.MSpace.kWorld )
        
            matResults.set(matFn.asMatrix() , n )
            tempMatrices.set(matFn.asMatrix() , n )

        
        for n in range(blendCount-1,0,-1):
            outMat = matResults[n]
            #print '##############################################################'
            for j in range(n-1,-1,-1):
                outMat =  outMat*tempMatrices[j]
                #print 'the matrix', n ,'will be concatanated to  matrix', j                
            matResults.set(outMat , n )
    def compute(self,Plug,Data):       
        input_handle           = Data.inputArrayValue(self.input)
        blendCount = input_handle.elementCount()
        if blendCount < 1:
            return

        if Plug.isChild() == True and Plug.parent() == self.output : 
            posResults = OpenMaya.MVectorArray(blendCount)
            rotResults = OpenMaya.MVectorArray(blendCount)
            sclResults = OpenMaya.MVectorArray(blendCount)
            matResults = OpenMaya.MMatrixArray(blendCount)
            
            self.extractMixValues(  input_handle   ,
                                    posResults     ,
                                    rotResults     ,
                                    sclResults     ,
                                    matResults     ,
                                    blendCount     ,
                                    Data           )

            output_handle          = Data.outputArrayValue(self.output)
            cBuilder               = output_handle.builder()  
            
            blendHierarchyValue    = Data.inputValue(self.blendHierarchy).asBool()
            if blendHierarchyValue == True:
                outMat = OpenMaya.MEulerRotation()
                matFn = OpenMaya.MTransformationMatrix()
                tmpPnt = OpenMaya.MPoint()
                posVector = OpenMaya.MVector()

                for n in range(1):
                    outMat.x = rotResults[n].x
                    outMat.y = rotResults[n].y
                    outMat.z = rotResults[n].z
                    
                    tmpPnt.x = posResults[n].x
                    tmpPnt.y = posResults[n].y
                    tmpPnt.z = posResults[n].z

                    tmpPnt *= outMat.asMatrix()
                    posVector.x = tmpPnt.x
                    posVector.y = tmpPnt.y
                    posVector.z = tmpPnt.z

                    posResults.set(posVector,n)
                    
                    matFn.assign(outMat.asMatrix())
                    matFn.setTranslation(posVector,OpenMaya.MSpace.kWorld)
                    matResults.set(matFn.asMatrix(),n)

            #Now write some results
            for n in range(0,blendCount):
                currentDH       = cBuilder.addElement(n)
                outRotate_DH    = currentDH.child(self.outRotate)
                outTranslate_DH = currentDH.child(self.outTranslate)   
                outScale_DH     = currentDH.child(self.outScale)    
                outMatrix_DH    = currentDH.child(self.outMatrix) 
                
                outTranslate_DH.set3Float(posResults[n].x  ,posResults[n].y   ,posResults[n].z)
                outRotate_DH.set3Double(rotResults[n].x    ,rotResults[n].y   ,rotResults[n].z)
                outScale_DH.set3Float(sclResults[n].x      ,sclResults[n].y   ,sclResults[n].z)
                outMatrix_DH.setMMatrix(matResults[n])

            output_handle.set(cBuilder)
            output_handle.setAllClean()

            return 
    def blendposition(  self        ,
                        handle1     ,
                        handle2     ,
                        weight_Val  ): 

        valueList = [0,0,0]      
        if weight_Val == 0.0:
            for k in range(3):
                valueList[k] = handle1[k]
        elif weight_Val == 1.0:
            for k in range(3):
                valueList[k] = handle2[k]
        else:
            for k in range(3):
                startValue = handle1[k]
                reachValue = handle2[k]

                valueList[k] = startValue + (reachValue-startValue)*weight_Val
        return valueList
    def blendscale( self        ,
                    handle1     ,
                    handle2     ,
                    weight_Val  ): 

        valueList = [0,0,0]      
        if weight_Val == 0.0:
            for k in range(3):
                valueList[k] = handle1[k]
        elif weight_Val == 1.0:
            for k in range(3):
                valueList[k] = handle2[k]
        else:
            for k in range(3):
                startValue = handle1[k]-1.0
                reachValue = handle2[k]-1.0

                valueList[k] = 1.0 + ( startValue + (reachValue-startValue)*weight_Val )
        return valueList
    def blendOrient(self        ,
                    handle1     ,
                    handle2     ,
                    weight_Val  ,
                    rotInter    ):

        valueList = [0,0,0]
        
        if weight_Val == 0.0:
            for k in range(3):
                valueList[k] = handle1[k]
        elif weight_Val == 1.0:
            for k in range(3):
                valueList[k] = handle2[k]
        else:
            if rotInter == 0:
                for k in range(3):
                    valueList[k] = handle1[k] + (handle2[k]-handle1[k])*weight_Val
            else:
                        
                startEuler = OpenMaya.MEulerRotation (handle1[0],handle1[1],handle1[2], 0 )
                reachEuler = OpenMaya.MEulerRotation (handle2[0],handle2[1],handle2[2], 0 )
                
                startQuat = startEuler.asQuaternion()
                reachQuat = reachEuler.asQuaternion()
                
                blendQuat   = self.slerp(startQuat,reachQuat,weight_Val)
                blendRot    = blendQuat.asEulerRotation()
    
                valueList[0] = blendRot.x
                valueList[1] = blendRot.y
                valueList[2] = blendRot.z

        return valueList
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(milkShake())
def link_relashionShip( DriverList, driven_Attribute ):
    for driver in DriverList:
        milkShake.attributeAffects(driver,driven_Attribute)
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    enumAttr = OpenMaya.MFnEnumAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()

    milkShake.blendHierarchy = nAttr.create( "blendHierarchy", "bHr", OpenMaya.MFnNumericData.kBoolean,False)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    milkShake.addAttribute( milkShake.blendHierarchy)

    defaultAngle = OpenMaya.MAngle ( 0.0, OpenMaya.MAngle.kDegrees )
    defaultDist  = OpenMaya.MDistance ( 0.0, OpenMaya.MDistance.kCentimeters )
    
    #--> just to keep things simple lets say this node is to be used for the animation rig: and scaling is done with the translate channel
    #--> the node do a basic index matching: if input index is not valid write default value
    #--> behaves like a pairblendNode from input1 to input2
    mode_Attr =  OpenMaya.MFnEnumAttribute()
    milkShake.rotInterpolation = mode_Attr.create( "rotInterpolation", "ri", 0  )
    mode_Attr.addField("euler",0)
    mode_Attr.addField("quaternion",1)
    mode_Attr.setStorable(1)
    mode_Attr.setKeyable(1)
    mode_Attr.setHidden(0)
    milkShake.addAttribute(milkShake.rotInterpolation )
 
    milkShake.weight = nAttr.create( "weight", "w", OpenMaya.MFnNumericData.kFloat,0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    milkShake.addAttribute( milkShake.weight)
    #----------------------------------------------------------------------------------------------- Input Translate Attributes
    milkShake.input1_TranslateOffset = nAttr.create( "input1_TranslateOffset", "in1OTR", OpenMaya.MFnNumericData.k3Float,0)
    milkShake.input2_TranslateOffset = nAttr.create( "input2_TranslateOffset", "in2OTR", OpenMaya.MFnNumericData.k3Float,0)
    
    milkShake.input1_RotateOffsetX = unitAttr.create( "input1_RotateOffsetX", "i1Orx", defaultAngle)
    milkShake.input1_RotateOffsetY = unitAttr.create( "input1_RotateOffsetY", "i1Ory", defaultAngle)
    milkShake.input1_RotateOffsetZ = unitAttr.create( "input1_RotateOffsetZ", "i1Orz", defaultAngle)
    
    milkShake.inputScaleOffset1 = nAttr.create( "inputScaleOffset1", "inO1S", OpenMaya.MFnNumericData.k3Float,1.0)
    milkShake.inputScaleOffset2 = nAttr.create( "inputScaleOffset2", "inO2S", OpenMaya.MFnNumericData.k3Float,1.0)
    
    milkShake.input1_RotateOffset = nAttr.create( "input1_RotateOffset"         , 
                                                  "in1RotO"                     , 
                                                  milkShake.input1_RotateOffsetX,
                                                  milkShake.input1_RotateOffsetY,
                                                  milkShake.input1_RotateOffsetZ)
    
    milkShake.input2_RotateOffsetX = unitAttr.create( "input2_RotateOffsetX", "i2Orx", defaultAngle)
    milkShake.input2_RotateOffsetY = unitAttr.create( "input2_RotateOffsetY", "i2Ory", defaultAngle)
    milkShake.input2_RotateOffsetZ = unitAttr.create( "input2_RotateOffsetZ", "i2Orz", defaultAngle)

    milkShake.input2_RotateOffset = nAttr.create( "input2_RotateOffset", "in2ORot"  ,
                                                  milkShake.input2_RotateOffsetX    ,
                                                  milkShake.input2_RotateOffsetY    ,
                                                  milkShake.input2_RotateOffsetZ    )
    
    
    milkShake.inRotationOrder1 = enumAttr.create("inRotationOrder1","iro1",0)
    enumAttr.setStorable(1)
    enumAttr.setKeyable(1)
    enumAttr.addField('xyz',0 )  
    enumAttr.addField('yzx',1 ) 
    enumAttr.addField('zxy',2 )
    enumAttr.addField('xzy',3 )   
    enumAttr.addField('yxz',4 )   
    enumAttr.addField('zyx',5 )  
    milkShake.addAttribute( milkShake.inRotationOrder1)
    
    milkShake.inRotationOrder2 = enumAttr.create("inRotationOrder2","iro2",0)
    enumAttr.setStorable(1)
    enumAttr.setKeyable(1)
    enumAttr.addField('xyz',0 )  
    enumAttr.addField('yzx',1 ) 
    enumAttr.addField('zxy',2 )
    enumAttr.addField('xzy',3 )   
    enumAttr.addField('yxz',4 )   
    enumAttr.addField('zyx',5 )     
    milkShake.addAttribute( milkShake.inRotationOrder2)

    milkShake.input1_Translate = nAttr.create( "input1_Translate", "in1TR", OpenMaya.MFnNumericData.k3Float,0)
    milkShake.input2_Translate = nAttr.create( "input2_Translate", "in2TR", OpenMaya.MFnNumericData.k3Float,0)


    #-------------------------------------------- Input rotate Attributes

    milkShake.input1_RotateX = unitAttr.create( "input1_RotateX", "i1rx", defaultAngle)
    milkShake.input1_RotateY = unitAttr.create( "input1_RotateY", "i1ry", defaultAngle)
    milkShake.input1_RotateZ = unitAttr.create( "input1_RotateZ", "i1rz", defaultAngle)
    milkShake.input1_Rotate = nAttr.create( "input1_Rotate", "in1Rot", milkShake.input1_RotateX,milkShake.input1_RotateY,milkShake.input1_RotateZ)
    
    milkShake.input2_RotateX = unitAttr.create( "input2_RotateX", "i2rx", defaultAngle)
    milkShake.input2_RotateY = unitAttr.create( "input2_RotateY", "i2ry", defaultAngle)
    milkShake.input2_RotateZ = unitAttr.create( "input2_RotateZ", "i2rz", defaultAngle)
    milkShake.input2_Rotate = nAttr.create( "input2_Rotate", "in2Rot", milkShake.input2_RotateX,milkShake.input2_RotateY,milkShake.input2_RotateZ)


    milkShake.inputScale1 = nAttr.create( "inputScale1", "in1S", OpenMaya.MFnNumericData.k3Float,1.0)
    milkShake.inputScale2 = nAttr.create( "inputScale2", "in2S", OpenMaya.MFnNumericData.k3Float,1.0)
    
    milkShake.input = cAttr.create( "input", "in" )

    cAttr.addChild(milkShake.input1_TranslateOffset)
    cAttr.addChild(milkShake.input2_TranslateOffset)
    cAttr.addChild(milkShake.input1_RotateOffset)
    cAttr.addChild(milkShake.input2_RotateOffset)
    cAttr.addChild(milkShake.inputScaleOffset1)
    cAttr.addChild(milkShake.inputScaleOffset2)

    cAttr.addChild(milkShake.input1_Translate)
    cAttr.addChild(milkShake.input1_Rotate)
    cAttr.addChild(milkShake.inputScale1)
    cAttr.addChild(milkShake.inRotationOrder1)

    cAttr.addChild(milkShake.input2_Translate)
    cAttr.addChild(milkShake.input2_Rotate)   
    cAttr.addChild(milkShake.inputScale2)
    cAttr.addChild(milkShake.inRotationOrder2)
    

    cAttr.setArray(1)
    cAttr.setStorable(1)
    cAttr.setKeyable(0)
    cAttr.setHidden(0)
    cAttr.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)
    milkShake.addAttribute(milkShake.input)


    #----------------------------------------------------------------------------------------------- Output Attributes

    milkShake.outRotateX = unitAttr.create( "outRotateX", "orx", defaultAngle)
    milkShake.outRotateY = unitAttr.create( "outRotateY", "ory", defaultAngle)
    milkShake.outRotateZ = unitAttr.create( "outRotateZ", "orz", defaultAngle)
    milkShake.outRotate = nAttr.create( "outRotate", "oRot", milkShake.outRotateX,milkShake.outRotateY,milkShake.outRotateZ)
    
    milkShake.outTranslate = nAttr.create( "outTranslate", "oTrn",  OpenMaya.MFnNumericData.k3Float,0.0)    
    milkShake.outScale = nAttr.create( "outScale", "outS", OpenMaya.MFnNumericData.k3Float,1.0 )    
    milkShake.outMatrix = matAttr.create("outMatrix", "oMat",OpenMaya.MFnMatrixAttribute.kDouble)

    milkShake.output = cAttr.create( "output", "out" )
    cAttr.addChild(milkShake.outRotate)
    cAttr.addChild(milkShake.outTranslate)
    cAttr.addChild(milkShake.outScale)
    cAttr.addChild(milkShake.outMatrix)
    

    cAttr.setArray(1)
    cAttr.setStorable(0)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    cAttr.setUsesArrayDataBuilder(1)
    milkShake.addAttribute(milkShake.output) 

    
    milkShake.attributeAffects( milkShake.input             , milkShake.output)
    milkShake.attributeAffects( milkShake.rotInterpolation  , milkShake.output)
    milkShake.attributeAffects( milkShake.weight            , milkShake.output)
    milkShake.attributeAffects( milkShake.blendHierarchy    , milkShake.output)
    
    return
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