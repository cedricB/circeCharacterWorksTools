'''
########################################################################
#                                                                      #
#             udon.py                                                  #
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
        restric curve length

    I N S T A L L A T I O N:
        Copy the "udon.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "udon"
kPluginNodeId = OpenMaya.MTypeId(0xFC79345) 

outputCurveFn = OpenMaya.MFnNurbsCurve()
crvDatStock = OpenMaya.MFnNurbsCurveData()
crbOBJ = crvDatStock.create()

tmpPointList = OpenMaya.MPointArray()
pointT = OpenMaya.MPoint()

__plug_in__Version = "1.3"
__author = "Bazillou2013"


class udon(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    def check_curve_plugs(self,actionData):
        inputMeshConnected = False
        if actionData.isNull() == False :
            inputMeshConnected = True
        return inputMeshConnected
    def computKnotList (self,degreeN ,vertLen):

        spansM  = float(vertLen-degreeN)
        path_knots = OpenMaya.MDoubleArray()
        path_knots.append(0.0)
        path_knots.append(0.0)

        for k in range(int(spansM)+1) :
            path_knots.append(k)
        path_knots.append(spansM)
        path_knots.append(spansM)

        return path_knots
    def compute(self,Plug,Data):
        #Layout necessary output / input handle to gather data

        InputData       = Data.inputValue(self.inputShape ).asNurbsCurveTransformed()
        output_handle   = Data.outputValue(self.path)
        startLength_val = Data.inputValue(self.startLength ).asDouble()
        stretch_val     = Data.inputValue(self.stretch ).asDouble()

        #--------------------------------------------------------------------- Compute if a mesh is connected

        InputShapeConnected = self.check_curve_plugs(InputData)

        if InputShapeConnected == False:
            return 
        else:
            nrbMFn = OpenMaya.MFnNurbsCurve( InputData)

            nrbMFn.getCVs (tmpPointList,OpenMaya.MSpace.kObject)
            endLen = nrbMFn.length(0.0001)
            initLen = endLen *4.0+startLength_val

            start_util = OpenMaya.MScriptUtil()
            start_util.createFromDouble(0.0)
            startPtr = start_util.asDoublePtr()  

            end_util = OpenMaya.MScriptUtil()
            end_util.createFromDouble(0.0)
            endPtr = end_util.asDoublePtr()  

            nrbMFn.getKnotDomain(startPtr,endPtr)
            endVal = OpenMaya.MScriptUtil().getDouble(endPtr)

            endVector = nrbMFn.tangent(endVal,OpenMaya.MSpace.kObject).normal()*initLen
            lastId = tmpPointList.length()-1
            tmpPointList.append(tmpPointList[lastId]+endVector)


            path_knots = OpenMaya.MDoubleArray()
            path_knotsB = OpenMaya.MDoubleArray()
            crvDgre = 1
            pointList = OpenMaya.MPointArray(tmpPointList.length())
            spanNum = tmpPointList.length()-1

            for k in range(tmpPointList.length()) :
                path_knots.append(k)
            outputCurveFn.create( tmpPointList, path_knots, crvDgre,OpenMaya.MFnNurbsCurve.kOpen, False, False,  crbOBJ )

            blndLen = (endLen-startLength_val)*stretch_val + startLength_val
            
            #now slide point on this path
            ratio = 1.0/float(spanNum)
            for k in range(tmpPointList.length()) :
                lenTmp = k*ratio*blndLen
                crvPrm = outputCurveFn.findParamFromLength(lenTmp)
                outputCurveFn.getPointAtParam(crvPrm , pointT,OpenMaya.MSpace.kObject)
                pointList.set(pointT,k)

            crvDgre = 0
 
            if pointList.length() == 2 :
                crvDgre = 1
                for k in range(pointList.length()) :
                    path_knotsB.append(k)

            if pointList.length() == 3:
                crvDgre = 2
                path_knotsB.clear()
                path_knotsB.append(0.0)
                path_knotsB.append(0.0)
                path_knotsB.append(1.0)
                path_knotsB.append(1.0)

            if pointList.length() > 3 :
                crvDgre = 3
                path_knotsB = self.computKnotList ( crvDgre,pointList.length())

            outputCurveFn.create( pointList , path_knotsB, crvDgre,OpenMaya.MFnNurbsCurve.kOpen, False, False,  crbOBJ )

            output_handle.setMObject(crbOBJ)
            output_handle.setClean()

def link_relashionShip( DriverList, driven_Attribute):
    for driver in DriverList:
        udon.attributeAffects(driver,driven_Attribute)
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr =  OpenMaya.MFnCompoundAttribute()
    typed_Attr =  OpenMaya.MFnTypedAttribute()
    #input Attributes  ----------------------------------------------------------------------------------------------------------------------------
    inputShape_Attr =  OpenMaya.MFnTypedAttribute()     
    udon.inputShape = inputShape_Attr.create( "inputShape", "inS", OpenMaya.MFnNurbsCurveData.kNurbsCurve )
    inputShape_Attr.setStorable(0)
    inputShape_Attr.setKeyable(0)
    inputShape_Attr.setHidden(True)
    inputShape_Attr.setArray(0)
    udon.addAttribute( udon.inputShape )
    
    udon.startLength = nAttr.create( "startLength", "lg", OpenMaya.MFnNumericData.kDouble,1.0)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0.0001)
    udon.addAttribute(udon.startLength )
    
    udon.stretch = nAttr.create( "stretch", "srt", OpenMaya.MFnNumericData.kDouble,0.0)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    nAttr.setStorable(1)
    udon.addAttribute(udon.stretch  )

    #output Attributes  ----------------------------------------------------------------------------------------------------------------------------    

    udon.path = typed_Attr.create( "path", "ph", OpenMaya.MFnNurbsCurveData.kNurbsCurve )
    typed_Attr.setStorable(0)
    typed_Attr.setKeyable(0)
    typed_Attr.setHidden(True)
    udon.addAttribute( udon.path)

    #Affect Relationship Attributes  ---------------------------------------------------------------------------------------------------------------
    DriverList = [udon.inputShape,udon.startLength,udon.stretch ]
    link_relashionShip(DriverList, udon.path)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(udon())
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
