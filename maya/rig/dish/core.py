import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile
from functools import partial
import json

'''
* ..change is common
* ..space is cheap
* ..control outweighs performance


|Feature                          |Description  |
|:--------------------------------|:------------|
|Non-destructive                  | Every change you make is maintained in history; facilitating persistent undo/redo, traceable history of who did what and when, including incremental versioning with arbitrary metadata, like a changelog or description. All retrievable at any point in time. |
|Full disclosure                  | You may at any point in time browse to data at any hierarchical level using your native file-browser; read, write, modify, delete or debug malicious data with tools you know.    |
|Partial I/O                      | As a side-effect to its inherently simplistic design, reading and writing within large sets of data doesn't require reading everything into memory nor does it affect surrounding data; facilitating distributed collaborative editing. See [RFC13][] for more information.
|No limits on size nor complexity | Store millions of strings, booleans, matrices.. groups of matrices.. matrices of groups, strings, booleans and vectors. On consumer hardware, in a matter of megabytes, without compression. Then go ahead and store billions.
|Open specification, open source  | There are no mysteries about the inner-workings of the data that you write; you may write personal tools for debugging, graphical interfaces or extensions to the standard. The specifications are all laid out below and collaboration is welcome. (Want Open Metadata in Lua, Java, PHP or C++?)

### 

'''
author = 'cedric bazillou 2013'
version = 0.04

class dishBuilder:
    def __init__(self):
        self.scrollInfo  = ''
        self.assetListing  = ''
        self.bentoRoot = ''
        self.tabCtrl_A = ''
        self.tabCtrl_B = ''
        self.canvasSize =[430,400]
        self.bundle_prgrss = ''
        self.bentoElements = 'CCW_TOOLS_bentoElem'
        self.foodField = ''
        self.IO =  IO()
        self.factory = factory()
        self.defaultNodes = [u'time1', u'sequenceManager1', u'renderPartition',
        u'renderGlobalsList1', u'defaultLightList1', u'defaultShaderList1',
        u'postProcessList1', u'defaultRenderUtilityList1',
        u'defaultRenderingList1', u'lightList1',
        u'defaultTextureList1', u'lambert1', u'particleCloud1',
        u'initialShadingGroup', u'initialParticleSE', u'initialMaterialInfo',
        u'shaderGlow1', u'dof1', u'defaultRenderGlobals', 
        u'defaultRenderQuality', u'defaultResolution', u'defaultLightSet',
        u'defaultObjectSet', u'defaultViewColorManager', u'hardwareRenderGlobals',
        u'hardwareRenderingGlobals', u'characterPartition', u'defaultHardwareRenderGlobals',
        u'ikSystem', u'hyperGraphInfo', u'hyperGraphLayout', u'globalCacheControl', 
        u'dynController1', u'strokeGlobals', u'CustomGPUCacheFilter', u'objectTypeFilter74',
        u'persp', u'perspShape', u'top', u'topShape', u'front', u'frontShape', u'side', u'sideShape',
        u'lightLinker1', u'layersFilter', u'objectTypeFilter75', u'animLayersFilter',
        u'objectTypeFilter76', u'notAnimLayersFilter', u'objectTypeFilter77',
        u'defaultRenderLayerFilter', u'objectNameFilter4', u'renderLayerFilter',
        u'objectTypeFilter78', u'objectScriptFilter10', u'renderingSetsFilter',
        u'objectTypeFilter79', u'relationshipPanel1LeftAttrFilter', u'relationshipPanel1RightAttrFilter',
        u'layerManager', u'defaultLayer', u'renderLayerManager', u'defaultRenderLayer'] # 
    #---------------------------------------------------------------------------------------- widget Helpers 
    def resizeBuildTabs(self):
        tabIndex = mc.tabLayout(self.tabCtrl_A ,q=True,sti=True )
        if tabIndex == 1 :
             mc.tabLayout(self.tabCtrl_A,e=True,  h=620 )
        if tabIndex == 2 :
            mc.tabLayout(self.tabCtrl_A,e=True,  h=80 )
    #---------------------------------------------------------------------------------------- MAIN UI 
    def widget(self,widgetParent ):
        mc.text(l=' Current Path :')
        pathTxFld = mc.textField( 'buildDish_UI_data_dir_txFld',ed=False  )
        self.tabCtrl_A = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5,p=widgetParent  )
        
        #---------------------------------------------------------------------------------
        self.cookTab()
        #---------------------------------------------------------------------------------
        self.deliverTab()

        modulePath = ''.join(os.path.dirname(inspect.getfile(self.resizeBuildTabs))+'\src')
        mc.textField( pathTxFld,e=True,tx=modulePath)        
        mc.tabLayout(self.tabCtrl_A ,e=True,tabLabelIndex=[1,'Cook'])
        mc.tabLayout(self.tabCtrl_A ,e=True,tabLabelIndex=[2,'Deliver'])
        mc.tabLayout(self.tabCtrl_A ,e=True,cc=self.resizeBuildTabs )
    #---------------------------------------------------------------------------------------- cookTab UI sub Elements
    def flagRoot_UI(self):
        mc.rowLayout( numberOfColumns=3, columnWidth3=(80,(self.canvasSize[0]-80-20),20 ), adjustableColumn=2,cl3=('left','both','right'))
        mc.text(l='1. Bento root :')
        self.bentoRoot = mc.textField( 'CCW_TOOLS_ROOT_data_dir_txFld' )
        psdFileRootBtn = mc.button(l='<' ,c=partial(self.collect_root,  self.bentoRoot ) )
        mc.setParent('..')

        mc.text(l='2. FoodType')
        self.foodField = mc.textField( 'CCW_TOOLS_FoodType_txFld',alwaysInvokeEnterCommandOnReturn=True )
        mc.textField( self.foodField,e=True, enterCommand=partial(self.validateModule, self.foodField  )  )
        mc.separator()
        mc.text(l='3. Description')
        self.scrollInfo = mc.scrollField( editable=True, wordWrap=True, text='#Any relevant informations can be placed here' )
        mc.button(l='Flag bento root',c=self.validateRootData)
        mc.separator()
    def injectElement_UI(self ):
        slot = mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        anchorDock = mc.rowLayout(    numberOfColumns=2,
                            columnWidth2=(self.canvasSize[0]/5*2-30, self.canvasSize[0]/5*2-20 ),
                            adjustableColumn=1,
                            columnAlign=(1, 'right'),
                            columnAttach=[(1,'both',0), (2,'both',0)] ,w=self.canvasSize[0]-40)
        mc.columnLayout( adjustableColumn=True  )
        mc.button(l='4-a. Scan current scene content',c=self.scanSceneGraph)

        mc.columnLayout( adjustableColumn=True,p=anchorDock    )
        mc.button(l='4-b. Remove selected' ,c=self.removeNodeFromElementList)
        
        mc.setParent(slot)
        self.assetListing  = mc.textScrollList( 'CCW_TOOLS_bentoElem',numberOfRows=10, allowMultiSelection=True )
        mc.button(l='4-c. Inject Elements',h=36 ,c=self.validateDishData)
    def defineDriver_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        
        anchorDock = mc.rowLayout(    numberOfColumns=2,
                            columnWidth2=(self.canvasSize[0]/5*2, 95 ),
                            adjustableColumn=2,
                            columnAlign=(1, 'right'),
                            columnAttach=[(1,'both',0), (2,'both',0)] ,w=self.canvasSize[0])
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedOut',mw=5,mh=5  )
        mc.button(l='Scan Elements' )
        mc.textScrollList( 'CCW_TOOLS_bentoDriver',numberOfRows=10, allowMultiSelection=True)
        mc.button(l='Remove Elements' ,w=40)
        
        mc.text(l='driver element in this list',p=anchorDock)
    #---------------------------------------------------------------------------------------- cookTab UI Helpers
    def validateDishBeforePublish(self,*args):
        root = mc.textField( self.bentoRoot,q=True,tx=True)
        erroChk = 0
        if len(root)== 0:
            print 'Please pick a root object'
        else:
            attributeList = ['foodType','moduleInfos','element']
            feedBackList = ['found no foodType data in this dish','found no moduleInfos data in this dish','found no element data in this dish']
            for index, checkObj in enumerate(attributeList): 
                if mc.attributeQuery(checkObj,node=root,ex=True) == False:
                    erroChk += 1
                    mc.warning(feedBackList[index])
            if erroChk == 0:
                self.factory.publish_driver(root)
                print 'publis succes'
    def validateRootData(self,*args):
        root = mc.textField( self.bentoRoot,q=True,tx=True)
        foodType = mc.textField( self.foodField,q=True,tx=True)
        erroChk = 0
        chkList = [root,foodType]
        feedBackList = ['Please pick a root object','Please define a unique foodType']
        for index, checkObj in enumerate(chkList): 
            if checkObj is None or len(checkObj)== 0:
                erroChk += 1
                mc.warning(feedBackList[index])
        if erroChk == 0:
            infoData = mc.scrollField( self.scrollInfo ,q=True,tx=True)
            self.factory.process_root(  root,
                                        foodType,
                                        infoData )
    def validateDishData(self,*args):
        root = mc.textField( self.bentoRoot,q=True,tx=True)
        assetListing = mc.textScrollList( self.assetListing  ,q=True,ai=True)
        erroChk = 0
        chkList = [root,assetListing]
        feedBackList = ['Please pick a root object','Please Fill the Element List']
        for index, checkObj in enumerate(chkList): 
            if checkObj is None or len(checkObj)== 0:
                erroChk += 1
                mc.warning(feedBackList[index])
        if erroChk == 0:
            self.factory.expose_members(root,assetListing)
    def validateModule(self ,fieldRef,*args):
        foodTx = mc.textField( self.foodField,q=True,tx=True)
        if foodTx is not None:
            modulePath = ''.join(os.path.dirname(inspect.getfile(self.resizeBuildTabs))+'\src')
            filelist= os.listdir(modulePath)
            if foodTx in  filelist:
                prt = mc.promptDialog(    title='foodType Alert', 
                                    message='Please choose another foodType name:',
                                    button=['OK'],
                                    defaultButton='OK')
                mc.textField( self.foodField,e=True,tx='')
            else:
                OpenMaya.MGlobal.displayInfo( '** %s is valid foodType, Please fill the other UI part to proceed'% foodTx )
    def collect_root(self,fieldRef,*args):
        sel = mc.ls(sl=True,fl=True)
        mc.textField(fieldRef,e=True,tx='')
        if sel is None or len(sel)<1  :                
            return 
        else:
            mc.textField(fieldRef,e=True,tx=sel[0])
    def scanSceneGraph(self ,*args):
        sceneGraph = mc.ls()
        mc.textScrollList(self.bentoElements,e=True,ra=True)
        
        filterList = [ item for item in sceneGraph if item not in self.defaultNodes]
        
        for obj in filterList:
            mc.textScrollList(self.bentoElements,e=True,a=obj)
    def removeNodeFromElementList(self ,*args):
        selectedItems = mc.textScrollList(self.bentoElements,q=True,selectItem=True)
        if selectedItems is not None:
            selectedItems.reverse()
            for obj in selectedItems :
                mc.textScrollList(self.bentoElements,e=True,removeItem=obj)
    #---------------------------------------------------------------------------------------- cook TAB
    def cookTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.tabCtrl_A)
        buildDish_UI_Anchor = mc.frameLayout( collapsable=False,labelVisible=False, mw=5,mh=5,borderStyle='out' )
        
        self.flagRoot_UI()        
        self.tabCtrl_B = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5 )        
        self.injectElement_UI() 
        self.defineDriver_UI()

        # publish Elements
        mc.setParent(buildDish_UI_Anchor)
        mc.separator()
        mc.button(l='Release bento',h=45,c=self.validateDishBeforePublish)
        
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[1,'4. Flag Elements'])
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[2,'5. Expose Drivers'])
    #---------------------------------------------------------------------------------------- deliverTab UI Helpers
    
    #---------------------------------------------------------------------------------------- deliver TAB
    def deliverTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.tabCtrl_A)
        mc.button(l='Compile bundle',c=self.IO.compile_bundle)
        self.bundle_prgrss = mc.progressBar('CCW_TOOLS_bundle_prgrss')
class dishEditor:
    def __init__(self):
         self.canvasSize =[430,400]
         self.IO =  IO()
         self.InfosTab = ''
    def widget(self,widgetParent):
        mc.columnLayout( adjustableColumn=True, rs=5 ,p=widgetParent)
        mc.rowLayout(   numberOfColumns=3, 
                        columnWidth2=(80,(self.canvasSize[0]-80-20)),
                        adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        pathTxFld = mc.textField( 'buildEditor_UI_data_dir_txFld',ed=False  )
        mc.setParent('..')
        mc.separator()
        anchorDock = mc.rowLayout(    numberOfColumns=2,
                                    columnWidth2=(self.canvasSize[0]/5*2+12, 75 ),
                                    adjustableColumn=2,
                                    columnAlign=(1, 'right'),
                                    columnAttach=[(1,'both',0), (2,'both',0)] ,w=self.canvasSize[0])

        self.exposedBentos_UI(anchorDock)
        #------------------------------------------------------------------------------------------------------------
        self.bentosFactory_UI(anchorDock)

        modulePath = ''.join(os.path.dirname(inspect.getfile(self.exposedBentos_UI)))
        mc.textField( pathTxFld,e=True,tx=modulePath)
    def exposedBentos_UI(self,anchor):
        leftPanel = mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5,p=anchor )
        mc.columnLayout( adjustableColumn=True, rs=5 )
        mc.text(l='Available Bentos')
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8)
        scrollWdth = mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0]/5*2-27,h=self.canvasSize[1]-20)
        dishList = self.IO.exposeZipTemplate()
        
        dishName = ''
        for dish in dishList:
            dishName = os.path.basename(dish).split('.zip')[0]
            btn = mc.button(l=dishName,h=28,ann='test')
            mc.button(btn,e=True,c=partial( self.switch_to_bent, dishName ,dish ))

    def switch_to_bent(self,dishName,dishFile,*args):
        archive = zipfile.ZipFile(dishFile, 'r')
        jsonFile = archive.read('dish.ini')
        jsondata = json.loads(jsonFile)  
        archive.close()

        #Clear chld
        chldrn = mc.layout( self.InfosTab, query=True, childArray=True )
        for chld in chldrn:
            mc.deleteUI(chld)

        mc.columnLayout( adjustableColumn=True ,p=self.InfosTab )
        mc.text( 'CCW_TOOLS_DISHNAME_txFld', l='', h=36  )
        #print jsondata['moduleInfos']
        ll = """<html>
            <body>
            <h1>%s</h1></body>
        </html>
        """%(dishName )
        mc.text( 'CCW_TOOLS_DISHNAME_txFld',e=True,l=ll,font='boldLabelFont')        
        mc.scrollField( editable=False, wordWrap=True, text=jsondata['moduleInfos'] ,h=120)
        mc.separator()
    def bentosFactory_UI(self,anchor):
        rgtTab = mc.tabLayout( p=anchor,innerMarginWidth=5, innerMarginHeight=5,h=self.canvasSize[1]-52)
        self.InfosTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.text(l='')

        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.text(l='')
        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.text(l='')
        
        #######################################################################
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[1,'Infos'])
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[2,'Tools'])
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[3,'Member list'])
        
        dishList = self.IO.exposeZipTemplate()
        self.switch_to_bent( os.path.basename(dishList[0]).split('.zip')[0],dishList[0] ) 
class Tool:
    def __init__(self):
        self.windowRef ='CCW_bentoUI'
        self.tmpleLib =  IO()
        self.canvasSize =[430,400]
        self.UI_TAB = ''
        self.ToDelete = []
        self.toresizeCtrl = ''
        self.toresizeCtrlB = ''
        self.dishBuilder = dishBuilder()
        self.dishEditor  = dishEditor()
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="CCW_Bento Manager  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
 
        self.UI_TAB = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        dishList = self.tmpleLib.exposeZipTemplate()
        if len(dishList) == 0:
            self.dishBuilder.widget(self.UI_TAB)
        else:
            self.dishEditor.widget(self.UI_TAB)

        mc.textField( 'copyrigth_txFld',ed=False ,tx=' AUTHOR : cedric BAZILLOU 2014      --       http://circecharacterworks.wordpress.com/ ',p=self.UI_TAB  )
        
        mc.showWindow( self.windowRef)
        mc.window( self.windowRef,e=True, widthHeight=(self.canvasSize[0],self.canvasSize[1]) )
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
            
                zipPath = os.path.join(tmpleRoot,tmpleName+'.zip')
                self.createBundle(tmpleDir,zipPath,tmpleRoot)
                mc.progressBar('CCW_TOOLS_bundle_prgrss', edit=True, step=1)
            mc.progressBar('CCW_TOOLS_bundle_prgrss', edit=True, endProgress=True)
            Tool().show()
    def createBundle(self,sourcePath,outputZip,root):
        myzip = zipfile.ZipFile(outputZip, 'w') 
        myzip.write( os.path.join( sourcePath ,'dish.ini') ,  r'\dish.ini'  )
        myzip.write( os.path.join( sourcePath ,'widget.py') ,  r'\widget.py'  )
        myzip.write( os.path.join( sourcePath ,'data.ma') ,  r'\data.ma') 
        myzip.close()
    def exposeZipTemplate(self):
        modulePath = os.path.dirname(inspect.getfile(self.merge))
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
        scrpDir = mc.internalVar(userScriptDir=True)
        localModuleToMerge = os.path.join(scrpDir,newModuleName+'.01.ma')
        
        outputFile = open(localModuleToMerge, "w") 
        with open(sourcePath) as f:        
            for line in f:
                if prfxToReplace in line:
                    nwLn = line.replace(prfxToReplace,newModuleName)
                    outputFile.writelines( nwLn)
                else:
                    outputFile.writelines(line)
                
        outputFile.close()
        ## ------------------------------- inject it in your scene
        mc.file(localModuleToMerge,i=True)
        OpenMaya.MGlobal.displayInfo( '** %s was successfully merge in your scene'% newModuleName )
        mc.sysFile(localModuleToMerge,delete=True)  
    def clean_asset_file():
        pass
class factory:
    def expose_members(selfroot,
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
            attributeList = ['foodType','moduleInfos']
            dataList = [foodType,moduleInfos]
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
