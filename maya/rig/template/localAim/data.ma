//Maya ASCII 2011 scene
//Name: localAim.ma
requires maya "2011";
requires "heimer.py" "1.0.0";
currentUnit -l centimeter -a degree -t film;

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

connectAttr "XX_target.nds" "XX_ZERO.element[0]";
connectAttr "XX_drivenAIM.nds" "XX_ZERO.element[1]";
connectAttr "XX_heimer1.nds" "XX_ZERO.element[2]";
connectAttr "XX_heimer1.or" "XX_drivenAIM.r";
connectAttr "XX_targetShape.wp" "XX_heimer1.trgPos";
connectAttr "XX_drivenAIM.pim" "XX_heimer1.wtlMat";
// End of localAim.ma
