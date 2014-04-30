//Maya ASCII 2013 scene
//Name: data.ma
//Last modified: Wed, Apr 30, 2014 02:35:33 AM
//Codeset: 1252
requires maya "2013";
requires "caramel.py" "1.285";

createNode transform -n "XX_ANCHOR";
	addAttr -ci true -sn "foodType" -ln "foodType" -dt "string";
	addAttr -ci true -h true -m -sn "element" -ln "element" -at "double";
	setAttr -l on ".foodType" -type "string" "caramel";
	setAttr -s 4 ".element";
	setAttr -s 4 ".element";
createNode transform -n "XX_Input" -p "XX_ANCHOR";
	setAttr -k off -cb on ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "XX_knot1" -p "XX_Input";
	setAttr ".uoc" yes;
	setAttr ".oc" 1;
	setAttr ".dh" yes;
	setAttr ".drp" yes;
createNode transform -n "XX_knot2" -p "XX_Input";
	setAttr ".uoc" yes;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 3 0 0 ;
	setAttr ".dh" yes;
	setAttr ".drp" yes;
createNode transform -n "XX_knot3" -p "XX_Input";
	setAttr ".uoc" yes;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 6 0 0 ;
	setAttr ".dh" yes;
	setAttr ".drp" yes;
createNode transform -n "XX_knot4" -p "XX_Input";
	setAttr ".uoc" yes;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 9 0 0 ;
	setAttr ".dh" yes;
	setAttr ".drp" yes;
createNode transform -n "XX_Ribbon" -p "XX_ANCHOR";
	setAttr -k off -cb on ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsSurface -n "XX_RibbonShape" -p "XX_Ribbon";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 3;
	setAttr ".dvv" 3;
	setAttr ".cpr" 15;
	setAttr ".cps" 4;
createNode caramel -n "XX_caramel1";

connectAttr "XX_caramel1.out" "XX_RibbonShape.cr";
connectAttr "XX_knot1.wm" "XX_caramel1.in[0]";
connectAttr "XX_knot2.wm" "XX_caramel1.in[1]";
connectAttr "XX_knot3.wm" "XX_caramel1.in[2]";
connectAttr "XX_knot4.wm" "XX_caramel1.in[3]";

connectAttr "XX_ANCHOR.nds" "XX_ANCHOR.element[0]";
connectAttr "XX_Input.nds" "XX_ANCHOR.element[1]";
connectAttr "XX_Ribbon.nds" "XX_ANCHOR.element[2]";
connectAttr "XX_caramel1.nds" "XX_ANCHOR.element[3]";
// End of data.ma
