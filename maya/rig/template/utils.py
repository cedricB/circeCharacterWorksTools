import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile

author = 'cedric bazillou 2013'
version = 0.01

class UI:
    def __init__(self):
        self.windowRef ='CCW_templateUI'
        self.tmpleLib =  lib()
        self.canvasSize =[320,400]
        self.UI_TAB = ''
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="Slime dealer  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
 
        self.UI_TAB = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0])
        
        mc.button(l='Compile bundle',c=self.tmpleLib.compile_bundle)
        mc.showWindow( self.windowRef)
        mc.window( self.windowRef,e=True, widthHeight=(self.canvasSize[0],self.canvasSize[1]) )
class lib:
    def compile_bundle(self,*args):
        templateList = self.exposeBundles()
        if templateList is not None or len(templateList) > 0:
            for idx in range(len(templateList)):
                tmpleName = os.path.basename(os.path.dirname(templateList[idx]))
                tmpleDir = str(os.path.dirname(templateList[idx]))
                tmpleRoot = os.path.dirname(inspect.getfile(self.merge))
                tmpleRoot = r''.join(tmpleRoot)
            
                zipPath = os.path.join(tmpleRoot,tmpleName+'.zip')
                self.createBundle(tmpleDir,zipPath,tmpleRoot)
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