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
    
if 'attrToFilter' not in sys.modules.keys():
    import dish.data as attrToFilter
    reload(attrToFilter)

if 'dishCore' not in sys.modules.keys():
    import dish.core as dishCore    
    reload(dishCore)


author = 'cedric bazillou 2013'
version = 0.01



class UI:
    def __init__(self):
        self.outputScroll = ''
        self.outputAttributes =  ''
        self.outputFld  =  ''
        self.scrollInfo  = ''
        self.assetListing  = ''
        self.bentoRoot = ''
        self.tabCtrl_A = ''
        self.tabCtrl_B = ''
        self.driverFld =  ''
        self.driverScroll = ''
        self.DriverAttributes = ''
        self.canvasSize =[430,400]
        self.bundle_prgrss = ''
        self.bentoElements = 'CCW_TOOLS_bentoElem'
        self.foodField = ''
        self.IO =  dishCore.IO()
        self.factory = dishCore.factory()
        self.defaultNodes = attrToFilter.defaultNodes        
        excludeAttr = attrToFilter.excludeAttr
        
        filter =  attrToFilter.unExposeAttr
        excludeAttr.extend(filter) 
        excludeAttr.extend(attrToFilter.crveExclude)
        excludeAttr.extend(attrToFilter.meshExclude)
        excludeAttr.extend(attrToFilter.latExclude)
        excludeAttr.extend(attrToFilter.surfceExclude)
        
        self.exludedAttributes = excludeAttr 

    #---------------------------------------------------------------------------------------- widget Helpers 
    def resizeBuildTabs(self):
        tabIndex = mc.tabLayout(self.tabCtrl_A ,q=True,sti=True )
        if tabIndex == 1 :
             mc.tabLayout(self.tabCtrl_A,e=True,  h=620 )
        if tabIndex == 2 :
            mc.tabLayout(self.tabCtrl_A,e=True,  h=80 )
    #---------------------------------------------------------------------------------------- MAIN UI 
    def widget(self,widgetParent ):
        wd = mc.columnLayout(widgetParent,q=True,w=True)
        mc.columnLayout( adjustableColumn=True,p=widgetParent,w=wd )
        mc.separator()
        
        mc.rowLayout(   numberOfColumns=3, 
                    columnWidth2=(80,(self.canvasSize[0]-80-20)),
                    adjustableColumn=2,cl2=('left','both' )  )
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
    #-------------------------------------------------------------------------------------
    def defineDriver_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        defineDriver_form = mc.formLayout(numberOfDivisions=2)

        #---------------------------------------------------------------------------------------
        rowA = self.editDriverTab( defineDriver_form ) 
        rowB = self.manageDriverTab( defineDriver_form ) 

        mc.formLayout(defineDriver_form,e=True,attachForm=[ 
                            (rowA, 'top', 1),(rowA, 'bottom', 1),(rowA, 'left', 1),
                            (rowB, 'top', 1),(rowB, 'bottom', 1),(rowB, 'right', 1) ],
                            attachControl=[(rowB, 'left', 5, rowA)])
    def editDriverTab(self,anchor ):
        driverRow = mc.frameLayout( collapsable=False,labelVisible=False,  borderStyle='etchedIn', 
        mh=5,mw=5 ,w=self.canvasSize[0]/2-30,p=anchor )  
        mc.text(l=' 5-a. Driver Node :')
        mc.rowLayout( numberOfColumns=2,  adjustableColumn=1,cl2=('left','both' ) )
        self.driverFld = mc.textField( 'CCW_TOOLS_DRVER_txFld' )
        psdFileRootBtn = mc.button(l='<' ,w=20,h=20,c=self.collect_driver_data )        
        mc.setParent('..')
 
        self.DriverAttributes = mc.textScrollList( 'CCW_TOOLS_DriverAttributes',numberOfRows=8, allowMultiSelection=True)

        mc.setParent( driverRow )
        mc.separator()
        mc.button(l='5-b. Expose selection' , h=32,c=self.validate_driverData)

        return driverRow
    #-------------------------------------------------------------------------------------
    def defineOutput_UI(self  ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        defineDriver_form = mc.formLayout(numberOfDivisions=2)

        #---------------------------------------------------------------------------------------
        rowA = self.editOutput_UI( defineDriver_form ) 
        rowB = self.manageOutputTab( defineDriver_form ) 

        mc.formLayout(defineDriver_form,e=True,attachForm=[ 
                            (rowA, 'top', 1),(rowA, 'bottom', 1),(rowA, 'left', 1),
                            (rowB, 'top', 1),(rowB, 'bottom', 1),(rowB, 'right', 1) ],
                            attachControl=[(rowB, 'left', 5, rowA)])
    def editOutput_UI(self,anchor ):
        driverRow = mc.frameLayout( collapsable=False,labelVisible=False,  borderStyle='etchedIn', 
        mh=5,mw=5 ,w=self.canvasSize[0]/2-30,p=anchor )  
        mc.text(l=' 6-a. Output Node :')
        mc.rowLayout( numberOfColumns=2,  adjustableColumn=1,cl2=('left','both' ) )
        self.outputFld = mc.textField( 'CCW_TOOLS_output_txFld' )
        psdFileRootBtn = mc.button(l='<' ,w=20,h=20 ,c=self.collect_output_data )        
        mc.setParent('..')
 
        self.outputAttributes = mc.textScrollList( 'CCW_TOOLS_outputAttributes',numberOfRows=8, allowMultiSelection=True)

        mc.setParent( driverRow )
        mc.separator()
        mc.button(l='6-b. Expose selection' , h=32,c=self.validate_outputData )

        return driverRow
    def manageOutputTab(self,anchor  ):
        driverRow = mc.frameLayout( collapsable=False,labelVisible=False,  borderStyle='in',  mh=3,mw=5  ,p=anchor )
        mc.text(l='Published Output' )
        self.outputScroll = mc.scrollLayout( horizontalScrollBarThickness=0,verticalScrollBarThickness=8,childResizable=True )
        
        return driverRow
    #-------------------------------------------------------------------------------------
    def defineMisc_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        mc.button(l='Flag output' ,w=40)
    #---------------------------------------------------------------------------------------- editOutputTab UI Helpers
    def collect_output_data(self,*args):
        sel = mc.ls(sl=True,fl=True)
        root = mc.textField( self.outputFld ,q=True,tx=True)
        mc.textField( self.outputFld ,e=True,tx='')
        if sel is None or len(sel)<1  : 
            return 
        else:
            bentoRoot = mc.textField( self.bentoRoot,q=True,tx=True)
            erroChk = 0
            chkList = [bentoRoot ]
            feedBackList = ['Please pick a root object']
            for index, checkObj in enumerate(chkList): 
                if checkObj is None or len(checkObj)== 0:
                    erroChk += 1
                    mc.warning(feedBackList[index])
            if erroChk > 0:
                return 
            mc.textField( self.outputFld ,e=True,tx=sel[0])

            attributeList = list( set(mc.listAttr(sel[0] ))-set(self.exludedAttributes)) 
            print attributeList
            #
            
            mc.textScrollList( self.outputAttributes ,e=True,ra=True)
            if attributeList is not None:
                attributeList = sorted(attributeList)
                for attr in attributeList:
                    mc.textScrollList( self.outputAttributes ,e=True,a=attr)
    def validate_outputData(self,*args):
        attr = mc.textScrollList( self.outputAttributes ,q=True,si=True)
        root = mc.textField( self.outputFld ,q=True,tx=True)
        
        bentoRoot = mc.textField( self.bentoRoot,q=True,tx=True)
        erroChk = 0
        chkList = [bentoRoot ]
        feedBackList = ['Please pick a root object']
        for index, checkObj in enumerate(chkList): 
            if checkObj is None or len(checkObj)== 0:
                erroChk += 1
                mc.warning(feedBackList[index])
        if erroChk > 0:
            return 
        if attr is not None and len(root)>0:
            self.factory.publish_IO_Connections( bentoRoot,root+'.'+attr[0],1 ) 
            self.reset_outputUI()
            self.fill_outputUI( bentoRoot )
    def fill_outputUI(self,root ):
        inputData = self.factory.retrieve_IO_Connections(root, 1)

        if inputData is not None: 
            lenData = len(inputData.keys())
            keyList = sorted(inputData.keys())

            for k in range(lenData):
                writeData = inputData[keyList[k]]
                self.expose_output_unit(self.outputScroll,writeData,keyList[k],root)
    def expose_output_unit(self, anchor, writeData,index,root ):
        mc.frameLayout( collapsable=True,labelVisible=True,  borderStyle='out' ,l='driver%s'%index ,mw=2,mh=2 ,p=anchor )
        
        if writeData[5] == True:
            mc.textField(tx=writeData[0],ed=False ,font='boldLabelFont')
        else:
            mc.textField(tx=writeData[0],ed=False )
        mc.separator()
        mc.text(l='label')
        lblFld = mc.textField( ed=True )
        mc.connectControl( lblFld, writeData[3])
        
        mc.text(l='widgetID')
        wdgFld = mc.textField( ed=True )
        mc.connectControl( wdgFld, writeData[4] )
        mc.separator()
        rmBtn = mc.button(l='remove',c=partial(self.validate_output_deletion,root , index))
    def validate_output_deletion(self ,root , index, *args):
        self.factory.delete_Connections_at_targetIndex( root , index,1 )
        self.reset_outputUI()
        self.fill_outputUI( root)
    def reset_outputUI(self):
        childArray = mc.scrollLayout( self.outputScroll ,q=True,childArray=True) 
        if childArray is not None:
            for obj in childArray:
                mc.deleteUI(obj)
    #---------------------------------------------------------------------------------------- editDriverTab UI Helpers
    def collect_driver_data(self,*args):
        sel = mc.ls(sl=True,fl=True)
        root = mc.textField( self.driverFld ,q=True,tx=True)
        mc.textField( self.driverFld ,e=True,tx='')
        if sel is None or len(sel)<1  : 
            return 
        else:
            bentoRoot = mc.textField( self.bentoRoot,q=True,tx=True)
            erroChk = 0
            chkList = [bentoRoot ]
            feedBackList = ['Please pick a root object']
            for index, checkObj in enumerate(chkList): 
                if checkObj is None or len(checkObj)== 0:
                    erroChk += 1
                    mc.warning(feedBackList[index])
            if erroChk > 0:
                return 
            mc.textField( self.driverFld ,e=True,tx=sel[0])

            attributeList = list( set(mc.listAttr(sel[0] ))-set(self.exludedAttributes)) 
            print attributeList
            #
            
            mc.textScrollList( self.DriverAttributes ,e=True,ra=True)
            if attributeList is not None:
                attributeList = sorted(attributeList)
                for attr in attributeList:
                    mc.textScrollList( self.DriverAttributes ,e=True,a=attr)
    def validate_driverData(self,*args):
        attr = mc.textScrollList( self.DriverAttributes ,q=True,si=True)
        root = mc.textField( self.driverFld ,q=True,tx=True)
        
        bentoRoot = mc.textField( self.bentoRoot,q=True,tx=True)
        erroChk = 0
        chkList = [bentoRoot ]
        feedBackList = ['Please pick a root object']
        for index, checkObj in enumerate(chkList): 
            if checkObj is None or len(checkObj)== 0:
                erroChk += 1
                mc.warning(feedBackList[index])
        if erroChk > 0:
            return 
        if attr is not None and len(root)>0:
            self.factory.publish_IO_Connections( bentoRoot,root+'.'+attr[0],0 ) 
            self.reset_driverUI()
            self.fill_driverUI( bentoRoot )
    def manageDriverTab(self,anchor  ):
        driverRow = mc.frameLayout( collapsable=False,labelVisible=False,  borderStyle='in',  mh=3,mw=5  ,p=anchor )
        mc.text(l='Published Drivers' )
        self.driverScroll = mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8,childResizable=True )
        
        return driverRow
    def expose_driver_unit(self, anchor, writeData,index,root ):
        mc.frameLayout( collapsable=True,labelVisible=True,  borderStyle='out' ,l='driver%s'%index ,mw=2,mh=2 ,p=anchor )
        
        if writeData[5] == True:
            mc.textField(tx=writeData[0],ed=False ,font='boldLabelFont')
        else:
            mc.textField(tx=writeData[0],ed=False )
        mc.separator()
        mc.text(l='label')
        lblFld = mc.textField( ed=True )
        mc.connectControl( lblFld, writeData[3])
        
        mc.text(l='widgetID')
        wdgFld = mc.textField( ed=True )
        mc.connectControl( wdgFld, writeData[4] )
        mc.separator()
        rmBtn = mc.button(l='remove',c=partial(self.validate_driver_deletion,root , index))
    def reset_driverUI(self):
        childArray = mc.scrollLayout( self.driverScroll ,q=True,childArray=True) 
        if childArray is not None:
            for obj in childArray:
                mc.deleteUI(obj)
    def fill_driverUI(self,root ):
        inputData = self.factory.retrieve_IO_Connections(root, 0)

        if inputData is not None: 
            lenData = len(inputData.keys())
            keyList = sorted(inputData.keys())

            for k in range(lenData):
                writeData = inputData[keyList[k]]

                self.expose_driver_unit(self.driverScroll,writeData,keyList[k],root)
    def validate_driver_deletion(self ,root , index, *args):
        self.factory.delete_Connections_at_targetIndex( root , index,0 )
        self.reset_driverUI()
        self.fill_driverUI( root)
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
        mc.textField( self.foodField,e=True,tx='')  
        mc.scrollField(self.scrollInfo ,e=True,tx='') 

        mc.textScrollList( self.DriverAttributes ,e=True,ra=True) 
        mc.textField( self.driverFld,e=True,tx='')  

        mc.textScrollList( self.outputAttributes ,e=True,ra=True) 
        mc.textField( self.outputFld,e=True,tx='')     
        
        mc.textScrollList(  self.assetListing,e=True,ra=True) 
        self.reset_driverUI()
        self.reset_outputUI()

        if sel is None or len(sel)<1  :      
            return 
        else:
            self.fill_driverUI(sel[0])
            self.fill_outputUI(sel[0])

            UI_Dict = {}
            UI_Dict['moduleInfos']  = [ self.scrollInfo, 1]
            UI_Dict['foodType']     = [ self.foodField, 0]
            UI_Dict['element']     = [ self.assetListing, 2]
            
            dataList = self.factory.read_dish_data(sel[0])

            for key in dataList.keys():
                if  dataList[key] is not '':
                    if UI_Dict[key][1] == 0:
                        mc.textField( UI_Dict[key][0],e=True,tx=dataList[key])
                    if UI_Dict[key][1] == 1:
                        mc.scrollField( UI_Dict[key][0] ,e=True,tx=dataList[key])
                    if UI_Dict[key][1] == 2:
                        for elem in dataList[key]:
                            mc.textScrollList( UI_Dict[key][0] ,e=True,a=elem)
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
        self.defineOutput_UI()
        self.defineMisc_UI()

        # publish Elements
        mc.setParent(buildDish_UI_Anchor)
        mc.separator()
        mc.button(l='Release bento',h=45,c=self.validateDishBeforePublish)
        
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[1,'4. Flag Elements'])
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[2,'5. Expose Drivers'])
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[3,'6. Expose Outputs'])
        mc.tabLayout(self.tabCtrl_B ,e=True,tabLabelIndex=[4,'7. Misc.'])
    #---------------------------------------------------------------------------------------- deliverTab UI Helpers
    def validate_compile(self ,*args):
        self.IO.compile_bundle()
        # Tool().show()
    #---------------------------------------------------------------------------------------- deliver TAB
    def deliverTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.tabCtrl_A)
        mc.button(l='Compile bundle',c=self.validate_compile)
        self.bundle_prgrss = mc.progressBar('CCW_TOOLS_bundle_prgrss')
