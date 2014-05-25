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
reload(dishCore)

author = 'cedric bazillou 2013'
version = 0.048

class UI:
    def __init__(self):
        self.windowRef ='CCW_bentoUI'
        self.canvasSize =[430,400]
        self.UI_TAB = ''
        self.ToDelete = []
        self.toresizeCtrl = ''
        self.toresizeCtrlB = ''
        self.modeMenu  = ''
        self.tmpleLib =  dishCore.IO()
        self.dishBuilder = dishBuilder.UI()
        self.dishManager  = dishManager.UI()
    def show(self):
        if mc.window(self.windowRef,q=True,ex=True) == True:
            mc.deleteUI(self.windowRef)
        mc.window(self.windowRef , title="CCW_Bento Tools  %s"%version,  widthHeight=(self.canvasSize[0],self.canvasSize[1]),rtf=True,s=False )
        FrameAnchor = mc.frameLayout(cll=False,lv=False,mw=5,w=self.canvasSize[0])
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='out',mw=2,mh=2  )

        self.modeMenu = mc.optionMenu( label='' ,w=self.canvasSize[0]+16,cc=self.showModUI )
        mc.menuItem( label='Manager' )
        mc.menuItem( label='Builder' )

        self.UI_TAB = mc.columnLayout(p=FrameAnchor,adjustableColumn=True)
        self.dishManager.widget(self.UI_TAB)

        mc.textField( 'copyrigth_txFld',ed=False ,tx=' AUTHOR : cedric BAZILLOU 2014      --       http://circecharacterworks.wordpress.com/ ',p= FrameAnchor )
        
        mc.showWindow( self.windowRef)
        mc.window( self.windowRef,e=True, widthHeight=(self.canvasSize[0],self.canvasSize[1]) )
    def showModUI(self,*args):
        dishMode = mc.optionMenu( self.modeMenu,q=True,sl=True)
        dishList = self.tmpleLib.exposeZipTemplate()
        
        childArray = mc.columnLayout( self.UI_TAB ,q=True,childArray=True) 
        if childArray is not None:
            for obj in childArray:
                mc.deleteUI(obj)

        if dishMode == 1:
            self.dishManager.widget(self.UI_TAB)
        else:
            self.dishBuilder.widget(self.UI_TAB)
