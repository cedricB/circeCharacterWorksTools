import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile
from functools import partial
import json
import uuid


'''
* ..change is common
* ..space is cheap
* ..control outweighs performance

copyAEWindow
|Feature                          |Description  |
|:--------------------------------|:------------|
|Non-destructive                  | Every change you make is maintained in history; facilitating persistent undo/redo, traceable history of who did what and when, including incremental versioning with arbitrary metadata, like a changelog or description. All retrievable at any point in time. |
|Full disclosure                  | You may at any point in time browse to data at any hierarchical level using your native file-browser; read, write, modify, delete or debug malicious data with tools you know.    |
|Partial I/O                      | As a side-effect to its inherently simplistic design, reading and writing within large sets of data doesn't require reading everything into memory nor does it affect surrounding data; facilitating distributed collaborative editing. See [RFC13][] for more information.
|No limits on size nor complexity | Store millions of strings, booleans, matrices.. groups of matrices.. matrices of groups, strings, booleans and vectors. On consumer hardware, in a matter of megabytes, without compression. Then go ahead and store billions.
|Open specification, open source  | There are no mysteries about the inner-workings of the data that you write; you may write personal tools for debugging, graphical interfaces or extensions to the standard. The specifications are all laid out below and collaboration is welcome. (Want Open Metadata in Lua, Java, PHP or C++?)
reglisse
brownie

15 juin
### 

'''
author = 'cedric bazillou 2013'
version = 0.043


class dishBuilder:
    def __init__(self):
        #sys.path.append(modulePath)
        if 'dish.dishData' not in sys.modules.keys():
            modulePath = os.path.dirname(inspect.getfile(self.resizeBuildTabs))
            modulePath = os.path.dirname(modulePath)
            sys.path.append(modulePath)
        import dish.dishData as attrToFilter
        reload(attrToFilter)

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
        self.IO =  IO()
        self.factory = factory()
        self.defaultNodes = attrToFilter.defaultNodes        
        excludeAttr = attrToFilter.excludeAttr
        
        filter =  attrToFilter.unExposeAttr
        excludeAttr.extend(filter) 
        excludeAttr.extend(attrToFilter.crveExclude)
        excludeAttr.extend(attrToFilter.meshExclude)
        excludeAttr.extend(attrToFilter.latExclude)
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
        defineDriver_form = mc.formLayout(numberOfDivisions=2)

        #---------------------------------------------------------------------------------------
        rowA = self.editDriverTab( defineDriver_form ) 
        rowB = self.manageDriverTab( defineDriver_form ) 

        mc.formLayout(defineDriver_form,e=True,attachForm=[ 
                            (rowA, 'top', 1),(rowA, 'bottom', 1),(rowA, 'left', 1),
                            (rowB, 'top', 1),(rowB, 'bottom', 1),(rowB, 'right', 1) ],
                            attachControl=[(rowB, 'left', 5, rowA)])
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
    def defineOutput_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        mc.button(l='Flag output' ,w=40)
    def defineMisc_UI(self ):
        mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5 ,p=self.tabCtrl_B)
        mc.button(l='Flag output' ,w=40)
    #---------------------------------------------------------------------------------------- editDriverTab UI Helpers
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
    def expose_driver_unit(self, anchor, driverLabel,index,root ):
        mc.frameLayout( collapsable=False,labelVisible=True,  borderStyle='out' ,l='driver%s'%index ,mw=2,mh=2 ,p=anchor )
        mc.textField(tx=driverLabel,ed=False )
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
        mc.textScrollList(  self.assetListing,e=True,ra=True) 
        self.reset_driverUI()

        if sel is None or len(sel)<1  :      
            return 
        else:
            inputData = self.factory.retrieve_IO_Connections(sel[0], 0)
            self.fill_driverUI(sel[0])
            
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
    
    #---------------------------------------------------------------------------------------- deliver TAB
    def deliverTab(self):
        mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0],p=self.tabCtrl_A)
        mc.button(l='Compile bundle',c=self.IO.compile_bundle)
        self.bundle_prgrss = mc.progressBar('CCW_TOOLS_bundle_prgrss')
class dishEditor:
    def __init__(self):
        self.module=''
        self.canvasSize =[430,400]
        self.IO =  IO()
        self.InfosTab       =  ''
        self.bentoElements  =  ''
        self.gourmetTab     =  ''
        self.dishPrfx       =  ''
        self.pathTxFld      =  ''
        self.dishType       =  ''
        self.dishTabTool    =  ''
        self.factory = factory()
    def widget(self,widgetParent):
        mc.columnLayout( adjustableColumn=True, rs=5 ,p=widgetParent)
        mc.rowLayout(   numberOfColumns=3, 
                        columnWidth2=(80,(self.canvasSize[0]-80-20)),
                        adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        self.pathTxFld  = mc.textField( 'buildEditor_UI_data_dir_txFld',ed=False  )
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
        mc.textField( self.pathTxFld ,e=True,tx=modulePath)
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
            mc.button(btn,e=True,c=partial( self.switch_module, dishName ,dish ))
    def switch_module(self,dishName,dishFile,*args):
        archive = zipfile.ZipFile(dishFile, 'r')
        jsonFile = archive.read('dish.ini')
        jsondata = json.loads(jsonFile)  
        archive.close()

        #Clear chld
        chldrn = mc.layout( self.InfosTab, query=True, childArray=True )
        for chld in chldrn:
            mc.deleteUI(chld)
        #-------------------------------------------------------------------
        mc.columnLayout( adjustableColumn=True ,p=self.InfosTab ,rs=5)        
        header = """<html>
            <body>
            <h1>%s</h1></body>
            </html>
        """%(dishName )
        
        self.dishType  = dishName
        mc.text( self.module,e=True,l=header,font='boldLabelFont')        
        mc.scrollField( editable=False, wordWrap=True, text=jsondata['moduleInfos'] ,h=120)
        mc.separator()   
        LimbMenu = mc.optionMenu( label='Limb type          ' )
        mc.menuItem( label='arm                              ' )
        mc.menuItem( label='leg                              ' )
        mc.menuItem( label='spine                            ' )
        mc.menuItem( label='head                             ' )
        mc.menuItem( label='neck                             ' )
        mc.menuItem( label='foot                             ' )
        mc.menuItem( label='hand                             ' )
        mc.optionMenu( LimbMenu ,e=True,changeCommand=partial(self.composePrfX,LimbMenu))

        
        ArticulationMenu =mc.optionMenu( label='Articulation       ' )    
        mc.menuItem( label='shoulder                        ' )            
        mc.menuItem( label='wrist                           ' )
        mc.menuItem( label='elbow                           ' )
        mc.menuItem( label='finger                          ' )
        mc.menuItem( label='knee                            ' )
        mc.menuItem( label='ankle                           ' )
        mc.optionMenu( ArticulationMenu ,e=True,changeCommand=partial(self.composePrfX,ArticulationMenu))
        
        SideMenu = mc.optionMenu( label='Side                  ' )    
        mc.menuItem( label='left              *l*            ' )            
        mc.menuItem( label='right             *r*            ' )
        mc.menuItem( label='center            *c*            ' )
        mc.optionMenu( SideMenu ,e=True,changeCommand=partial(self.composePrfX,SideMenu))

        self.dishPrfx       =  mc.textField()
        mc.button(l='Import', h=42,c=self.validate_dish_before_merge )        
        
        mc.textScrollList( self.bentoElements , e=True,ra=True)
        self.refresh_dishTabs_contents()
    def validate_dish_before_merge(self,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        if len(prx)>1:
            path = mc.textField( self.pathTxFld, q=True,tx=True)
            dishFile = os.path.join( path,self.dishType+'.zip')
            self.IO.merge( dishFile,'XX_',prx+'_')
    def composePrfX (self,menuOpt ,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        module = mc.optionMenu(menuOpt,q=True,value=True).strip()
        if len(prx)<1:
            if '*' in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=module)
        else:
            if '*'  in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=prx+'_'+module )
    def bentosFactory_UI(self,anchor):
        mc.columnLayout( adjustableColumn=True,p=anchor )
        self.module= mc.text( 'CCW_TOOLS_DISHNAME_txFld', l='', h=36  )
        self.dishTabTool = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5,h=self.canvasSize[1]-84)
        self.InfosTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.text(l='')

        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.text(l='')
        
        #--------------------------------------------------------
        self.gourmetTab = mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.columnLayout( adjustableColumn=True )
        self.bentoElements =  mc.textScrollList( 'CCW_TOOLS_bentoElements',numberOfRows=18, selectCommand=self.select_installedDish )
        
        
        
        #######################################################################
        
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[1,'Infos'])
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[2,'Tools'])
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[3,'Gourmet Manager'])

        dishList = self.IO.exposeZipTemplate()
        self.switch_module( os.path.basename(dishList[0]).split('.zip')[0],dishList[0] )         
        mc.tabLayout(self.dishTabTool ,e=True,changeCommand=self.refresh_dishTabs_contents)
    def select_installedDish(self,*args):
        dish = mc.textScrollList( 'CCW_TOOLS_bentoElements',q=True,selectItem=True)
        mc.select(dish,r=True)
    def refresh_dishTabs_contents(self,*args):
        currentTab = mc.tabLayout(self.dishTabTool ,q=True,selectTabIndex=True)
        if currentTab == 3:
            dishList = self.factory.collect_similar_dish(self.dishType)
            mc.textScrollList( self.bentoElements ,e=True,ra=True)
            if len(dishList)>0:
                for dish in dishList:
                    mc.textScrollList( self.bentoElements ,e=True,a=dish)
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
        ## ------------------------------- then name elements properly
        scrpDir = mc.internalVar(userScriptDir=True)
        localModuleToMerge = os.path.join(scrpDir,newModuleName+'.01.ma')
        archive = zipfile.ZipFile(sourcePath, 'r')
        jsonFile = archive.open('data.ma')
        
        outputFile =  open(localModuleToMerge, "w") 
       
        for line in jsonFile:
            if prfxToReplace in line:
                nwLn = line.replace(prfxToReplace,newModuleName)
                outputFile.writelines( nwLn)
            else:
                outputFile.writelines(line)
        archive.close()   
        outputFile.close()
        ## ------------------------------- inject it in your scene
        mc.file(localModuleToMerge,i=True)
        mc.sysFile(localModuleToMerge,delete=True)  
        
        #now list new imported module
        content = mc.ls(type='transform')
        attributeList = ['foodType','uuID']
        nwNode = []
        for obj in content:
            idx = 0
            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=obj,ex=True) == True:
                    idx += 1
            if idx > 1:
                nwNode.append(obj)
        mc.setAttr(nwNode[0] +'.uuID',l=False)
        mc.deleteAttr(nwNode[0] +'.uuID')
        
        foodTpe = mc.getAttr(nwNode[0] +'.foodType')
        OpenMaya.MGlobal.displayInfo( '**The %s dish  %s was successfully merge in your scene'% (foodTpe, newModuleName) )
        return nwNode[0]
    def clean_asset_file():
        pass
class factory:
    def expose_members(self ,
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
            flagKey = str(uuid.uuid4().hex)
            attributeList = ['foodType','moduleInfos','uuID']
            dataList = [foodType,moduleInfos,flagKey]
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
    def collect_similar_dish(self,expextedFood):
        content = mc.ls(type='transform')
        attributeList = ['foodType' ]
        nwNode = []
        for obj in content:
            idx = 0
            for index, attr in enumerate(attributeList):
                if mc.attributeQuery(attributeList[index],node=obj,ex=True) == True:
                    if mc.getAttr(obj+'.'+attributeList[index]) == expextedFood  :
                        idx = 2
            if idx > 1:
                nwNode.append(obj)
        return nwNode
    def read_dish_data(self , root):
        attributeList = ['foodType','moduleInfos' ]
        dataList = {}
        for  attr in  attributeList :
            dataList[attr] = ''
            if mc.attributeQuery(attr,node=root,ex=True) == True:
                dataList[attr] = mc.getAttr('%s.%s'%(root,attr))
        
        dataList['element'] = ''
        if mc.attributeQuery('element',node=root,ex=True) == True:
            cntList = mc.listConnections('%s.%s'%(root,'element'),sh=True)
            if cntList is not None and len(cntList)>0:
                dataList['element'] = []
                dataList['element'].extend(cntList)
        return dataList
    def retrieve_IO_Connections(self,root, IO_Index ):
        attributeList = ['foodType','moduleInfos','uuID']
        chkErrr = 0
        for index, attr in enumerate(attributeList):
            if mc.attributeQuery(attributeList[index],node=root,ex=True) == False:
                chkErrr += 1

        if chkErrr > 0:
            return None
        attributeList = ['inputStorage', 'outputStorage']
        cnList = ['input', 'output']    
        for  attr in  attributeList :
            if mc.attributeQuery(attr,node=root,ex=True) == False:
                storage = mc.createNode('choice',n=''.join((root,'_',attr,'1')))
                mc.addAttr(root,ln=attr,k=False,h=True)
                mc.connectAttr(storage+'.nodeState' ,root+'.'+attr ,f=True)
                
        dataList = {} 
        storage = mc.listConnections(root+'.'+attributeList[IO_Index])[0]
        idxList = mc.getAttr(storage+'.'+cnList[IO_Index],mi=True)
        if idxList is None:
            return None
            
        for index, value in enumerate(idxList):
            driverAttr = mc.connectionInfo(storage+'.'+cnList[IO_Index]+'[%s]'%value,sfd=True)
            dataList[index] = driverAttr
        
        
        return dataList
    def publish_IO_Connections(self,root,targetAttribute,IO_Index ):
        if mc.objExists(targetAttribute) == False :
            return

        attributeList = ['inputStorage', 'outputStorage']   
        cnList = ['input', 'output']          
        storage = mc.listConnections(root+'.'+attributeList[IO_Index])[0]  
   
        idxList = mc.getAttr(storage+'.'+cnList[IO_Index],mi=True)
        idx = 0
        if idxList is None:
            idxList = [0]
            mc.connectAttr( targetAttribute, storage + '.input[%s]'%0,f=True)
        else:
            idx = idxList[-1]+1
            mc.connectAttr( targetAttribute, storage + '.input[%s]'%idx,f=True)
    def delete_Connections_at_targetIndex(self,root,targetIndex,IO_Index ):
        attributeList = ['inputStorage', 'outputStorage']   
        cnList = ['input', 'output']          
        storage = mc.listConnections(root+'.'+attributeList[IO_Index])[0]  
   
        idxList = mc.getAttr(storage+'.'+cnList[IO_Index],mi=True)
        idx = 0
        if idxList is None:
            return
        else:
            targetIndex = idxList[targetIndex]
            if targetIndex in idxList :
                mc.removeMultiInstance(storage+'.'+cnList[IO_Index]+'[%s]'%targetIndex,b=True)
