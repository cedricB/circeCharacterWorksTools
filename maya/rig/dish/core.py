import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile
from functools import partial

author = 'cedric bazillou 2013'
version = 0.03

class dishBuilder:
    def __init__(self):
        self.tabCtrl_A = ''
        self.tabCtrl_B = ''
        self.canvasSize =[430,400]
        self.bundle_prgrss = ''
        self.bentoElements = 'CCW_TOOLS_bentoElem'
        self.foodField = ''
        self.IO =  IO()
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
             mc.tabLayout(self.tabCtrl_A,e=True,  h=618 )
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
        mc.text(l=' Bento root :')
        txFld = mc.textField( 'CCW_TOOLS_ROOT_data_dir_txFld' )
        psdFileRootBtn = mc.button(l='<' ,c=partial(self.collect_root, txFld ) )
        mc.setParent('..')

        mc.text(l='FoodType')
        self.foodField = mc.textField( 'CCW_TOOLS_FoodType_txFld',alwaysInvokeEnterCommandOnReturn=True )
        mc.textField( self.foodField,e=True, enterCommand=partial(self.validateModule, self.foodField  )  )
        mc.separator()
        mc.text(l='Description')
        mc.scrollField( editable=True, wordWrap=True, text='#Any relevant informations can be placed here' )
        mc.button(l='Flag bento root')
        mc.separator()
    def injectElement_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        mc.button(l='Scan current scene content',c=self.scanSceneGraph)
        mc.textScrollList( 'CCW_TOOLS_bentoElem',numberOfRows=10, allowMultiSelection=True)
        mc.button(l='Remove selected',h=36,c=self.removeNodeFromElementList)
    def defineDriver_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        mc.separator(style='none')
    #---------------------------------------------------------------------------------------- cookTab UI Helpers
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
        mc.button(l='Release bento',h=45)
        
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[1,'Flag Elements'])
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[2,'Expose Drivers'])
    #---------------------------------------------------------------------------------------- deliverTab UI Helpers
    
    #---------------------------------------------------------------------------------------- cook TAB
    def deliverTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.tabCtrl_A)
        mc.button(l='Compile bundle',c=self.IO.compile_bundle)
        self.bundle_prgrss = mc.progressBar('CCW_TOOLS_bundle_prgrss')
class dishEditor:
    def __init__(self):
         self.canvasSize =[430,400]
         self.IO =  IO()
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
        for dish in dishList:
            dishName = os.path.basename(dish).split('.zip')[0]
            mc.button(l=dishName,h=28,ann='test')
    def bentosFactory_UI(self,anchor):
        rgtTab = mc.tabLayout( p=anchor,innerMarginWidth=5, innerMarginHeight=5,h=self.canvasSize[1]-52)
        mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=rgtTab )
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
        if templateList is not None or len(templateList) > 0:
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
            UI().show()
    def createBundle(self,sourcePath,outputZip,root):
        myzip = zipfile.ZipFile(outputZip, 'w') 
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
        filteredDirlist = []

        for dir in dirlist:
            if os.path.isdir(os.path.join(modulePath,dir)) == True:
                filteredDirlist.append(os.path.join(modulePath,dir,'data.ma'))

        return filteredDirlist
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
    def expose_members():
        pass
    def process_root():
        pass
    def publish_driver():
        pass
