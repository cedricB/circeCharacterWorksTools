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

import dish.data as attrToFilter
import dish.builder as dishBuilder
import dish.manager as dishManager
import dish.core as dishCore

reload(attrToFilter)
reload(dishBuilder)
reload(dishManager)


'''
* ..Current Features


copyAEWindow
|Feature                          |Description  |
|:--------------------------------|:------------|
|Non-destructive                  | Every change you make is maintained in history; facilitating persistent undo/redo, traceable history of who did what and when, including incremental versioning with arbitrary metadata, like a changelog or description. All retrievable at any point in time. |
|Full disclosure                  | You may at any point in time browse to data at any hierarchical level using your native file-browser; read, write, modify, delete or debug malicious data with tools you know.    |
|Partial I/O                      | As a side-effect to its inherently simplistic design, reading and writing within large sets of data doesn't require reading everything into memory nor does it affect surrounding data; facilitating distributed collaborative editing. See [RFC13][] for more information.
|No limits on size nor complexity | Store millions of strings, booleans, matrices.. groups of matrices.. matrices of groups, strings, booleans and vectors. On consumer hardware, in a matter of megabytes, without compression. Then go ahead and store billions.
|Open specification, open source  | There are no mysteries about the inner-workings of the data that you write; you may write personal tools for debugging, graphical interfaces or extensions to the standard. The specifications are all laid out below and collaboration is welcome. (Want Open Metadata in Lua, Java, PHP or C++?)

'''
author = 'cedric bazillou 2013'
version = 0.045

class UI:
    def __init__(self):
        self.windowRef ='CCW_bentoUI'
        self.canvasSize =[430,400]
        self.UI_TAB = ''
        self.ToDelete = []
        self.toresizeCtrl = ''
        self.toresizeCtrlB = ''
        self.tmpleLib =  dishCore.IO()
        self.dishBuilder = dishBuilder.UI()
        self.dishManager  = dishManager.UI()
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="CCW_Bento Manager  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
 
        self.UI_TAB = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        dishList = self.tmpleLib.exposeZipTemplate()
        if len(dishList) == 0:
            self.dishBuilder.widget(self.UI_TAB)
        else:
            self.dishManager.widget(self.UI_TAB)

        mc.textField( 'copyrigth_txFld',ed=False ,tx=' AUTHOR : cedric BAZILLOU 2014      --       http://circecharacterworks.wordpress.com/ ',p=self.UI_TAB  )
        
        mc.showWindow( self.windowRef)
        mc.window( self.windowRef,e=True, widthHeight=(self.canvasSize[0],self.canvasSize[1]) )
