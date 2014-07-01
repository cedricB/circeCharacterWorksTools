import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim

kPluginNodeName = "brownie"
kPluginNodeId = OpenMaya.MTypeId(0x531AB36) 
kPluginAuthor = "Bazillou2011"
kPluginVersion = "0.37"
nurbIntersect = OpenMaya.MNurbsIntersector()

surfMFn = OpenMaya.MFnNurbsSurface()
curveFn = OpenMaya.MFnNurbsCurve()
pointList = OpenMaya.MPointArray()
tempPnt = OpenMaya.MPoint()


outMeshFn = OpenMaya.MFnMesh()
meshDataFn = OpenMaya.MFnMeshData()   


class brownie(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_curve_surface_plugs(self,argList):
        actionData             = argList[0]
        inputNurbsConnected = False

        if actionData.isNull() == False :
            inputNurbsConnected = True
        return inputNurbsConnected
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
        if Plug ==  self.outLattice :
            InputData           = Data.inputValue(self.input ).asNurbsSurface()
            InputShapeConnected = self.check_curve_surface_plugs([InputData])
    
            if InputShapeConnected == False:
                return  
            else:                    
                self.compute_outLattice( Data,InputData)
        if Plug ==  self.outCage :
            self.compute_outCage( Data )
        if Plug ==  self.outMesh :
            self.compute_outMesh( Data)
        if Plug ==  self.outTube :
            self.compute_outTube( Data)
    def compute_outTube(self,Data):
            splineMatrixData  = self.composeSplineMatrix( Data)
            radius_Val        = Data.inputValue( self.radius).asDouble()
    
            if splineMatrixData == None:
                return
            else:  
                radius_Val                  = Data.inputValue( self.radius).asDouble()
                knotCount = 8
                
                offsetPoint = OpenMaya.MPoint(0,radius_Val,0,1)
                offsetArray = OpenMaya.MPointArray(knotCount+1)
                u_len = splineMatrixData.length()
                                
                indexTable = [[5,4,3],
                              [6,8,2],
                              [7,0,1]]
                
                
                shiftVal = OpenMaya.MEulerRotation(0,0,0, 0) 
                shftRatio = 360.0/(knotCount*1.0)

                locSpace = OpenMaya.MSpace.kObject
                
                
                for j in range(knotCount):
                    shiftVal.x = math.radians(j*shftRatio)
                    offsetArray.set(offsetPoint*shiftVal.asMatrix(),j)
                    

                newMeshObj = meshDataFn.create()
                resultPoint = OpenMaya.MPoint()
                
                VtxPos =  OpenMaya.MPointArray(knotCount*u_len )
                
                polygonCounts = OpenMaya.MIntArray(knotCount*(u_len-1) ,4)                       
                polygonConnects = OpenMaya.MIntArray()
                
                indexTableB = [1,2,3,4,5,6,7,0 ]
                for i in range(u_len-1):
                    for j in range(knotCount):
                        vertID_A = j+(i*knotCount)
                        vertID_B = j+((i+1)*knotCount)
                        vertID_C = indexTableB[j]+((i+1)*knotCount)
                        vertID_D = indexTableB[j] +(i*knotCount)
                        
                        polygonConnects.append(vertID_A)
                        polygonConnects.append(vertID_D)
                        polygonConnects.append(vertID_C)
                        polygonConnects.append(vertID_B)
                
                
                knotOffset_obj            = Data.inputValue( self.knotOffset).data()  
                knotChk = False 
                knotOffsetList = None    
 
                if knotOffset_obj.isNull() == False:  
                    knotOffsetFn   = OpenMaya.MFnVectorArrayData(knotOffset_obj)                    
                    knotOffsetList = knotOffsetFn.array() 
                        
                    if knotOffsetList.length() > 0 :
                        knotChk = True

                if knotChk == False:
                    for i in range(u_len):
                        for j in range(knotCount):
                            VtxPos.set(offsetArray[j] * splineMatrixData[i] ,j+(i*knotCount))
                else:
                    tmpPnt = OpenMaya.MPoint()
                    for i in range(u_len):
                        for j in range(knotCount):
                            VtxPos.set((tmpPnt +knotOffsetList[j+(i*knotCount)] ) * splineMatrixData[i] ,j+(i*knotCount))


                outMeshFn.create (VtxPos.length(), polygonCounts.length(), VtxPos,  polygonCounts, polygonConnects, newMeshObj)
                outHandle = Data.outputValue( self.outTube) 
                outHandle.setMObject(newMeshObj)
                outHandle.setClean()     
    def composeSplineMatrix(self,Data):
        splineMatrix_obj            = Data.inputValue( self.splineMatrix).data()        
        if splineMatrix_obj.isNull() == True:
            return None
        else:
            splineMatrixFn   = OpenMaya.MFnVectorArrayData(splineMatrix_obj)                    
            vecList = splineMatrixFn.array()    
            
            vec_len = vecList.length()/4
            

            if vec_len < 1 :
                return None
            else:
                targLen  = int(vecList[0].x)
                sliceMatList = OpenMaya.MMatrixArray(targLen)

                for i in range(targLen):                    
                    matrixValueList = [ vecList[1+i*4+0].x, vecList[1+i*4+0].y, vecList[1+i*4+0].z, 0.0,
                                        vecList[1+i*4+1].x, vecList[1+i*4+1].y, vecList[1+i*4+1].z, 0.0,
                                        vecList[1+i*4+2].x, vecList[1+i*4+2].y, vecList[1+i*4+2].z, 0.0,
                                        vecList[1+i*4+3].x, vecList[1+i*4+3].y, vecList[1+i*4+3].z,1.0]  
            
                    rotMatrix = OpenMaya.MMatrix()
                    utilB = OpenMaya.MScriptUtil()
                    utilB.createMatrixFromList( matrixValueList, rotMatrix )
                    
                    sliceMatList.set(rotMatrix,i)
                return sliceMatList
    def compute_outMesh(self,Data):
            splineMatrixData  = self.composeSplineMatrix( Data)
            radius_Val        = Data.inputValue( self.radius).asDouble()
    
            if splineMatrixData == None:
                return
            else:
                radius_Val                  = Data.inputValue( self.radius).asDouble()
                knotCount = 8
                
                offsetPoint = OpenMaya.MPoint(0,radius_Val,0,1)
                offsetArray = OpenMaya.MPointArray(knotCount+1)
                u_len = splineMatrixData.length()
                                
                indexTable = [[5,4,3],
                              [6,8,2],
                              [7,0,1]]
                
                
                shiftVal = OpenMaya.MEulerRotation(0,0,0, 0) 
                shftRatio = 360.0/(knotCount*1.0)
                sidenum = int(math.sqrt(knotCount+1))
                locSpace = OpenMaya.MSpace.kObject
                
                
                for j in range(knotCount):
                    shiftVal.x = math.radians(j*shftRatio)
                    offsetArray.set(offsetPoint*shiftVal.asMatrix(),j)

                newMeshObj = meshDataFn.create()
                resultPoint = OpenMaya.MPoint()
                
                VtxPos =  OpenMaya.MPointArray(knotCount*u_len+2)
                
                polygonCounts = OpenMaya.MIntArray(knotCount*(u_len-1)+8,4)                       
                polygonConnects = OpenMaya.MIntArray()
                
                indexTableB = [1,2,3,4,5,6,7,0 ]
                for i in range(u_len-1):
                    for j in range(knotCount):
                        vertID_A = j+(i*knotCount)
                        vertID_B = j+((i+1)*knotCount)
                        vertID_C = indexTableB[j]+((i+1)*knotCount)
                        vertID_D = indexTableB[j] +(i*knotCount)
                        
                        polygonConnects.append(vertID_A)
                        polygonConnects.append(vertID_D)
                        polygonConnects.append(vertID_C)
                        polygonConnects.append(vertID_B)
                      
                
                capA = knotCount*u_len
                VtxPos.set(resultPoint*splineMatrixData[0] ,capA)
                
                capB = knotCount*u_len+1               
                VtxPos.set(resultPoint*splineMatrixData[u_len-1] ,capB)
                
                for i in range(u_len):
                    for j in range(knotCount):
                        VtxPos.set(offsetArray[j] * splineMatrixData[i] ,j+(i*knotCount))

                
                capList = [0,capA,2,1,7,6,capA,0,6,5,4,capA,capA,4,3,2 ]
                for j in range(len(capList)):
                    polygonConnects.append(capList[j])
                    
                lastRow = []
                for j in range(knotCount):
                    lastRow.append(j+((u_len-1)*knotCount))
                        
                capListB = [lastRow[0],lastRow[1],lastRow[2],capB,
                           lastRow[7],lastRow[0],capB,lastRow[6],
                           lastRow[6],capB,lastRow[4],lastRow[5],
                           capB,lastRow[2],lastRow[3],lastRow[4] ]

                for j in range(len(capListB)):
                    polygonConnects.append(capListB[j] )


                outMeshFn.create (VtxPos.length(), polygonCounts.length(), VtxPos,  polygonCounts, polygonConnects, newMeshObj)
                outHandle = Data.outputValue( self.outMesh) 
                outHandle.setMObject(newMeshObj)
                outHandle.setClean()
    def compute_outCage(self,Data):
        splineMatrixData  = self.composeSplineMatrix( Data)
        radius_Val        = Data.inputValue( self.radius).asDouble()

        if splineMatrixData == None:
            return
        else:
            knotCount = 8
            
            offsetPoint = OpenMaya.MPoint(0,radius_Val,0,1)
            offsetArray = OpenMaya.MPointArray(knotCount+1)
            
            indexTable = [[5,4,3],
                          [6,8,2],
                          [7,0,1]]

            shiftVal = OpenMaya.MEulerRotation(0,0,0, 0) 
            shftRatio = 360.0/(knotCount*1.0)
            sidenum = int(math.sqrt(knotCount+1))
            
            
            for j in range(knotCount):
                shiftVal.x = math.radians(j*shftRatio)
                offsetArray.set(offsetPoint*shiftVal.asMatrix(),j)
                
            outCage_Hndle = Data.outputValue(self.outCage )
            latDat = OpenMaya.MFnLatticeData ()
            latObj = latDat.create()
            lafFn = OpenMayaAnim.MFnLattice()
        
            
            divX = splineMatrixData.length()
            divY = sidenum
            divZ = sidenum
            
            
            lafFn.create( divX,divY,divZ,latObj)
            
            knotOffset_obj            = Data.inputValue( self.knotOffset).data()  
            knotChk = False 
            knotOffsetList = None    

            if knotOffset_obj.isNull() == False:  
                knotOffsetFn   = OpenMaya.MFnVectorArrayData(knotOffset_obj)                    
                knotOffsetList = knotOffsetFn.array() 
                    
                if knotOffsetList.length() > 0 :
                    knotChk = True

            if knotChk == False:
                for i in range(divX):
                    for j in range(divY):                   
                        for k in range(divZ):                                                                      
                            outPoint = lafFn.point( i, j, k )   
                            outPointB = offsetArray[ indexTable[j][k] ] * splineMatrixData[i]  

                            outPoint.x = outPointB.x
                            outPoint.y = outPointB.y
                            outPoint.z = outPointB.z
            else:
                idx = 0
                outPointB = OpenMaya.MPoint()
                tmpPnt = OpenMaya.MPoint()
                for i in range(divX):
                    for j in range(divY):                   
                        for k in range(divZ):                                                                      
                            outPoint = lafFn.point( i, j, k )   
                            idx = indexTable[j][k]
                            if idx != 8 :
                                outPointB = (tmpPnt +knotOffsetList[idx+(i*knotCount)]) * splineMatrixData[i]  
                            else :
                                outPointB = offsetArray[ 8 ] * splineMatrixData[i]  
                            outPoint.x = outPointB.x
                            outPoint.y = outPointB.y
                            outPoint.z = outPointB.z
            outCage_Hndle.setMObject(latObj)
            outCage_Hndle.setClean()
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
    def compute_outLattice(self,Data,InputData):
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
    brownie.attributeAffects( brownie.uDensity  , brownie.outLattice )  
    brownie.attributeAffects( brownie.vDensity  , brownie.outLattice )  
    
    brownie.splineMatrix = typed_Attr.create( "splineMatrix", "sMat", OpenMaya.MFnData.kVectorArray) #1 matrix is decompose into 4 vector....
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(1)
    brownie.addAttribute(brownie.splineMatrix) 

    
    brownie.radius = mAttr.create("radius","rds", OpenMaya.MFnNumericData.kDouble,1.0)
    mAttr.setStorable(1)
    mAttr.setKeyable(1)
    mAttr.setHidden(0)     
    brownie.addAttribute( brownie.radius)  
    
    brownie.outCage = typed_Attr.create("outCage", "oCg", OpenMaya.MFnData.kLattice)
    typed_Attr.setHidden(1)
    brownie.addAttribute(brownie.outCage)    
    
    

    brownie.attributeAffects( brownie.splineMatrix    , brownie.outCage )  
    brownie.attributeAffects( brownie.radius        , brownie.outCage )  
    
    
    brownie.outMesh = typed_Attr.create( "outMesh", "oMsh", OpenMaya.MFnMeshData.kMesh)
    typed_Attr.setHidden(1)
    brownie.addAttribute( brownie.outMesh )
    
   
    brownie.attributeAffects( brownie.splineMatrix  , brownie.outMesh ) 
    brownie.attributeAffects( brownie.radius        , brownie.outMesh ) 

    
    brownie.knotOffset = typed_Attr.create( "knotOffset", "kOff",  OpenMaya.MFnData.kVectorArray)
    typed_Attr.setHidden(1)
    brownie.addAttribute( brownie.knotOffset )
    
    brownie.outTube = typed_Attr.create( "outTube", "oTbe", OpenMaya.MFnMeshData.kMesh)
    typed_Attr.setHidden(1)
    brownie.addAttribute( brownie.outTube )
    
   
    brownie.attributeAffects( brownie.splineMatrix  , brownie.outTube ) 
    brownie.attributeAffects( brownie.radius        , brownie.outTube )   
    brownie.attributeAffects( brownie.knotOffset    , brownie.outTube )


    
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
