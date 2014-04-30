'''
########################################################################
#                                                                      #
#             geodesicWeight.py                                        #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################

    L I C E N S E:
        Copyright (c) 2012 Cedric BAZILLOU All rights reserved.
        
        THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
        THE SOFTWARE.

    P U R P O S E:
        Trigger an array of pose space helper/blendshape

    I N S T A L L A T I O N:
        Copy the "geodesicWeight.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "geodesicWeight"
kPluginNodeId = OpenMaya.MTypeId(0xCCB225A) 

class geodesicWeight(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_mesh_surface_plugs(self,actionData):
        inputMeshConnected = False
        if actionData.isNull() == False :
            inputMeshConnected = True
        return inputMeshConnected
    def extract_point_on_surface_infos(self,inputStruct):
        cubePointVal    = inputStruct[0]
        polyMfnMesh     = inputStruct[1]

        #samplePos = [round( cubePointVal[0],5),round( cubePointVal[1],5),round( cubePointVal[2],5)]
        VectorFloat  = OpenMaya.MFloatVector(cubePointVal[0],cubePointVal[1],cubePointVal[2])
        
        #pointer for hitFace
        hitFaceParam = OpenMaya.MScriptUtil()
        hitFaceParam.createFromInt(0)
        hitFacePtr = hitFaceParam.asIntPtr()

        InFloatPoint = OpenMaya.MFloatPoint(0, 0 , 0)
        hitPoint = OpenMaya.MFloatPoint()

        #Intersection parameter setup
        mmAccelParams   = OpenMaya.MMeshIsectAccelParams()
        mmAccelParams   = polyMfnMesh.autoUniformGridParams()

        testHit = polyMfnMesh.closestIntersection ( InFloatPoint, VectorFloat ,
        None , None , False , OpenMaya.MSpace.kObject ,4.0, False, mmAccelParams,
        hitPoint, None, hitFacePtr, None, None,None, 0.001 )
            
        #Data packing and return
        if testHit == False:
            return None
        else:
            fceNm = OpenMaya.MScriptUtil(hitFacePtr).asInt()
            return [ OpenMaya.MPoint(hitPoint),fceNm]
    def compute_weight_list(self,polyMfnMesh,numVertices,polygonId,faceIter,collisionDatas):
        weightList = OpenMaya.MDoubleArray(numVertices,0.0)        
        vertexList = OpenMaya.MIntArray()
        polyMfnMesh.getPolygonVertices(polygonId,vertexList) 
        prev_util = OpenMaya.MScriptUtil()
        prev_util.createFromInt(0)
        prev_ptr = prev_util.asIntPtr()
        faceIter.setIndex (polygonId,prev_ptr)        
        facePntList = OpenMaya.MPointArray()
        faceIter.getPoints(facePntList,OpenMaya.MSpace.kObject)

        hitPoint = collisionDatas[0]
        if vertexList.length() == 3:  
            areaParam = OpenMaya.MScriptUtil()
            areaParam.createFromDouble(0)
            areaPtr = areaParam.asDoublePtr()
            faceIter.getArea( areaPtr,OpenMaya.MSpace.kObject )
            faceArea =  OpenMaya.MScriptUtil(areaPtr).asDouble()

            barycenters = self.extract_barycentric_coordinates(facePntList, hitPoint,faceArea)
            for k in range(3):
                weightList[vertexList[k]] = barycenters[k]
            
        return weightList
    def extract_barycentric_coordinates(self, vertexPositions , hitPoint,faceArea):
        vertId_List = [1,2,0,1]        
        weightList = [0.0,0.0,0.0]
        for k in range(2):
            vecA = vertexPositions[vertId_List[k]] - hitPoint
            vecB = vertexPositions[vertId_List[k+1]] - hitPoint
            subTris_Area    = (vecA^vecB).length()*0.5
            weightList[k]   = subTris_Area/faceArea
        weightList[2] = math.fabs(1.0 - ( weightList[0] + weightList[1] ))
        return weightList
    def compute(self,Plug,Data):
        #Layout necessary output / input handle to gather data
        InputMeshData               = Data.inputValue(self.inputShape ).asMesh()
        pos_val                     = Data.inputValue(self.cartesianPosition).asDouble3()
        output_handle               = Data.outputArrayValue(self.output)
        collision_Face_handle       = Data.outputValue(self.collision_Face)
        #--------------------------------------------------------------------- Compute if a mesh is connected
        InputMeshConnected = self.check_mesh_surface_plugs(InputMeshData)
        if InputMeshConnected == False:
            return 
        else:
            #@ 1 Mesh is connected we can processed its data 
            polyMfnMesh = OpenMaya.MFnMesh(InputMeshData) 
            faceIter = OpenMaya.MItMeshPolygon(InputMeshData)
            numPolygon = polyMfnMesh.numPolygons()

                           
            collisionDatas = self.extract_point_on_surface_infos((pos_val,polyMfnMesh))
            
            if collisionDatas is None :
                return
            else:               
                numVertices = polyMfnMesh.numVertices()
                polygonId = collisionDatas[1]
                
                collision_Face_handle.setInt(polygonId)
                collision_Face_handle.setClean()

                cBuilder = output_handle.builder()
                weightList = self.compute_weight_list(polyMfnMesh,numVertices,polygonId,faceIter,collisionDatas)

                for n in range(0,numVertices):
                    currentDH = cBuilder.addElement(n)
                    currentDH.setDouble(weightList[n]) 
                    
                output_handle.set(cBuilder)
                output_handle.setAllClean()
def link_relashionShip( DriverList, driven_Attribute):
    for driver in DriverList:
        geodesicWeight.attributeAffects(driver,driven_Attribute)
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    #input Attributes  ----------------------------------------------------------------------------------------------------------------------------
    inputShape_Attr =  OpenMaya.MFnTypedAttribute()	
    geodesicWeight.inputShape = inputShape_Attr.create( "inputShape", "inS", OpenMaya.MFnMeshData.kMesh)
    inputShape_Attr.setStorable(0)
    inputShape_Attr.setKeyable(0)
    inputShape_Attr.setHidden(True)
    geodesicWeight.addAttribute( geodesicWeight.inputShape )
    
    geodesicWeight.cartesianPosition = nAttr.create( "cartesianPosition", "cPos", OpenMaya.MFnNumericData.k3Double )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    geodesicWeight.addAttribute( geodesicWeight.cartesianPosition )

    #output Attributes  ----------------------------------------------------------------------------------------------------------------------------
    geodesicWeight.collision_Face = nAttr.create( "collision_Face", "col", OpenMaya.MFnNumericData.kInt,-1)
    nAttr.setStorable(1)
    geodesicWeight.addAttribute( geodesicWeight.collision_Face)
    
    geodesicWeight.output = nAttr.create( "output", "out" , OpenMaya.MFnNumericData.kDouble  ) 
    nAttr.setArray(1)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)
    nAttr.setUsesArrayDataBuilder(1)
    geodesicWeight.addAttribute(geodesicWeight.output) 


    #Affect Relationship Attributes  ---------------------------------------------------------------------------------------------------------------
    DriverList = [geodesicWeight.cartesianPosition,geodesicWeight.inputShape ]
    link_relashionShip(DriverList, geodesicWeight.output)
    link_relashionShip(DriverList, geodesicWeight.collision_Face)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(geodesicWeight())
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Bazillou2012", "1.0", "Any")
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
