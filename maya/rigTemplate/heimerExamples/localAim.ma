//Maya ASCII 2011 scene
//Name: localAim.ma
//Last modified: Sat, Apr 26, 2014 05:52:10 PM
//Codeset: 1252
requires maya "2011";
requires "heimer.py" "1.0.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2011";
fileInfo "version" "2011";
fileInfo "cutIdentifier" "201003190014-771504";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "XX_ZERO";
	addAttr -ci true -sn "heimerType" -ln "heimerType" -dt "string";
	addAttr -ci true -h true -m -sn "element" -ln "element" -at "double";
	setAttr -l on -k on ".heimerType" -type "string" "local aim node";
	setAttr -s 3 ".element";
	setAttr -s 3 ".element";
createNode transform -n "XX_target" -p "XX_ZERO";
	setAttr ".t" -type "double3" 8 0 0 ;
createNode locator -n "XX_targetShape" -p "XX_target";
	setAttr -k off ".v";
	setAttr -l on -cb off ".lpx";
	setAttr -l on -cb off ".lpy";
	setAttr -l on -cb off ".lpz";
createNode transform -n "XX_drivenAIM" -p "XX_ZERO";
	setAttr ".dla" yes;
createNode heimer -n "XX_heimer1";
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :renderGlobalsList1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "XX_target.nds" "XX_ZERO.element[0]";
connectAttr "XX_drivenAIM.nds" "XX_ZERO.element[1]";
connectAttr "XX_heimer1.nds" "XX_ZERO.element[2]";
connectAttr "XX_heimer1.or" "XX_drivenAIM.r";
connectAttr "XX_targetShape.wp" "XX_heimer1.trgPos";
connectAttr "XX_drivenAIM.pim" "XX_heimer1.wtlMat";
// End of localAim.ma
