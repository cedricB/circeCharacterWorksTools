import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile
from functools import partial
import json
import uuid
import datetime

if 'dish.data' not in sys.modules.keys():
    frme = inspect.currentframe()
    frameData =  inspect.getframeinfo(frme)
    modulePath = os.path.dirname(frameData[0])
    modulePath = os.path.dirname(modulePath)
    sys.path.append(modulePath)

    import dish.dishData as attrToFilter
    reload(attrToFilter)


author = 'cedric bazillou 2013'
version = 0.05

class IO:
    def compile_bundle(self,*args):
        templateList = self.exposeBundles()

        if templateList is not None and len(templateList) > 0:
            mc.progressBar( 'CCW_TOOLS_bundle_prgrss',
            edit=True,
            beginProgress=True,
            isInterruptable=True,
            status='Please wait ...' ,
            maxValue=len(templateList)    )
        
            for idx in range(len(templateList)):
                tmpleName = os.path.basename(os.path.dirname(templateList[idx]))
                tmpleDir = str(os.path.dirname(templateList[idx]))
                tmpleRoot = os.path.dirname(inspect.getfile(self.merge))
                tmpleRoot = r''.join(tmpleRoot)
                
                tmpleRoot = os.path.join(tmpleRoot,'lunchBox')
            
                zipPath = os.path.join(tmpleRoot,tmpleName+'.zip')
                self.createBundle(tmpleDir,zipPath,tmpleRoot)
                mc.progressBar('CCW_TOOLS_bundle_prgrss', edit=True, step=1)
            mc.progressBar('CCW_TOOLS_bundle_prgrss', edit=True, endProgress=True)
    def createBundle(self,sourcePath,outputZip,root):
        myzip = zipfile.ZipFile(outputZip, 'w') 
        myzip.write( os.path.join( sourcePath ,'dish.ini') ,  r'\dish.ini'  )
        myzip.write( os.path.join( sourcePath ,'widget.py') ,  r'\widget.py'  )
        myzip.write( os.path.join( sourcePath ,'data.ma') ,  r'\data.ma') 
        myzip.close()
    def exposeZipTemplate(self):
        modulePath = os.path.dirname(inspect.getfile(self.merge))
        modulePath = os.path.join(modulePath,'lunchBox')
        filelist= os.listdir(modulePath)
        modulelist = [ f for f in filelist if  f.endswith('.zip')  ]
        for k in range(len(modulelist)):
            modulelist[k] = os.path.join(modulePath,modulelist[k])
        return modulelist
    def exposeBundles(self):
        modulePath = os.path.dirname(inspect.getfile(self.merge))
        modulePath = os.path.join(modulePath,'src')

        dirlist= os.listdir(modulePath)
        if dirlist is not None and len(dirlist)> 0:
            filteredDirlist = []

            for dir in dirlist:
                if os.path.isdir(os.path.join(modulePath,dir)) == True:
                    filteredDirlist.append(os.path.join(modulePath,dir,'data.ma'))

            return filteredDirlist
        else:
            return None
    def merge(self,sourcePath,prfxToReplace,newModuleName):
        ## ------------------------------- first create temp module
        ## ------------------------------- then name elements properly
        scrpDir = mc.internalVar(userScriptDir=True)
        localModuleToMerge = os.path.join(scrpDir,newModuleName+'.01.ma')
        archive = zipfile.ZipFile(sourcePath, 'r')
        jsonFile = archive.open('data.ma')
        
        outputFile =  open(localModuleToMerge, "w") 
       
        for line in jsonFile:
            if prfxToReplace in line:
                nwLn = line.replace(prfxToReplace,newModuleName)
                outputFile.writelines( nwLn)
            else:
                outputFile.writelines(line)
        archive.close()   
        outputFile.close()
        ## ------------------------------- inject it in your scene
        mc.file(localModuleToMerge,i=True)
        mc.sysFile(localModuleToMerge,delete=True)  
        
        #now list new imported module
        content = mc.ls(type='transform')
        attributeList = ['foodType','uuID']
        nwNode = []
        for obj in content:
            idx = 0
            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=obj,ex=True) == True:
                    idx += 1
            if idx > 1:
                nwNode.append(obj)
        mc.setAttr(nwNode[0] +'.uuID',l=False)
        mc.deleteAttr(nwNode[0] +'.uuID')
        
        foodTpe = mc.getAttr(nwNode[0] +'.foodType')
        OpenMaya.MGlobal.displayInfo( '**The %s dish  %s was successfully merge in your scene'% (foodTpe, newModuleName) )
        return nwNode[0]
    def clean_asset_file():
        pass
class factory:
    def expose_members(self ,
                        root,
                        assetListing ):
        if mc.objExists(root)==True:
            attributeList = [ 'element']

            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=root,ex=True) == False:
                    mc.addAttr(root,ln=attributeList[index] ,m=True,h=True,k=False)

            for index, elemObj in enumerate(assetListing):
                try:
                    mc.connectAttr(elemObj+'.nodeState','%s.%s[%s]'%( root ,attributeList[0], index), f=True)
                except:
                    pass
            OpenMaya.MGlobal.displayInfo( '** Module elements were added to %s '% root )
    def process_root(self,  root,
                            foodType,
                            moduleInfos ):
        if mc.objExists(root)==True:
            flagKey = str(uuid.uuid4().hex)
            attributeList = ['foodType','moduleInfos']#,'uuID'
            dataList = [foodType,moduleInfos,flagKey]
            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=root,ex=True) == False:
                    mc.addAttr(root,ln=attributeList[index],dt='string')
                mc.setAttr('%s.%s'%(root ,attributeList[index] ),l=False)
                mc.setAttr('%s.%s'%(root ,attributeList[index] ) ,dataList[index],type='string')
                mc.setAttr('%s.%s'%(root ,attributeList[index] ),l=True)
            OpenMaya.MGlobal.displayInfo( '** %s was successfully Flagged'% root )
    def publish_driver(self,root):
        modulePath = os.path.dirname(inspect.getfile(self.expose_members))
        attributeList = ['foodType','moduleInfos','element']
        
        foodType = mc.getAttr('%s.%s'%(root,attributeList[0]))
        directory = os.path.join(os.path.join(modulePath,'src'),foodType)

        if not os.path.isdir(directory):
            os.makedirs(directory)
        targetFile  = os.path.join(directory,'data.ma')
        filename    = os.path.join(directory,'dish.ini')
        widgetname    = os.path.join(directory,'widget.py')
        
        fo = open(widgetname, "w")
        fo.close()
        
        attributeList = ['foodType','moduleInfos' ]
        bakedData = {}
        
        for attr in attributeList:
            dat = mc.getAttr('%s.%s'%(root,attr))
            if dat is None or len(dat)< 1 :
                dat = []
            bakedData[attr]= dat 
        
        mc.select (root,r=True)       
        mc.file(targetFile,force=True,typ="mayaAscii",pr=True, es=True)
        
        try:
            jsondata = json.dumps(bakedData ,sort_keys=True, indent=4)
            fd = open(filename, 'w')
            fd.write(jsondata)
            fd.close()
        except:
            print 'ERROR writing', filename
            pass
    def collect_similar_dish(self,expextedFood):
        content = mc.ls(type='transform')
        attributeList = ['foodType' ]
        nwNode = []
        for obj in content:
            idx = 0
            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=obj,ex=True) == True:
                    if mc.getAttr(obj+'.'+attributeList[index]) == expextedFood  :
                        idx = 2
            if idx > 1:
                nwNode.append(obj)
        return nwNode
    def read_dish_data(self , root):
        attributeList = ['foodType','moduleInfos' ]
        dataList = {}
        for  attr in  attributeList :
            dataList[attr] = ''
            if mc.attributeQuery(attr,node=root,ex=True) == True:
                dataList[attr] = mc.getAttr('%s.%s'%(root,attr))
        
        dataList['element'] = ''
        if mc.attributeQuery('element',node=root,ex=True) == True:
            cntList = mc.listConnections('%s.%s'%(root,'element'),sh=True)
            if cntList is not None and len(cntList)>0:
                dataList['element'] = []
                dataList['element'].extend(cntList)
        return dataList
    def retrieve_IO_Connections(self,root, IO_Index ):
        plugList = ['recipe.py']
        for plugin in plugList:
            if not mc.pluginInfo(plugin,q=True,l=True):
                mc.loadPlugin(plugin)
        attributeList = ['foodType','moduleInfos']#,'uuID'
        chkErrr = 0
        for index, attr in enumerate(attributeList):
            if mc.attributeQuery(attributeList[index],node=root,ex=True) == False:
                chkErrr += 1

        if chkErrr > 0:
            return None

        attributeList = ['recipe']
        cnList = ['input', 'output']   
        linkList =  ['inlink', 'outLink']   
        labelList =  ['inLabel', 'outLabel'] 
        widgetID_List =  ['inWidgetID', 'outWidgetID'] 
        hub_List =  ['input_useParentHub', 'output_useParentHub'] 
        for  attr in  attributeList :
            if mc.attributeQuery(attr,node=root,ex=True) == False:
                storage = mc.createNode('recipe',n=''.join((root,'_',attr,'1')))
                mc.addAttr(root,ln=attr,k=False,h=True)
                mc.connectAttr(storage+'.nodeState' ,root+'.'+attr ,f=True)
                
                mc.setAttr(storage+'.author',attrToFilter.recipeData['author'],type='string')
                mc.setAttr(storage+'.gitSource',attrToFilter.recipeData['gitSource'],type='string')
                
                releaseDate =  str( datetime.date.today())
                mc.setAttr(storage+'.releaseDate',releaseDate,type='string')
        dataList = {} 
        storage = mc.listConnections(root+'.'+attributeList[0])
        if storage is None:
            attributeList = ['recipe']
            storage = mc.createNode('recipe',n=''.join((root,'_',attributeList[0],'1')))
            mc.connectAttr(storage+'.nodeState' ,root+'.'+attributeList[0] ,f=True)
               
            mc.setAttr(storage+'.author',attrToFilter.recipeData['author'],type='string')
            mc.setAttr(storage+'.gitSource',attrToFilter.recipeData['gitSource'],type='string')
            
        else:
            storage = storage[0]  

        idxList = mc.getAttr(storage+'.'+cnList[IO_Index],mi=True)
        if idxList is None:
            return None
            
        for index, value in enumerate(idxList):
            driverAttr  = mc.connectionInfo(storage+'.'+cnList[IO_Index]+'[%s].'%value+linkList[IO_Index],sfd=True)
            label       = mc.getAttr(storage+'.'+cnList[IO_Index]+'[%s].'%value+ labelList[IO_Index])
            widgetID    = mc.getAttr(storage+'.'+cnList[IO_Index]+'[%s].'%value+ widgetID_List[IO_Index] )
            hubState    = mc.getAttr(storage+'.'+cnList[IO_Index]+'[%s].'%value+ hub_List[IO_Index] )

            if hubState == True:
                driverAttr = driverAttr.split('[')[0]
            
            labelLINK       =  (storage+'.'+cnList[IO_Index]+'[%s].'%value+ labelList[IO_Index])
            widgetIDLINK    =  (storage+'.'+cnList[IO_Index]+'[%s].'%value+ widgetID_List[IO_Index] )
            dataList[index] = [driverAttr,label,widgetID,labelLINK,widgetIDLINK,hubState]
        
        
        return dataList
    def publish_IO_Connections(self,root,targetAttribute,IO_Index ):
        if mc.objExists(targetAttribute) == False :
            return

        attributeList = ['recipe']
        cnList = ['input', 'output']     
        linkList =  ['inlink', 'outLink']   
        hub_List =  ['input_useParentHub', 'output_useParentHub'] 
        storage = mc.listConnections(root+'.'+attributeList[0])   
        
        print storage,root
        if storage is None:
            attributeList = ['recipe']
            storage = mc.createNode('recipe',n=''.join((root,'_',attributeList[0],'1')))
            mc.connectAttr(storage+'.nodeState' ,root+'.'+attributeList[0] ,f=True)
        else:
            storage = storage[0]  

        idxList = mc.getAttr(storage+'.'+cnList[IO_Index] ,mi=True)
        idx = 0
        
        trgRoot = targetAttribute.split('.')
        multichk = False
        if mc.attributeQuery(trgRoot[1],node=trgRoot[0],multi=True) == True:
            targetAttribute = targetAttribute+'[0]'
            multichk = True
        if idxList is not None:
            idx = idxList[-1]+1
        mc.connectAttr( targetAttribute, storage + '.%s[%s].%s'%(cnList[IO_Index],idx,linkList[IO_Index]),f=True)

        if multichk == True:
            mc.setAttr(storage + '.%s[%s].%s'%(cnList[IO_Index],idx,hub_List[IO_Index]),1)
            mc.setAttr(storage + '.%s[%s].%s'%(cnList[IO_Index],idx,hub_List[IO_Index]),l=True)
    def delete_Connections_at_targetIndex(self,root,targetIndex,IO_Index ):
        attributeList = ['recipe']
        cnList = ['input', 'output']          
        storage = mc.listConnections(root+'.'+attributeList[0])
        if storage is None:
            attributeList = ['recipe']
            storage = mc.createNode('recipe',n=''.join((root,'_',attributeList[0],'1')))
            mc.connectAttr(storage+'.nodeState' ,root+'.'+attributeList[0] ,f=True)
        else:
            storage = storage[0]  
            
   
        idxList = mc.getAttr(storage+'.'+cnList[IO_Index],mi=True)
        idx = 0
        if idxList is None:
            return
        else:
            targetIndex = idxList[targetIndex]
            if targetIndex in idxList :
                mc.removeMultiInstance(storage+'.'+cnList[IO_Index]+'[%s]'%targetIndex,b=True)
