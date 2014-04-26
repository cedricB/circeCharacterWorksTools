//Maya ASCII 2011 scene
requires maya "2011";
requires "heimer.py" "1.0.0";
currentUnit -l centimeter -a degree -t film;

createNode transform -n "XX_ZERO";
	addAttr -ci true -sn "heimerType" -ln "heimerType" -dt "string";
	addAttr -ci true -h true -m -sn "element" -ln "element" -at "double";
	setAttr -l on -k on ".heimerType" -type "string" "WorldData";
	setAttr -s 4 ".element";
	setAttr -s 4 ".element";
createNode transform -n "XX_RefSpace" -p "XX_ZERO";
createNode locator -n "XX_RefSpaceShape" -p "XX_RefSpace";
	setAttr -k off ".v";
	setAttr -l on -cb off ".lpx";
	setAttr -l on -cb off ".lpy";
	setAttr -l on -cb off ".lpz";
createNode transform -n "XX_target" -p "XX_ZERO";
	setAttr ".t" -type "double3" 12 0 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr ".drp" yes;
createNode transform -n "XX_heimerDriven" -p "XX_ZERO";
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
	setAttr ".dla" yes;
createNode heimer -n "XX_heimer1";

connectAttr "XX_RefSpace.nds" "XX_ZERO.element[0]";
connectAttr "XX_target.nds" "XX_ZERO.element[1]";
connectAttr "XX_heimerDriven.nds" "XX_ZERO.element[2]";
connectAttr "XX_heimer1.nds" "XX_ZERO.element[3]";
connectAttr "XX_heimer1.r" "XX_heimerDriven.r";
connectAttr "XX_heimer1.t" "XX_heimerDriven.t";
connectAttr "XX_RefSpace.wim" "XX_heimer1.wtlMat";
connectAttr "XX_target.wm" "XX_heimer1.trgMat";
// End of WorldData.ma
