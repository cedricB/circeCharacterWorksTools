import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect

def hook():
    pass
def exposeElements():
    modulePath = os.path.dirname(inspect.getfile(hook))
    filelist= os.listdir(modulePath)
    modulelist = [ f for f in filelist if  f.endswith('.ma')  ]
    for k in range(len(modulelist)):
        modulelist[k] = os.path.join(modulePath,modulelist[k])
    return modulelist
def merge(sourcePath,prfxToReplace,newModuleName):
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