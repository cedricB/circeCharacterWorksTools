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

if 'dishCore' not in sys.modules.keys():
    import dish.core as dishCore    
    reload(dishCore)


author = 'cedric bazillou 2013'
version = 0.02

class dishComponent:
    def __init__(self):
        self.canvasSize =[430,400]
    def expose_list(self,tabAnchor,rootData):
        samplingConnections     = rootData[0]
        caption                 = rootData[1]
        mc.textField(  tx=caption,ed=False ,p=tabAnchor , font="boldLabelFont",bgc=[0.8,0.8,0.8])
        mc.optionMenu( label=' Options: ' ,p=tabAnchor , w=432  -30)
        mc.menuItem( label='select' )
        mc.menuItem( label='connect' )
        mc.menuItem( label='swap' )
        mc.menuItem( label='constraint' )
        mc.menuItem( label='Manage Input' )
        scrollWdth = mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8, p=tabAnchor ,h=150,childResizable=True )

        inputIdxList = mc.getAttr(samplingConnections,mi=True )
        ctrlHgt = 24
        for idx  in inputIdxList:
            input = mc.listConnections(samplingConnections+'[%s]'%idx)
            
            if input is not None and len(input)>0:
                input = input[0]
            else:
                input = samplingConnections+'[%s]'%idx

            mc.separator(style='none', p=scrollWdth,h=6 )
            mc.flowLayout( columnSpacing=4  , p=scrollWdth )
            fldLnk = mc.textField(  tx=input,ed=False ,w=395 -30,h=ctrlHgt)
            mc.popupMenu( button=3 ,p=fldLnk)
            mc.menuItem(l='moveUP' )
            mc.menuItem(l='moveDown' )
            mc.menuItem(l='Delete' )
            mc.button( label='<')
    def expose_component(self,tabAnchor,rootData):
        attrib_link = rootData[0]
        ctrlHgt = 24
        nodeData = attrib_link.split('.') 
        typeChk = mc.attributeQuery(  nodeData[-1], node=nodeData[0], attributeType=True  )
        numericType = ['float','double','short','long','int','bool','enum','string']
        clm = mc.columnLayout( adjustableColumn=True, rs=5 ,p=tabAnchor, w=420 -30 )
        
        stringType = mc.getAttr(attrib_link,type=True)
        fildCaption = mc.textField(  tx=rootData[1],ed=False,w=410 -30 ,p=clm , font="boldLabelFont",bgc=[0.8,0.8,0.8])    
        mc.popupMenu( button=3 ,p=fildCaption)
        mc.menuItem(l='Open in connection Editor' )


        if stringType == 'string':  
            attrFld = mc.textField(  ed=True,w=410 -30 ,p=clm )              
            mc.connectControl( attrFld, attrib_link )

        else:
            if typeChk in numericType:
                mc.attrFieldSliderGrp( attribute=rootData[0],p=clm )
            else:        
                flw = mc.flowLayout( columnSpacing=4  , p=clm )
                fldLnk = mc.textField(  tx=rootData[0],ed=False ,w=385,h=ctrlHgt,p=flw)
                mc.button( label='<',p=flw)
class UI:
    def __init__(self):
        self.module=''
        self.canvasSize =[430,400]
        self.InfosTab       =  ''
        self.bentoElements  =  ''
        self.gourmetTab     =  ''
        self.dishPrfx       =  ''
        self.pathTxFld      =  ''
        self.dishType       =  ''
        self.dishTabTool    =  ''
        self.editTool       =  ''
        self.ImportTab      =  ''
        self.EditTab        =  ''
        self.FindTab        =  ''
        self.swtTab         =  ''
        self.IO             = dishCore.IO()
        self.factory        = dishCore.factory()
        self.dishComponent  = dishComponent()
        self.dishInputsComponents = ''
        self.dishOutputsComponents = ''
        self.currentEditedDish = ''
        self.IO_TAB         = ''    
    def widget(self,widgetParent):
        hook = mc.columnLayout( adjustableColumn=True, rs=5 ,p=widgetParent)
        mc.separator()
        mc.rowLayout(   numberOfColumns=3, 
                        columnWidth2=(80,(self.canvasSize[0]-80-20)),
                        adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        self.pathTxFld  = mc.textField( 'buildEditor_UI_data_dir_txFld',ed=False  )
        mc.setParent('..')
        mc.separator()

        self.swtTab = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5 )
        self.ImportTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5 ,p=self.swtTab)

        self.EditTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5 ,p=self.swtTab)

        mc.columnLayout( adjustableColumn=True)
        mc.frameLayout( borderStyle='etchedIn',collapsable=False,labelVisible=False,mw= 3 ,mh=3)
        mc.rowLayout( h=26,numberOfColumns=3, columnWidth3=(80,(self.canvasSize[0]-80-20),20), adjustableColumn=2,cl3=('left','both','right'))
        mc.text(l=' Current Dish :')
        self.currentEditedDish = mc.textField( )       
        rRootBtnC = mc.button(l='<' ,c=self.expose_dish_root)
        
        self.IO_TAB         =  mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5,p=self.EditTab )
        mc.frameLayout( borderStyle='etchedIn',collapsable=False,labelVisible=False,mw= 5 ,mh=5,p=self.IO_TAB  )
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8,  h=200,childResizable=True )
        self.dishInputsComponents = mc.columnLayout( adjustableColumn=True,rs=3)
        
        mc.frameLayout( borderStyle='etchedIn',collapsable=False,labelVisible=False,mw= 5 ,mh=5,p=self.IO_TAB  )
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8,  h=200,childResizable=True)
        self.dishOutputsComponents = mc.columnLayout( adjustableColumn=True,rs=3)
        
        mc.tabLayout(self.IO_TAB ,e=True,tabLabelIndex=[1,'Inputs'])
        mc.tabLayout(self.IO_TAB ,e=True,tabLabelIndex=[2,'Outputs'])

        self.FindTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5 ,p=self.swtTab)
        self.createGourmetTab()
        mc.textScrollList( self.bentoElements , e=True,ra=True)
        
        mc.tabLayout(self.swtTab ,e=True,tabLabelIndex=[1,'Import'])
        mc.tabLayout(self.swtTab ,e=True,tabLabelIndex=[2,'Edit'])
        mc.tabLayout(self.swtTab ,e=True,tabLabelIndex=[3,'Find'])
        
        mc.tabLayout(self.swtTab,e=True,changeCommand=self.refresh_dishTabs_contents)

        anchorDock = mc.rowLayout(    numberOfColumns=2,
                                    columnWidth2=(self.canvasSize[0]/5*2+12, 75 ),
                                    adjustableColumn=2,
                                    columnAlign=(1, 'right'),
                                    columnAttach=[(1,'both',0), (2,'both',0)] ,w=self.canvasSize[0],p=self.ImportTab)

        self.exposedBentos_UI(anchorDock)
        #------------------------------------------------------------------------------------------------------------
        self.bentosFactory_UI(anchorDock)

        modulePath = ''.join(os.path.dirname(inspect.getfile(self.exposedBentos_UI)))
        mc.textField( self.pathTxFld ,e=True,tx=modulePath)
    def cleanUP_editDishTAB(self,anchor):
        mc.textField( self.currentEditedDish ,e=True,tx='' )
        chldList = mc.layout(anchor,q=True,ca=True)
        
        if chldList is not None and len(chldList)>0:
            for chld in chldList:
                mc.deleteUI(chld)
    def expose_dish_root(self,*args):
        root = mc.ls(sl=True,fl=True)
        self.cleanUP_editDishTAB(self.dishInputsComponents)
        self.cleanUP_editDishTAB(self.dishOutputsComponents)
        if root is not None and len(root)>0:
            root = root[0]
            rootData = self.factory.retrieve_IO_Connections(  root,0 )            
            
            #fILL INPUTS
            if rootData is None:
                self.cleanUP_editDishTAB(self.dishInputsComponents)
                self.cleanUP_editDishTAB(self.dishOutputsComponents)
                return
            else:
                mc.textField( self.currentEditedDish ,e=True,tx=root )
                for key in rootData.keys():
                    componentIsList =  rootData[key][-1]
                    if componentIsList == True:
                        self.dishComponent.expose_list(self.dishInputsComponents,rootData[key] )
                    else:
                        self.dishComponent.expose_component(self.dishInputsComponents,rootData[key])
            #fILL OUTPUTS
            rootData = self.factory.retrieve_IO_Connections(  root,1)       
            if rootData is None:
                self.cleanUP_editDishTAB(self.dishInputsComponents)
                self.cleanUP_editDishTAB(self.dishOutputsComponents)
                return
            else:
                mc.textField( self.currentEditedDish ,e=True,tx=root )
                for key in rootData.keys():
                    componentIsList =  rootData[key][-1]
                    if componentIsList == True:
                        self.dishComponent.expose_list(self.dishOutputsComponents,rootData[key] )
                    else:
                        self.dishComponent.expose_component(self.dishOutputsComponents,rootData[key])
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
        mc.scrollField( editable=False, wordWrap=True, text=jsondata['moduleInfos'] ,h=140)
        mc.separator()   
        mc.text( l='name bank') 
        mc.columnLayout( adjustableColumn=True)
        LimbMenu = mc.optionMenu( label='',w=224  )
        mc.menuItem( label='NONE')
        mc.setParent('..')
        mc.button(l='Open name composer',h=28)
        mc.optionMenu( LimbMenu ,e=True,changeCommand=partial(self.composePrfX,LimbMenu))

        self.dishPrfx       =  mc.textField()
        mc.button(l='Import', h=42,c=self.validate_dish_before_merge )        
    def validate_dish_before_merge(self,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        if len(prx)>1:
            path = mc.textField( self.pathTxFld, q=True,tx=True)
            dishFile = os.path.join( path,self.dishType+'.zip')
            self.IO.merge( dishFile,'XX_',prx+'_')
    def composePrfX (self,menuOpt ,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        module = mc.optionMenu(menuOpt,q=True,value=True).strip()
        if module == 'NONE':
            return
        if len(prx)<1:
            if '*' in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=module)
        else:
            if '*'  in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=prx+'_'+module )
    def bentosFactory_UI(self,anchor):
        self.dishTabTool = mc.columnLayout( adjustableColumn=True,p=anchor )
        self.module= mc.text( 'CCW_TOOLS_DISHNAME_txFld', l='', h=36  )
        self.InfosTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.text(l='')
        dishList = self.IO.exposeZipTemplate()
        if dishList is not None and len(dishList)>0:
            self.switch_module( os.path.basename(dishList[0]).split('.zip')[0],dishList[0] )         
    def createGourmetTab( self ):
        self.gourmetTab = mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=self.FindTab)
        mc.columnLayout( adjustableColumn=True )
        self.bentoElements =  mc.textScrollList( 'CCW_TOOLS_bentoElements',numberOfRows=22, selectCommand=self.select_installedDish )
    def select_installedDish(self,*args):
        dish = mc.textScrollList( 'CCW_TOOLS_bentoElements',q=True,selectItem=True)
        mc.select(dish,r=True)
    def refresh_dishTabs_contents(self,*args):
        currentTab = mc.tabLayout(self.swtTab ,q=True,selectTabIndex=True)

        if currentTab == 3:
            mc.textScrollList( self.bentoElements ,e=True,ra=True)     
            globalDishList = self.IO.exposeZipTemplate()
            dishes = []
            for dish in globalDishList:
                dishName = os.path.basename(dish).split('.zip')[0]
                dishes.append(dishName)
       
            for dishModule in dishes:
                dishList = self.factory.collect_similar_dish(dishModule)#self.dishType
                if len(dishList)>0:
                    for dish in dishList:
                        mc.textScrollList( self.bentoElements ,e=True,a=dish)
