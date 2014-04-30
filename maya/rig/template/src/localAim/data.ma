//Maya ASCII 2013 scene
//Name: data.ma
//Last modified: Tue, Apr 29, 2014 12:11:53 AM
//Codeset: 1252
requires maya "2013";
requires "heimer.py" "1.0.0";
currentUnit -l centimeter -a degree -t film;
createNode transform -n "XX_ZERO";
	addAttr -ci true -sn "foodType" -ln "foodType" -dt "string";
	addAttr -ci true -h true -m -sn "element" -ln "element" -at "double";
	setAttr -l on -k on ".foodType" -type "string" "local aim node";
	setAttr -s 3 ".element";
	setAttr -s 3 ".element";
createNode transform -n "XX_target" -p "XX_ZERO";
	setAttr ".t" -type "double3" 8 0 0 ;
	setAttr ".dh" yes;
	setAttr ".drp" yes;
createNode locator -n "XX_targetShape" -p "XX_target";
	setAttr -l on -k off ".v" no;
	setAttr -l on ".lodv" no;
	setAttr -l on -cb off ".lpx";
	setAttr -l on -cb off ".lpy";
	setAttr -l on -cb off ".lpz";
	setAttr -l on -cb off ".lsx";
	setAttr -l on -cb off ".lsy";
	setAttr -l on -cb off ".lsz";
createNode transform -n "XX_drivenAIM" -p "XX_ZERO";
	setAttr -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".dla" yes;
createNode heimer -n "XX_heimer1";
connectAttr "XX_target.nds" "XX_ZERO.element[0]";
connectAttr "XX_drivenAIM.nds" "XX_ZERO.element[1]";
connectAttr "XX_heimer1.nds" "XX_ZERO.element[2]";
connectAttr "XX_heimer1.or" "XX_drivenAIM.r";
connectAttr "XX_targetShape.wp" "XX_heimer1.trgPos";
connectAttr "XX_drivenAIM.pim" "XX_heimer1.wtlMat";
// End of data.ma
