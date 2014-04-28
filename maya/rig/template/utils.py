import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect

def exposeElements():
    modulePath = os.path.dirname(inspect.getfile(merge))
    filelist= os.listdir(modulePath)
    modulelist = [ f for f in filelist if  f.endswith('.ma')  ]
    for k in range(len(modulelist)):
        modulelist[k] = os.path.join(modulePath,modulelist[k])
    return modulelist
def exposeBundles():
    modulePath = os.path.dirname(inspect.getfile(merge))
    dirlist= os.listdir(modulePath)
    filteredDirlist = []

    for dir in dirlist:
        if os.path.isdir(os.path.join(modulePath,dir)) == True:
            filteredDirlist.append(dir)

    print filteredDirlist
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