import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile

author = 'cedric bazillou 2013'
version = 0.02

class UI:
    def __init__(self):
        self.windowRef ='CCW_templateUI'
        self.tmpleLib =  lib()
        self.canvasSize =[430,400]
        self.UI_TAB = ''
        self.ToDelete = []
    def CompileTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.UI_TAB)
        mc.button(l='Compile bundle',c=self.tmpleLib.compile_bundle)
        mc.progressBar('CCW_TOOLS_bundle_prgrss')
    def leftPanel_in_templateListing(self,anchor):
        leftPanel = mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5,p=anchor )
        mc.columnLayout( adjustableColumn=True, rs=5 )
        mc.text(l='Available Template')
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8)
        scrollWdth = mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0]/5*2-27,h=self.canvasSize[1]-20)
        bndList = self.tmpleLib.exposeZipTemplate()
        for n in range(len(bndList) ):
            templateCls = os.path.basename(bndList[n]).split('.zip')[0]
            mc.button(l=templateCls,h=28,ann='test')
    def rigthPanel_in_templateListing(self,anchor):
        rgtTab = mc.tabLayout( p=anchor,innerMarginWidth=5, innerMarginHeight=5,h=self.canvasSize[1]-52)
        mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.button()
        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.button()
        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=rgtTab )
        mc.button()
        
        #######################################################################
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[1,'Infos'])
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[2,'Member list'])
        mc.tabLayout(rgtTab ,e=True,tabLabelIndex=[3,'Tools'])
    def templateListing(self):
        mc.columnLayout( adjustableColumn=True, rs=5 ,p=self.UI_TAB)
        mc.rowLayout( numberOfColumns=3, columnWidth2=(80,(self.canvasSize[0]-80-20)), adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        pathTxFld = mc.textField( 'data_dir_txFld',ed=False  )
        mc.setParent('..')
        mc.separator()
        listDock = mc.rowLayout( numberOfColumns=2, columnWidth2=(self.canvasSize[0]/5*2+12, 75 ), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] ,w=self.canvasSize[0])

        self.leftPanel_in_templateListing(listDock)
        #------------------------------------------------------------------------------------------------------------
        self.rigthPanel_in_templateListing(listDock)
        modulePath = ''.join(os.path.dirname(inspect.getfile(self.CompileTab)))
        mc.textField( pathTxFld,e=True,tx=modulePath)
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="CCW_Template Manager  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
 
        self.UI_TAB = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        bndList = self.tmpleLib.exposeZipTemplate()
        if len(bndList) == 0:
            self.CompileTab()
        else:
            self.templateListing()

        mc.showWindow( self.windowRef)
        mc.window( self.windowRef,e=True, widthHeight=(self.canvasSize[0],self.canvasSize[1]) )
class lib:
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