//Maya ASCII 2013 scene
//Name: data.ma
//Last modified: Mon, Apr 28, 2014 10:01:13 PM
//Codeset: 1252
requires maya "2013";
requires "stereoCamera" "10.0";
requires "twistKnot.py" "0.15.2";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2013";
fileInfo "version" "2013 x64";
fileInfo "cutIdentifier" "201202220241-825136";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "XX_Twist_anchor";
	addAttr -ci true -sn "TWIST" -ln "TWIST" -at "double";
	addAttr -ci true -sn "readerLink" -ln "readerLink" -at "double";
	setAttr -k off -cb on ".v";
	setAttr -cb on ".TWIST";
createNode transform -n "XX_TwistDriver_BUFFER" -p "XX_Twist_anchor";
	addAttr -ci true -sn "twist" -ln "twist" -at "double";
	setAttr -k off -cb on ".v";
	setAttr ".dh" yes;
	setAttr -cb on ".twist";
createNode transform -n "XX_TwistDriver" -p "XX_TwistDriver_BUFFER";
	addAttr -ci true -sn "TWIST" -ln "TWIST" -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".TWIST";
createNode orientConstraint -n "XX_TwistEXTRACT_orientConstraint1" -p "XX_Twist_anchor";
	addAttr -ci true -sn "w0" -ln "TwistDriverW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "w1" -ln "arm_twistBASEW1" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "twistReaderConstraint" -ln "twistReaderConstraint" -at "double";
	setAttr -l on ".nds";
	setAttr -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr -l on -k off ".ox";
	setAttr -l on -k off ".oy";
	setAttr -l on -k off ".oz";
	setAttr ".int" 0;
	setAttr -l on ".w0" 0.5;
	setAttr -l on ".w1" 0.5;
	setAttr -l on -k on ".twistReaderConstraint";
createNode unitConversion -n "XX_TwistDriver_unitConversion1";
	setAttr ".cf" 114.59155902616465;
createNode twistKnot -n "XX_TwistKnot1";
select -ne :time1;
	setAttr ".o" 0;
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
select -ne :defaultRenderingList1;
select -ne :renderGlobalsList1;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "XX_TwistDriver_unitConversion1.o" "XX_Twist_anchor.TWIST";
connectAttr "XX_TwistEXTRACT_orientConstraint1.nds" "XX_Twist_anchor.readerLink"
		;
connectAttr "XX_TwistDriver_unitConversion1.o" "XX_TwistDriver_BUFFER.twist";
connectAttr "XX_TwistDriver_unitConversion1.o" "XX_TwistDriver.TWIST";
connectAttr "XX_TwistEXTRACT_orientConstraint1.cr" "XX_TwistEXTRACT_orientConstraint1.r"
		;
connectAttr "XX_Twist_anchor.ro" "XX_TwistEXTRACT_orientConstraint1.cro";
connectAttr "XX_Twist_anchor.wim" "XX_TwistEXTRACT_orientConstraint1.cpim";
connectAttr "XX_TwistDriver.r" "XX_TwistEXTRACT_orientConstraint1.tg[0].tr";
connectAttr "XX_TwistDriver.ro" "XX_TwistEXTRACT_orientConstraint1.tg[0].tro";
connectAttr "XX_TwistDriver.pm" "XX_TwistEXTRACT_orientConstraint1.tg[0].tpm";
connectAttr "XX_TwistEXTRACT_orientConstraint1.w0" "XX_TwistEXTRACT_orientConstraint1.tg[0].tw"
		;
connectAttr "XX_TwistKnot1.or" "XX_TwistEXTRACT_orientConstraint1.tg[1].tr";
connectAttr "XX_Twist_anchor.ro" "XX_TwistEXTRACT_orientConstraint1.tg[1].tro";
connectAttr "XX_Twist_anchor.wm" "XX_TwistEXTRACT_orientConstraint1.tg[1].tpm";
connectAttr "XX_TwistEXTRACT_orientConstraint1.w1" "XX_TwistEXTRACT_orientConstraint1.tg[1].tw"
		;
connectAttr "XX_TwistEXTRACT_orientConstraint1.rx" "XX_TwistDriver_unitConversion1.i"
		;
connectAttr "XX_Twist_anchor.wm" "XX_TwistKnot1.rMat";
connectAttr "XX_TwistDriver.wm" "XX_TwistKnot1.drMat";
// End of data.ma
