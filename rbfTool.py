"""
    General descrition of your module here.
"""
from functools import partial

from maya import OpenMaya
from maya import OpenMayaUI
from maya import cmds


from PySide import QtCore 
from PySide import QtGui 
from shiboken import wrapInstance
from shiboken import getCppPointer


class RbfSettings(object):
    """
        Class for storing rbf network creation options.
    """
    def __init__(self):
        self.connectMatrix = False
        self.connectRgbValues = False
        self.connectAlphaValues = False
        self.useAttributeAlias = False
        self.visualizeFalloff = False


class RbfManager(object):
    """
        Pose driver mixing contribution of various elements in n spaces.
    """
    def __init__(self):
        self.pluginState = self.initPlugins()

    def createNetwork(self, inputRbfSettings):
        if self.pluginState is False:
            return

    def vizualizeSigma(self):
        pass

    def createSigmaShader(self):
        pass

    def initPlugins(self):
        try:
            #you dont seem to use the class elements nor Api related encapsulation
            #of pymel so basically you can stick to maya python commands?
            cmds.loadPlugin('jsRadial.mll')
        except:
            cmds.error('ERROR: jsRadial.mll not loaded.')


class RbfOptionsWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RbfOptionsWidget, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        #create widget
        self.connectMatrixCheckBox = QtGui.QCheckBox('Connect Matrix')
        self.connectRgbCheckBox = QtGui.QCheckBox('Connect RGB Values from Material')
        self.connectAlphaCheckBox = QtGui.QCheckBox('Connect Alpha Values from Material')
        self.useAliasCheckBox = QtGui.QCheckBox('Use Aliases for Targets on RBF Node')

        sphereLabel = 'Create Spheres to Visualize Falloff  (most accurate for Gaussian)'
        self.createSphereCheckBox = QtGui.QCheckBox(sphereLabel)

        #Create layout
        self.mainLayout = QtGui.QVBoxLayout()

        #Set properties  
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
                
        for widget in [self.connectMatrixCheckBox,
                       self.connectRgbCheckBox,
                       self.connectAlphaCheckBox,
                       self.useAliasCheckBox,
                       self.createSphereCheckBox]:
            #Set properties  
            widget.setChecked(True)

            #Assign widget to layouts
            self.mainLayout.addWidget(widget)

        #set the main layout for this UI part
        self.setLayout(self.mainLayout)


class RbfListWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RbfListWidget, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        #create widget
        self.poseListWidget = QtGui.QListView()
        self.targetListWidget = QtGui.QListView()

        #Create layout
        self.poselistLayout = QtGui.QVBoxLayout()

        #Set properties
        self.poseListWidget.setMaximumHeight(20)
        self.poseListWidget.setMinimumWidth(190)
        self.targetListWidget.setMinimumHeight(260)

        self.poselistLayout.setContentsMargins(0, 0, 0, 0)
        self.poselistLayout.setSpacing(14)

        #Assign widget to layouts
        self.poselistLayout.addWidget(self.poseListWidget)
        self.poselistLayout.addWidget(self.targetListWidget)

        #set the main layout for this UI part
        self.setLayout(self.poselistLayout)


class RbfDataIoWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RbfDataIoWidget, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        #create widget
        self.anchorWidget = QtGui.QWidget()
        
        self.addPoseButton = QtGui.QPushButton('Add Pose')
        self.removePoseButton = QtGui.QPushButton('Remove Pose')

        self.addTargetButton= QtGui.QPushButton('Add Target')
        self.removeTargetButton = QtGui.QPushButton('Remove Target')

        #Create layout
        self.ioLayout = QtGui.QGridLayout()
        self.mainLayout = QtGui.QVBoxLayout()

        #Set properties
        ioWidth = 78
        self.ioLayout.setContentsMargins(0, 0, 0, 0)
        self.ioLayout.setColumnMinimumWidth(0, ioWidth)
        self.ioLayout.setColumnMinimumWidth(1, ioWidth)
        self.ioLayout.setSpacing(10)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        #Assign widget to layouts
        self.ioLayout.addWidget(self.removePoseButton, 0 , 0)
        self.ioLayout.addWidget(self.addPoseButton, 0 , 1)
        self.ioLayout.addWidget(self.removeTargetButton, 1 , 0)
        self.ioLayout.addWidget(self.addTargetButton, 1 , 1)

        self.mainLayout.addWidget(self.anchorWidget)
        self.mainLayout.addStretch()

        #set the main layout for this UI part
        self.anchorWidget.setLayout(self.ioLayout)
        self.setLayout(self.mainLayout)

        #Connect signals
        self.addPoseButton.clicked.connect(self._addPose)
        self.removePoseButton.clicked.connect(self._removePose)
        self.addTargetButton.clicked.connect(self._addTargets)
        self.removeTargetButton.clicked.connect(self._removeTargets)

    def _addPose(self):
        pass

    def _addTargets(self):
        pass

    def _removeTargets(self):
        pass

    def _removePose(self):
        pass


class RbfHeaderWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RbfHeaderWidget, self).__init__(parent)

        self.setupUI()

    def setupUI(self):
        #create widget
        self.headerLabel = QtGui.QLabel('RBF Network Builder')
        self.creditLabel = QtGui.QLabel('by James Sumner III')
        self.websiteLabel = QtGui.QLabel('www.jamessumneriii.com')

        #Create layout
        self.headerLayout = QtGui.QVBoxLayout()

        #Set properties
        self.headerLabel.setStyleSheet('font-size: 16pt' )
        self.creditLabel.setStyleSheet('color: rgb(140,140,140)')
        self.websiteLabel.setStyleSheet('color: rgb(140,140,140); link-decoration: none;')

        #Assign widget to layouts
        self.headerLayout.addWidget(self.headerLabel)
        self.headerLayout.addWidget(self.creditLabel)
        self.headerLayout.addWidget(self.websiteLabel)

        #set the main layout for this UI part
        self.setLayout(self.headerLayout)


class RbfManagerTool(QtGui.QDialog):
    """
        General UI used to create and maintain pose drivers.
    """
    def __init__(self, parent=None):
        super(RbfManagerTool, self).__init__(parent=parent)

        #Parent widget under Maya main window        
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)   

        self.toolName = 'RBF Tool'
        self.pose = []
        self.targets = []
        
        self.setupUI()

    def setupUI(self):
        #cmds.undoInfo(openChunk=True) will bundle a list of commands
        #which will modify the Dag or the dg hence the separation in the
        #API into 2 classes MDAGModifier / MDGModifier.
        #not sure about its usefulness for UI?

        #create widget
        self.tabWidget = QtGui.QTabWidget()
        self.headerWidget = RbfHeaderWidget()
        self.createTab = self._buildCreateTab() 

        #Create layout
        self.mainLayout = QtGui.QVBoxLayout()

        #Set properties
        self.setWindowTitle(self.toolName)

        self.mainLayout.setContentsMargins(10, 10, 10, 10)

        #Assign widget to layouts
        self.tabWidget.addTab(self.createTab, 'Create')
        #self.tabWidget.addTab(self.editTab, 'Edit')

        self.mainLayout.addWidget(self.headerWidget)
        self.mainLayout.addWidget(self.tabWidget)

        self.setLayout(self.mainLayout)

    def _buildCreateTab(self):
        #create widget
        self.createTabWidget = QtGui.QWidget()
        self.createTabAnchor = QtGui.QWidget()
        self.ioWidget = RbfDataIoWidget()
        self.poseListWidget = RbfListWidget()

        self.optionsWidget = RbfOptionsWidget()

        #Create layout
        self.createTabLayout = QtGui.QHBoxLayout()
        self.createTabOptionLayout = QtGui.QVBoxLayout()

        #Set properties
        self.createTabLayout.setContentsMargins(5, 5, 5, 5)
        self.createTabOptionLayout.setContentsMargins(0, 0, 0, 0)

        #Assign widget to layouts
        self.createTabOptionLayout.addWidget(self.createTabAnchor)
        self.createTabOptionLayout.addWidget(self.optionsWidget)

        self.createTabLayout.addWidget(self.ioWidget)
        self.createTabLayout.addWidget(self.poseListWidget)

        self.createTabWidget.setLayout(self.createTabOptionLayout)
        self.createTabAnchor.setLayout(self.createTabLayout)

        return self.createTabWidget


def DeleteWindowInstances(mayaMainWindow):
    """
        Close tool by type.
    """
    checkWidget = RbfManagerTool()

    #Check if window exists
    for child in mayaMainWindow.children():
        if not isinstance(child, QtGui.QWidget):
            continue
        #delete previous UI instance (isinstance was giving weird result)
        if child.__class__.__name__ == checkWidget.__class__.__name__:
            child.deleteLater()
            child.parent = None

    checkWidget = None


def Run():
    mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget) 

    DeleteWindowInstances(mayaMainWindow)

    tool = RbfManagerTool(parent=mayaMainWindow)
    tool.show()     

    return tool
