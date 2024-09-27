"""
Important points:
0. The script is made for RayStation 12A DTK. Therefore, the script might not work with other versions of RayStation.
1. A planning CT must be assigned to an imaging system (CT modality). 
2. The CBCT image must be assigned to an imaging system (CBCT modality).
3. Planning CT must have an external roi contoured.
4. The ROIs generated using DLS on cCBCT may not be accurate. It is recommended to verify the DLS generated ROIs and manually corrected if required before generating APvCT.
"""

import numpy as np
from connect import *
case = get_current("Case")

#######################################################################################
# Change the parameters according to patient data
PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CBCT = -600
PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CCBCT = -250
PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CT = -250
PLANNING_CT_NAME = "CT Planning"
CBCT_NAME = "CBCT1"

# Name of CTV and ROIs (Prostate cancer)
CTV_PRIMARY = "CTV P"
BLADDER = "Bladder"
RECTUM = "Anorectum"
FEMORAL_HEAD_RIGHT = "Femur_Head_R"
FEMORAL_HEAD_LEFT = "Femur_Head_L"
#######################################################################################
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with CompositeAction("Prepocessing"):

    examination = case.Examinations[CBCT_NAME]

    # create external on CBCT
    case.PatientModel.RegionsOfInterest["External"].CreateExternalGeometry(
        Examination=examination,
        ThresholdLevel=PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CBCT,
    )

    # Create a FOV
    case.PatientModel.CreateRoi(
        Name="Field-of-view",
        Color="Red",
        Type="FieldOfView",
        TissueName=None,
        RbeCellTypeName=None,
        RoiMaterial=None,
    )
    case.PatientModel.RegionsOfInterest["Field-of-view"].CreateFieldOfViewROI(
        ExaminationName=CBCT_NAME
    )

    # Create a contracted FOV
    case.PatientModel.CreateRoi(
        Name="ContractedFOV",
        Color="Pink",
        Type="Control",
        TissueName=None,
        RbeCellTypeName=None,
        RoiMaterial=None,
    )

    case.PatientModel.RegionsOfInterest["ContractedFOV"].CreateMarginGeometry(
        Examination=examination,
        SourceRoiName="Field-of-view",
        MarginSettings={
            "Type": "Contract",
            "Superior": 2,
            "Inferior": 2,
            "Anterior": 2,
            "Posterior": 2,
            "Right": 2,
            "Left": 2,
        },
    )

    # Frame Of Reference Registration between pCT and present CBCT
    case.CreateNamedIdentityFrameOfReferenceRegistration(
        FromExaminationName=CBCT_NAME,
        ToExaminationName=PLANNING_CT_NAME,
        RegistrationName="Frame-of-reference registration",
        Description=None,
    )

    case.ComputeGrayLevelBasedRigidRegistration(
        FloatingExaminationName=CBCT_NAME,
        ReferenceExaminationName=PLANNING_CT_NAME,
        UseOnlyTranslations=False,
        HighWeightOnBones=False,
        InitializeImages=True,
        FocusRoisNames=[],
        RegistrationName=None,
    )

    # Copy the contracted FOV to planning CT
    case.PatientModel.CopyRoiGeometries(
        SourceExamination=examination,
        TargetExaminationNames=[PLANNING_CT_NAME],
        RoiNames=["ContractedFOV"],
        ImageRegistrationNames=[],
        TargetExaminationNamesToSkipAddedReg=[PLANNING_CT_NAME],
    )

    # Deformable registration between pCT and present CBCT
    case.PatientModel.CreateHybridDeformableRegistrationGroup(
        RegistrationGroupName=f"HybridDefReg_{CBCT_NAME}_",
        ReferenceExaminationName=PLANNING_CT_NAME,
        TargetExaminationNames=[CBCT_NAME],
        ControllingRoiNames=[],
        ControllingPoiNames=[],
        FocusRoiNames=["ContractedFOV"],
        AlgorithmSettings={
            "NumberOfResolutionLevels": 3,
            "InitialResolution": {"x": 0.5, "y": 0.5, "z": 0.5},
            "FinalResolution": {"x": 0.25, "y": 0.25, "z": 0.25},
            "InitialGaussianSmoothingSigma": 2,
            "FinalGaussianSmoothingSigma": 0.333333333333333,
            "InitialGridRegularizationWeight": 400,
            "FinalGridRegularizationWeight": 400,
            "ControllingRoiWeight": 0.5,
            "ControllingPoiWeight": 0.1,
            "MaxNumberOfIterationsPerResolutionLevel": 1000,
            "ImageSimilarityMeasure": "CorrelationCoefficient",
            "DeformationStrategy": "Default",
            "ConvergenceTolerance": 1e-05,
        },
    )


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with CompositeAction("Create cCBCT"):

    # Create CORRECTED CBCT
    ccbct_name = f"cCBCT_{CBCT_NAME}"
    case.CreateNewCorrectedCbct(
        CorrectedCbctName=ccbct_name,
        ReferenceExaminationName=PLANNING_CT_NAME,
        TargetExaminationName=CBCT_NAME,
        FovRoiName="Field-of-view",
        DeformableRegistrationName=f"HybridDefReg_{CBCT_NAME}_1",
    )

    # Create external ROI on cCBCT
    case.PatientModel.RegionsOfInterest["External"].CreateExternalGeometry(
        Examination=case.Examinations[ccbct_name],
        ThresholdLevel=PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CCBCT,
    )


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with CompositeAction("Create vCT"):
    # CREATE VIRTUAL CT
    vct_name = f"vCT_{CBCT_NAME}"
    case.CreateNewVirtualCt(
        VirtualCtName=vct_name,
        ReferenceExaminationName=PLANNING_CT_NAME,
        TargetExaminationName=CBCT_NAME,
        DeformableRegistrationName=f"HybridDefReg_{CBCT_NAME}_1",
        FovRoiName="Field-of-view",
    )

    # Create external on vCT
    case.PatientModel.RegionsOfInterest["External"].CreateExternalGeometry(
        Examination=case.Examinations[vct_name],
        ThresholdLevel=PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CT,
    )


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with CompositeAction("Create deformabale registration for DLS"):
    # CREATE ROI ON CORRECTED CBCT USING DEEP LEARNING MODEL (can be done by any other method available)
    # Deformable registration from cCBCT to planning CT
    case.PatientModel.RegionsOfInterest["Field-of-view"].CreateFieldOfViewROI(
        ExaminationName=ccbct_name
    )
    case.PatientModel.CreateHybridDeformableRegistrationGroup(
        RegistrationGroupName=f"HybridDefReg_ML_{ccbct_name}_",
        ReferenceExaminationName=ccbct_name,
        TargetExaminationNames=[PLANNING_CT_NAME],
        ControllingRoiNames=[],
        ControllingPoiNames=[],
        FocusRoiNames=["ContractedFOV"],
        AlgorithmSettings={
            "NumberOfResolutionLevels": 3,
            "InitialResolution": {"x": 0.5, "y": 0.5, "z": 0.5},
            "FinalResolution": {"x": 0.25, "y": 0.25, "z": 0.25},
            "InitialGaussianSmoothingSigma": 2,
            "FinalGaussianSmoothingSigma": 0.333333333333333,
            "InitialGridRegularizationWeight": 400,
            "FinalGridRegularizationWeight": 400,
            "ControllingRoiWeight": 0.5,
            "ControllingPoiWeight": 0.1,
            "MaxNumberOfIterationsPerResolutionLevel": 1000,
            "ImageSimilarityMeasure": "CorrelationCoefficient",
            "DeformationStrategy": "Default",
            "ConvergenceTolerance": 1e-05,
        },
    )


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Run the DLS segmentation
ccbct_examination = case.Examinations[ccbct_name]
ccbct_examination.RunDeepLearningSegmentationComposite(
    ExaminationsAndRegistrations={PLANNING_CT_NAME: f"HybridDefReg_ML_{ccbct_name}_1"},
    ModelNamesAndRoisToInclude={
        "RSL Male Pelvic CT": [
            BLADDER,
            FEMORAL_HEAD_LEFT,
            FEMORAL_HEAD_RIGHT,
            RECTUM,
            "Prostate",
        ]
    },
)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
with CompositeAction("Create APvCT"):
    # CREATE ANATOMY PRESERVING VIRTUAL CT
    
    # Copy geometries from cCBCT to CBCTs
    case.PatientModel.CopyRoiGeometries(
        SourceExamination=ccbct_examination,
        TargetExaminationNames=[CBCT_NAME],
        RoiNames=[BLADDER, RECTUM, FEMORAL_HEAD_RIGHT, FEMORAL_HEAD_LEFT],
        ImageRegistrationNames=[],
        TargetExaminationNamesToSkipAddedReg=[CBCT_NAME],
    )

    # Create a new deformable registration group from CBCT to pCT with controlling contours
    case.PatientModel.CreateHybridDeformableRegistrationGroup(
        RegistrationGroupName=f"HybridDefReg_ctrlroi_{CBCT_NAME}_",
        ReferenceExaminationName=PLANNING_CT_NAME,
        TargetExaminationNames=[CBCT_NAME],
        ControllingRoiNames=[BLADDER, RECTUM, FEMORAL_HEAD_RIGHT, FEMORAL_HEAD_LEFT],
        ControllingPoiNames=[],
        FocusRoiNames=["ContractedFOV"],
        AlgorithmSettings={
            "NumberOfResolutionLevels": 3,
            "InitialResolution": {"x": 0.5, "y": 0.5, "z": 0.5},
            "FinalResolution": {"x": 0.25, "y": 0.25, "z": 0.25},
            "InitialGaussianSmoothingSigma": 2,
            "FinalGaussianSmoothingSigma": 0.333333333333333,
            "InitialGridRegularizationWeight": 1500,
            "FinalGridRegularizationWeight": 1000,
            "ControllingRoiWeight": 0.5,
            "ControllingPoiWeight": 0.1,
            "MaxNumberOfIterationsPerResolutionLevel": 1000,
            "ImageSimilarityMeasure": "CorrelationCoefficient",
            "DeformationStrategy": "Default",
            "ConvergenceTolerance": 1e-05,
        },
    )

    # Create the APvCT from CBCT
    apvct_name = f"APvCT_{CBCT_NAME}"
    case.CreateNewVirtualCt(
        VirtualCtName=apvct_name,
        ReferenceExaminationName=PLANNING_CT_NAME,
        TargetExaminationName=CBCT_NAME,
        DeformableRegistrationName=f"HybridDefReg_ctrlroi_{CBCT_NAME}_1",
        FovRoiName="Field-of-view",
    )

    # Create external on APvCT
    case.PatientModel.RegionsOfInterest["External"].CreateExternalGeometry(
        Examination=case.Examinations[apvct_name],
        ThresholdLevel=PATIENT_SPECIFIC_THRESHOLD_LEVEL_FOR_CT,
    )
