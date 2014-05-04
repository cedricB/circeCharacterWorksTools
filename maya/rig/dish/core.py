import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile

author = 'cedric bazillou 2013'
version = 0.02

class UI:
    def __init__(self):
        self.windowRef ='CCW_bentoUI'
        self.tmpleLib =  IO()
        self.canvasSize =[430,400]
        self.UI_TAB = ''
        self.ToDelete = []
        self.toresizeCtrl = ''
        self.toresizeCtrlB = ''
    def resizeTab_In_Compile(self):
        tabIndex = mc.tabLayout(self.toresizeCtrl ,q=True,sti=True )
        if tabIndex == 1 :
             mc.tabLayout(self.toresizeCtrl,e=True,  h=592 )
        if tabIndex == 2 :
            mc.tabLayout(self.toresizeCtrl,e=True,  h=80 )
    def injectElement_Tab(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.toresizeCtrlB)
        mc.button(l='Scan current scene content')
        mc.textScrollList( 'CCW_TOOLS_bentoElem',numberOfRows=10, allowMultiSelection=True)
        mc.button(l='Remove selected',h=36)
        
    def defineDriver_Tab(self, ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.toresizeCtrlB)
        mc.separator()
    def flagRoot_tab(self):
        mc.text(l='FoodType')
        mc.textField( 'CCW_TOOLS_FoodType_txFld', )
        mc.separator()
        mc.text(l='Description')
        mc.scrollField( editable=True, wordWrap=True, text='#Any relevant informations can be placed here' )
        mc.button(l='Flag bento root')
        mc.separator()
    def bundleTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.toresizeCtrl)
        mc.button(l='Compile bundle',c=self.tmpleLib.compile_bundle)
        mc.progressBar('CCW_TOOLS_bundle_prgrss')
        
        
        mc.tabLayout(self.toresizeCtrl ,e=True,tabLabelIndex=[1,'Cook'])
        mc.tabLayout(self.toresizeCtrl ,e=True,tabLabelIndex=[2,'Deliver'])
        mc.tabLayout(self.toresizeCtrl ,e=True,cc=self.resizeTab_In_Compile )
    def CompileTab(self):
        mc.text(l=' Current Path :')
        pathTxFld = mc.textField( 'data_dir_txFld',ed=False  )
        self.toresizeCtrl = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5,p=self.UI_TAB  )
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.toresizeCtrl)
        anchorA = mc.frameLayout( collapsable=False,labelVisible=False, mw=5,mh=5,borderStyle='out' )
        
        self.flagRoot_tab()        
        self.toresizeCtrlB = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5 )        
        self.injectElement_Tab() 
        self.defineDriver_Tab()

        
        mc.setParent(anchorA)
        mc.separator()
        mc.button(l='Release bento',h=45)
        
        #---------------------------------------------------------------------------------
        self.bundleTab()
        

        modulePath = ''.join(os.path.dirname(inspect.getfile(self.bentoListing))+'\src')
        mc.textField( pathTxFld,e=True,tx=modulePath)
        
        mc.tabLayout(self.toresizeCtrlB ,e=True,tabLabelIndex=[1,'Flag Elements'])
        mc.tabLayout(self.toresizeCtrlB ,e=True,tabLabelIndex=[2,'Expose Drivers'])
    def leftPanel_in_bentoListing(self,anchor):
        leftPanel = mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5,p=anchor )
        mc.columnLayout( adjustableColumn=True, rs=5 )
        mc.text(l='Available Bentos')
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8)
        scrollWdth = mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0]/5*2-27,h=self.canvasSize[1]-20)
        bndList = self.tmpleLib.exposeZipTemplate()
        for n in range(len(bndList) ):
            templateCls = os.path.basename(bndList[n]).split('.zip')[0]
            mc.button(l=templateCls,h=28,ann='test')
    def rigthPanel_in_bentoListing(self,anchor):
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
    def bentoListing(self):
        mc.columnLayout( adjustableColumn=True, rs=5 ,p=self.UI_TAB)
        mc.rowLayout( numberOfColumns=3, columnWidth2=(80,(self.canvasSize[0]-80-20)), adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        pathTxFld = mc.textField( 'data_dir_txFld',ed=False  )
        mc.setParent('..')
        mc.separator()
        listDock = mc.rowLayout( numberOfColumns=2, columnWidth2=(self.canvasSize[0]/5*2+12, 75 ), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] ,w=self.canvasSize[0])

        self.leftPanel_in_bentoListing(listDock)
        #------------------------------------------------------------------------------------------------------------
        self.rigthPanel_in_bentoListing(listDock)
        modulePath = ''.join(os.path.dirname(inspect.getfile(self.CompileTab)))
        mc.textField( pathTxFld,e=True,tx=modulePath)
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="CCW_Bento Manager  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
 
        self.UI_TAB = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        bndList = self.tmpleLib.exposeZipTemplate()
        if len(bndList) == 0:
            self.CompileTab()
        else:
            self.bentoListing()

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
