//Maya ASCII 2013 scene
//Name: data.ma

requires maya "2013";
requires "geodesicWeight.py" "1.0.0";
createNode transform -n "XX_ZERO";
	addAttr -ci true -sn "foodType" -ln "foodType" -dt "string";
	addAttr -ci true -h true -m -sn "element" -ln "element" -at "double";
	setAttr ".t" -type "double3" 0.094910392002535801 0 0 ;
	setAttr -l on ".foodType" -type "string" "geodesicWeight";
	setAttr -s 4 ".element";
	setAttr -s 4 ".element";
createNode transform -n "XX_diamond1" -p "XX_ZERO";
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
createNode mesh -n "XX_diamond1Shape" -p "XX_diamond1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 6 ".vt[0:5]"  0 -0.5 0 -0.5 0 0 0 0 0.5 0.5 0 0 0 0.5 0
		 0 0 -0.5;
	setAttr -s 12 ".ed[0:11]"  1 2 1 2 3 1 1 5 1 5 3 1 0 1 0 0 2 1 0 3 0
		 1 4 0 2 4 1 3 4 0 4 5 1 5 0 1;
	setAttr -s 8 -ch 24 ".fc[0:7]" -type "polyFaces" 
		f 3 5 -1 -5
		mu 0 3 0 2 1
		f 3 6 -2 -6
		mu 0 3 0 3 2
		f 3 0 8 -8
		mu 0 3 1 2 4
		f 3 1 9 -9
		mu 0 3 2 3 4
		f 3 10 -3 7
		mu 0 3 4 6 5
		f 3 -10 -4 -11
		mu 0 3 4 7 6
		f 3 2 11 4
		mu 0 3 5 6 8
		f 3 3 -7 -12
		mu 0 3 6 7 8;
createNode transform -n "XX_Target1" -p "XX_ZERO";
	setAttr ".t" -type "double3" 4.9050896079974642 0 0 ;
createNode locator -n "XX_TargetShape1" -p "XX_Target1";
	setAttr -k off ".v";
	setAttr -l on -cb off ".lpx";
	setAttr -l on -cb off ".lpy";
	setAttr -l on -cb off ".lpz";
createNode pointMatrixMult -n "XX_wrlToLocal1";
createNode geodesicWeight -n "XX_gWgth1";
	setAttr ".col" 7;
connectAttr "XX_diamond1.nds" "XX_ZERO.element[0]";
connectAttr "XX_Target1.nds" "XX_ZERO.element[1]";
connectAttr "XX_wrlToLocal1.nds" "XX_ZERO.element[2]";
connectAttr "XX_gWgth1.nds" "XX_ZERO.element[3]";
connectAttr "XX_TargetShape1.wp" "XX_wrlToLocal1.ip";
connectAttr "XX_diamond1.wim" "XX_wrlToLocal1.im";
connectAttr "XX_diamond1Shape.o" "XX_gWgth1.inS";
connectAttr "XX_wrlToLocal1.o" "XX_gWgth1.cPos";
// End of data.ma
