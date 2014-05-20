import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim

kPluginNodeName = "brownie"
kPluginNodeId = OpenMaya.MTypeId(0x531AB36) 
kPluginAuthor = "Bazillou2011"
kPluginVersion = "0.04"
nurbIntersect = OpenMaya.MNurbsIntersector()

surfMFn = OpenMaya.MFnNurbsSurface()
pointList = OpenMaya.MPointArray()
tempPnt = OpenMaya.MPoint()

class brownie(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def check_curve_surface_plugs(self,argList):
        actionData             = argList[0]
        inputNurbsConnected = False

        if actionData.isNull() == False :
            inputNurbsConnected = True
        return inputNurbsConnected

    def validate_trigger(self,Plug,Data):  
        triggerList = [ self.outLattice  ]
        
        nodeNeedToRecompute = 0
        for obj in triggerList:
            if Plug ==  obj:
                nodeNeedToRecompute += 1
            
        return nodeNeedToRecompute
    def getPatchInfos(self,surfMFn):
        uCv = surfMFn.numCVsInU()
        vCv = surfMFn.numCVsInV()
        
        formInU_val = surfMFn.formInU()
        formInV_val = surfMFn.formInV() 
        
        degreeU_val = surfMFn.degreeU() 
        degreeV_val = surfMFn.degreeV() 
        
        path_knotsU = OpenMaya.MDoubleArray()
        path_knotsV = OpenMaya.MDoubleArray()
        
        
        surfMFn.getKnotsInU( path_knotsU   )
        surfMFn.getKnotsInV( path_knotsV   )
        
        startUParam = OpenMaya.MScriptUtil()
        startUParam.createFromDouble(0.0)    
        startUPtr = startUParam.asDoublePtr()
        
        endUParam = OpenMaya.MScriptUtil()
        endUParam.createFromDouble(0.0)    
        endUPtr = endUParam.asDoublePtr()   
        
        startVParam = OpenMaya.MScriptUtil()
        startVParam.createFromDouble(0.0)    
        startVPtr = startVParam.asDoublePtr()
        
        endVParam = OpenMaya.MScriptUtil()
        endVParam.createFromDouble(0.0)    
        endVPtr = endVParam.asDoublePtr()     
        
        
        surfMFn.getKnotDomain(  startUPtr, endUPtr, startVPtr, endVPtr )   

        startU = OpenMaya.MScriptUtil(startUPtr).asDouble()
        endU = OpenMaya.MScriptUtil(endUPtr).asDouble()
        startV = OpenMaya.MScriptUtil(startVPtr).asDouble()
        endV = OpenMaya.MScriptUtil(endVPtr).asDouble()

        return [ uCv ,vCv  ,degreeU_val ,degreeV_val,formInU_val ,formInV_val,path_knotsU ,path_knotsV,startU,endU , startV, endV ]  
    def compute(self,Plug,Data): 
        outputWasRequested = self.validate_trigger( Plug,Data)   
        if outputWasRequested == 0:
            return
        else: 
            InputData           = Data.inputValue(self.input ).asNurbsSurface()
            InputShapeConnected = self.check_curve_surface_plugs([InputData])
    
            if InputShapeConnected == False:
                return  
            else:

                widthA_Val                  = Data.inputValue( self.widthA).asDouble()
                widthB_Val                  = Data.inputValue( self.widthB).asDouble()
                uDensity_Val                  = Data.inputValue( self.uDensity).asShort()
                vDensity_Val                  = Data.inputValue( self.vDensity).asShort()

                surfMFn.setObject(InputData ) 
                surfData = self.getPatchInfos(surfMFn)
                surfMFn.getCVs (pointList,OpenMaya.MSpace.kObject)
                uCv = surfData[0]
                vCv = surfData[1]
                path_knotsU     = surfData[6]
                path_knotsV     = surfData[7]
                startU          = surfData[8]
                endU            = surfData[9]
                startV          = surfData[10]
                endV            = surfData[11]
                
                uRatio = (endU-startU)/(uCv*uDensity_Val*1.0)
                vRatio = (endV-startV)/(vCv*vDensity_Val*1.0)
                uRange = []
                vRange = []
                for k in xrange(uCv*uDensity_Val+1):
                    uRange.append(k*uRatio)
                for k in xrange(vCv*vDensity_Val+1):
                    vRange.append(k*vRatio)

                widthData = [widthA_Val,widthB_Val]      

                mat = OpenMaya.MMatrix()
                nurbIntersect.create(InputData, mat)
                ptON = OpenMaya.MPointOnNurbs()
                
                outLattice_Hndle = Data.outputValue(self.outLattice )
                latDat = OpenMaya.MFnLatticeData ()
                latObj = latDat.create()
                lafFn = OpenMayaAnim.MFnLattice()
        
                
                divX = len(uRange)
                divY = len(vRange)
                divZ = 2

                lafFn.create( divX,divY,divZ,latObj)
                resultPoint = OpenMaya.MPoint()
                vecList = [widthData[0]*-0.01,widthData[1]*0.01]

                for i in range(divX):
                    for j in range(divY):
                        surfMFn.getPointAtParam	(uRange[i],vRange[j],resultPoint,OpenMaya.MSpace.kObject  ) 
                        outV = surfMFn.normal(uRange[i],vRange[j],OpenMaya.MSpace.kObject).normal()
    
                        for k in range(divZ):
                            outPoint = lafFn.point( i, j, k ) 
                            outPointB = resultPoint+(outV*vecList[k])       
        
                            outPoint.x = outPointB.x
                            outPoint.y = outPointB.y
                            outPoint.z = outPointB.z

                outLattice_Hndle.setMObject(latObj)
                outLattice_Hndle.setClean()
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(brownie())
def nodeInitializer():
    typed_Attr =  OpenMaya.MFnTypedAttribute()    
    mAttr = OpenMaya.MFnNumericAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    

    
    brownie.input = typed_Attr.create( "input", "in", OpenMaya.MFnNurbsCurveData.kNurbsSurface )
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    brownie.addAttribute( brownie.input )   
        
    brownie.widthA = mAttr.create("widthA","wA", OpenMaya.MFnNumericData.kDouble,1.0)
    mAttr.setStorable(1)
    mAttr.setKeyable(1)
    mAttr.setHidden(0)     
    brownie.addAttribute( brownie.widthA)  
    
    brownie.widthB = mAttr.create("widthB","wB", OpenMaya.MFnNumericData.kDouble,1.0)
    mAttr.setStorable(1)
    mAttr.setKeyable(1)
    mAttr.setHidden(0)     
    brownie.addAttribute( brownie.widthB)  
    
    brownie.uDensity = mAttr.create("uDensity","uD", OpenMaya.MFnNumericData.kShort,1)
    mAttr.setStorable(1)
    mAttr.setKeyable(1)
    mAttr.setHidden(0)     
    mAttr.setMin(1)  
    mAttr.setSoftMax(5)  
    brownie.addAttribute( brownie.uDensity)  
    
    brownie.vDensity = mAttr.create("vDensity","vD", OpenMaya.MFnNumericData.kShort,1)
    mAttr.setStorable(1)
    mAttr.setKeyable(1)
    mAttr.setHidden(0)     
    mAttr.setMin(1)  
    mAttr.setSoftMax(5)  
    brownie.addAttribute( brownie.vDensity)  

    brownie.outLattice = typed_Attr.create("outLattice", "upLat", OpenMaya.MFnData.kLattice)
    typed_Attr.setHidden(1)
    brownie.addAttribute(brownie.outLattice)    
    

    brownie.attributeAffects( brownie.input , brownie.outLattice )    
    brownie.attributeAffects( brownie.widthA    , brownie.outLattice )  
    brownie.attributeAffects( brownie.widthB    , brownie.outLattice )  
    brownie.attributeAffects( brownie.uDensity    , brownie.outLattice )  
    brownie.attributeAffects( brownie.vDensity    , brownie.outLattice )  
    
    return    
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, kPluginAuthor, kPluginVersion, "Any")
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
