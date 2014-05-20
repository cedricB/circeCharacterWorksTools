'''
########################################################################
#                                                                      #
#             tortilla.py                                              #
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

    P U R P O S E:
        Compute twist on a per segment level --> we expect normalize u values....
    I N S T A L L A T I O N:
        Copy the "tortilla.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

__plug_in__Version = "0.742"
__author = "Bazillou2013"

import math 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "tortilla"
kPluginNodeId = OpenMaya.MTypeId(0xBCB7141) 

       


class tortilla(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def update_output_storage(self,uCount,bldChck,cBuilder):               
        #how many entry do we need add to the current output list?
        growVal = uCount-bldChck
        if growVal>0:    
            cBuilder.growArray ( growVal )
    def getValAtPos(self,pos,myRamp):
        valAt_util = OpenMaya.MScriptUtil()
        valAt_util.createFromDouble(0.0)
        valAtPtr = valAt_util.asFloatPtr()

        myRamp.getValueAtPosition(pos, valAtPtr)
        myMainValue = valAt_util.getFloat(valAtPtr)

        return myMainValue
    def compute(self,Plug,Data):
        if Plug.parent() == self.output :
            uParameters_obj = Data.inputValue(self.uParameters).data()
            
            if uParameters_obj.isNull() == False:
                DoubleArrayFn   = OpenMaya.MFnDoubleArrayData(uParameters_obj)
    
                u_params = DoubleArrayFn.array()            
                u_len = u_params.length()
                if u_len > 0 :
                    output_handle   = Data.outputArrayValue(self.output)
                    startTwist_val  = Data.inputValue(self.startTwist).asDouble()
                    endTwist_val    = Data.inputValue(self.endTwist).asDouble()
                    
                    startScale_val  = Data.inputValue(self.startScale).asDouble3()
                    endScale_val    = Data.inputValue(self.endScale).asDouble3()
                    
                    startScale_valX = startScale_val[0] - 1.0
                    startScale_valY  = startScale_val[1] - 1.0
                    startScale_valZ  = startScale_val[2] - 1.0

                    endScale_valX = endScale_val[0] - 1.0
                    endScale_valY  = endScale_val[1] - 1.0
                    endScale_valZ  = endScale_val[2] - 1.0
                    
                    twistTweak_val  = Data.inputValue(self.twistTweak).asDouble()
                    scaleTweak_val  = Data.inputValue(self.scaleTweak).asDouble()-1.0
                    
                    cBuilder = output_handle.builder()

                    nodeObj = self.thisMObject()
                    rampWeightData = OpenMaya.MRampAttribute (nodeObj, self.twist_rampWeight )                    
                    numEnt =  rampWeightData.getNumEntries()
                    
                    rampWeightDataB = OpenMaya.MRampAttribute (nodeObj, self.twistTweak_rampWeight )                    
                    numEntB =  rampWeightDataB.getNumEntries()
                    
                    
                    rampWeightDataC = OpenMaya.MRampAttribute (nodeObj, self.scaleTweak_rampWeight )                    
                    numEntC =  rampWeightDataC.getNumEntries()
                    
                    
                    rampWeightDataD = OpenMaya.MRampAttribute (nodeObj, self.endScale_rampWeight )                    
                    numEntD =  rampWeightDataD.getNumEntries()
                    
                    

                    for k in range(u_len):
                        currentDH    = cBuilder.addElement(k)  
                        outRotate_DH = currentDH.child(self.outRotate)
                        outScale_DH = currentDH.child(self.outScale) 
                        
                        uVal = u_params[k]
                        uValB = u_params[k]
    
                        if numEnt > 1 :                             
                            uVal = self.getValAtPos( u_params[k] ,rampWeightData)

                        
                        strtVal = 1.0-uVal
                        endVal  = 0.0+uVal
                        
                        tweakwist_offset = 0.0
                        tweakwist_offsetB = endVal
    
                        scaleTwist_offset = 0.0
                        if twistTweak_val != 0.0:
                            if numEntB > 1 :                             
                                tweakwist_offset = self.getValAtPos( u_params[k] ,rampWeightDataB)
                                
                            else:
                                if u_params[k] < 0.5:
                                    tweakwist_offset =  1.0- ((0.5-u_params[k])/0.5)
    
                                else:
                                    tweakwist_offset = 1.0- ((u_params[k]-0.5)/0.5) 

                            ###############################################################################
                                
                        if scaleTweak_val != 0.0:
                            if numEntC > 1 :                             
                                scaleTwist_offset = self.getValAtPos( u_params[k] ,rampWeightDataC)
                                
                            else:
                                if u_params[k] < 0.5:
                                    scaleTwist_offset =  1.0- ((0.5-u_params[k])/0.5)
    
                                else:
                                    scaleTwist_offset = 1.0- ((u_params[k]-0.5)/0.5)                            

                        outTwist = math.radians(startTwist_val*strtVal +endTwist_val*endVal + twistTweak_val*tweakwist_offset )

                        
                        if numEntD > 1 :                             
                            endVal = self.getValAtPos( u_params[k] ,rampWeightDataD)

                        scaleX = 1.0 + (startScale_valX*strtVal) + (endScale_valX*endVal)  + (scaleTweak_val*scaleTwist_offset) 
                        scaleY = 1.0 + (startScale_valY*strtVal) + (endScale_valY*endVal)  + (scaleTweak_val*scaleTwist_offset )
                        scaleZ = 1.0 + (startScale_valZ*strtVal) + (endScale_valZ*endVal)   + (scaleTweak_val*scaleTwist_offset  )    
                        
                        
                        #write values
                        outRotate_DH.set3Double(outTwist,0.0,0.0)   
                        outScale_DH.set3Double(scaleX,scaleY,scaleZ)

                
                    output_handle.set(cBuilder)
                    output_handle.setAllClean()
        if Plug == self.twistArray :
            uParameters_obj = Data.inputValue(self.uParameters).data()
            
            if uParameters_obj.isNull() == False:
                DoubleArrayFn   = OpenMaya.MFnDoubleArrayData(uParameters_obj)
    
                u_params = DoubleArrayFn.array()            
                u_len = u_params.length()
                if u_len > 0 :
                    output_handle   = Data.outputValue(self.twistArray)
                    
                    startTwist_val  = Data.inputValue(self.startTwist).asDouble()
                    endTwist_val    = Data.inputValue(self.endTwist).asDouble()                  
                    twistTweak_val  = Data.inputValue(self.twistTweak).asDouble()

                    nodeObj = self.thisMObject()
                    rampWeightData = OpenMaya.MRampAttribute (nodeObj, self.twist_rampWeight )                    
                    numEnt =  rampWeightData.getNumEntries()
                    
                    rampWeightDataB = OpenMaya.MRampAttribute (nodeObj, self.twistTweak_rampWeight )                    
                    numEntB =  rampWeightDataB.getNumEntries()

                    out_TwistList = OpenMaya.MDoubleArray(u_len,0.0)        
                    for n in range(u_len/2):   
                        k =  n*2                   
                        uVal = u_params[k]
    
                        if numEnt > 1 :                             
                            uVal = self.getValAtPos( u_params[k] ,rampWeightData)

                        
                        strtVal = 1.0-uVal
                        endVal  = 0.0+uVal
                        
                        tweakwist_offset = 0.0
                        tweakwist_offsetB = endVal

                        if twistTweak_val != 0.0:
                            if numEntB > 1 :                             
                                tweakwist_offset = self.getValAtPos( u_params[k] ,rampWeightDataB)
                                
                            else:
                                if u_params[k] < 0.5:
                                    tweakwist_offset =  1.0- ((0.5-u_params[k])/0.5)
    
                                else:
                                    tweakwist_offset = 1.0- ((u_params[k]-0.5)/0.5) 
                      

                        outTwist = math.radians(startTwist_val*strtVal +endTwist_val*endVal + twistTweak_val*tweakwist_offset )
                        out_TwistList.set(outTwist,k)
                        out_TwistList.set(u_params[k+1],k+1)
                    out_DoubleArrayFn   = OpenMaya.MFnDoubleArrayData()
                    outOBJ = out_DoubleArrayFn.create(out_TwistList)
                    
                    output_handle.setMObject(outOBJ)
                    output_handle.setClean()

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(tortilla())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    matAttr = OpenMaya.MFnMatrixAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()

    
    tortilla.uParameters = typed_Attr.create( "uParameters", "uuPrm", OpenMaya.MFnData.kDoubleArray)
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(1)
    tortilla.addAttribute(tortilla.uParameters)

    
    tortilla.startTwist = nAttr.create( "startTwist", "sTw", OpenMaya.MFnNumericData.kDouble, 0.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.startTwist)


    tortilla.endTwist = nAttr.create( "endTwist", "eTw", OpenMaya.MFnNumericData.kDouble, 0.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.endTwist)
    
    tortilla.startScale = nAttr.create( "startScale", "sSc", OpenMaya.MFnNumericData.k3Double, 1.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.startScale)

    tortilla.endScale = nAttr.create( "endScale", "eSc", OpenMaya.MFnNumericData.k3Double, 1.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.endScale)
    
    tortilla.twistTweak = nAttr.create( "twistTweak", "sWk", OpenMaya.MFnNumericData.kDouble, 0.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.twistTweak)
    
    tortilla.scaleTweak = nAttr.create( "scaleTweak", "scWk", OpenMaya.MFnNumericData.kDouble, 1.0 )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    tortilla.addAttribute( tortilla.scaleTweak)
    
    rmp_Attr =  OpenMaya.MRampAttribute()
    tortilla.twist_rampWeight = rmp_Attr.createCurveRamp ("twist_rampWeight", "tw_rWg")
    tortilla.addAttribute( tortilla.twist_rampWeight) 
    
    tortilla.endScale_rampWeight = rmp_Attr.createCurveRamp ("endScale_rampWeight", "enS_rWg")
    tortilla.addAttribute( tortilla.endScale_rampWeight) 
    
    tortilla.twistTweak_rampWeight = rmp_Attr.createCurveRamp ("twistTweak_rampWeight", "ttw_rWg")
    tortilla.addAttribute( tortilla.twistTweak_rampWeight) 
    
    tortilla.scaleTweak_rampWeight = rmp_Attr.createCurveRamp ("scaleTweak_rampWeight", "stw_rWg")
    tortilla.addAttribute( tortilla.scaleTweak_rampWeight) 


    #---------------------------------------------------------------------------- Output Attributes
    defaultAngle = OpenMaya.MAngle ( 0.0, OpenMaya.MAngle.kDegrees )
    defaultDist  = OpenMaya.MDistance ( 0.0, OpenMaya.MDistance.kCentimeters )
    
    tortilla.outRotateX = unitAttr.create( "outRotateX", "orx", defaultAngle)
    tortilla.outRotateY = unitAttr.create( "outRotateY", "ory", defaultAngle)
    tortilla.outRotateZ = unitAttr.create( "outRotateZ", "orz", defaultAngle)
    tortilla.outRotate = nAttr.create( "outRotate", "oRot",tortilla.outRotateX,tortilla.outRotateY,tortilla.outRotateZ)

    tortilla.outTranslateX = unitAttr.create( "outTranslateX", "otx", defaultDist)
    tortilla.outTranslateY = unitAttr.create( "outTranslateY", "oty", defaultDist)
    tortilla.outTranslateZ = unitAttr.create( "outTranslateZ", "otz", defaultDist)
    tortilla.outTranslate = nAttr.create( "outTranslate", "oTrn",tortilla.outTranslateX,tortilla.outTranslateY,tortilla.outTranslateZ)

    tortilla.outScale = nAttr.create( "outScale", "outS", OpenMaya.MFnNumericData.k3Double,1.0 )

    tortilla.output = cAttr.create( "output", "out" )
    cAttr.addChild(tortilla.outRotate)
    cAttr.addChild( tortilla.outScale)

    cAttr.setArray(1)
    cAttr.setStorable(1)
    cAttr.setKeyable(0)
    cAttr.setHidden(True)
    cAttr.setUsesArrayDataBuilder(1)
    tortilla.addAttribute(tortilla.output) 

    tortilla.attributeAffects( tortilla.startTwist , tortilla.output)
    tortilla.attributeAffects( tortilla.endTwist , tortilla.output)
    tortilla.attributeAffects( tortilla.uParameters , tortilla.output)
    tortilla.attributeAffects( tortilla.startScale , tortilla.output)
    tortilla.attributeAffects( tortilla.endScale , tortilla.output)
    
    tortilla.attributeAffects( tortilla.twist_rampWeight , tortilla.output)
    tortilla.attributeAffects( tortilla.scaleTweak , tortilla.output)
    tortilla.attributeAffects( tortilla.twistTweak , tortilla.output)
    tortilla.attributeAffects( tortilla.twistTweak_rampWeight, tortilla.output)
    tortilla.attributeAffects( tortilla.scaleTweak_rampWeight, tortilla.output)
    tortilla.attributeAffects( tortilla.endScale_rampWeight, tortilla.output)
    
    # TWIST array for spline deformer
    tortilla.twistArray = typed_Attr.create( "twistArray", "twL", OpenMaya.MFnData.kDoubleArray)
    typed_Attr.setStorable(1)
    typed_Attr.setHidden(1)
    tortilla.addAttribute(tortilla.twistArray)
    
    tortilla.attributeAffects( tortilla.startTwist , tortilla.twistArray)
    tortilla.attributeAffects( tortilla.endTwist , tortilla.twistArray)
    tortilla.attributeAffects( tortilla.uParameters , tortilla.twistArray)
    
    tortilla.attributeAffects( tortilla.twist_rampWeight , tortilla.twistArray)
    tortilla.attributeAffects( tortilla.twistTweak , tortilla.twistArray)
    tortilla.attributeAffects( tortilla.twistTweak_rampWeight, tortilla.twistArray)

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