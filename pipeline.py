'''
Author: Alexandra Fischbach
Github repo: https://github.com/AlexFischbach/local_csf_pipeline/tree/main
Date: 04-18-2025
Contact: fischbach.a@northeastern.edu
'''

import os 

# ----------------------------------------------------------------
# USER-DEFINED PATHS AND PARAMETERS
# ----------------------------------------------------------------
base_dir = '/Users/alex/.../local_csf_pipeline/'
data_dir = os.path.join(base_dir, 'test/input/')
out_dir = os.path.join(base_dir, 'test/output/')

# Template for resampling ROI masks to MNI space
template_path = os.path.join(data_dir, 'anat/MNI_template/mni_icbm152_t1_tal_nlin_asym_09c.nii.gz')

# ROI input file 
roi = 'PAG'
roi_path = os.path.join(data_dir, f'anat/roi_mask/probabilistic/{roi}.nii.gz') 

# Subject-specific input files
subj_id = 'sub-011'
csf_mask_path = os.path.join(data_dir, f'anat/csf_prob_tissue/{subj_id}_T1w_space-MNI152NLin2009cAsym_class-CSF_probtissue.nii.gz')
func_mask_path=os.path.join(data_dir, f'func/{subj_id}_task-rest_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz')
confound_file_path = os.path.join(data_dir, f'func/{subj_id}_task-rest_run-01_bold_confounds.tsv')

# ----------------------------------------------------------------
# IMPORT PIPELINE FUNCTIONS
# ----------------------------------------------------------------
from utils.process_roi import (
    process_roi_mask,threshold_roi_mask,
    dilate_binary_roi_mask,
)

from utils.extract_csf import (
    extract_local_csf_mask,
    extract_local_csf_time_series,
    add_local_csf_time_series_to_confound_file,
)

from utils.func_timeseries import compute_functional_timeseries

# ----------------------------------------------------------------
# PIPELINE EXECUTION
# ----------------------------------------------------------------
# Define output basename for all intermediate files
file_basename = os.path.join(out_dir, roi)
print(f'Saving outputs with basename: {file_basename}')

# -------------------- STEP 1: Resample ROI Mask -----------------
proc_roi_path = file_basename + "_proc.nii.gz"
process_roi_mask(
    roi_path,
    template_path=template_path,
    save_path = proc_roi_path
)

# -------------------- STEP 2: Threshold ROI Mask ----------------
threshold_roi_path = file_basename + "_binary.nii.gz"

threshold_roi_mask(
    proc_roi_path,
    save_path = threshold_roi_path
)

# -------------------- STEP 3: Dilate ROI Mask -------------------
dilated_roi_path = file_basename + "_dilated.nii.gz"

dilate_binary_roi_mask(
    threshold_roi_path, 
    save_path = dilated_roi_path
)

# -------------------- STEP 4: Extract Local CSF Mask ------------
local_csf_mask_path = file_basename + "_local_csf_mask.nii.gz"

extract_local_csf_mask(
    csf_mask_path, 
    threshold_roi_path,
    dilated_roi_path, 
    save_path = local_csf_mask_path
)

# -------------------- STEP 5: Extract Local CSF Time Series -----
local_csf_ts_path = file_basename + "_local_csf_ts.csv"

extract_local_csf_time_series(
    func_mask_path, 
    local_csf_mask_path, 
    roi,
    save_path = local_csf_ts_path
)

# -------------------- STEP 6: Add CSF to Confound File ----------
mod_conf_path = os.path.join(out_dir, f"{subj_id}_confounds_mod.tsv")

add_local_csf_time_series_to_confound_file(
    confound_file_path, 
    local_csf_ts_path, 
    roi,
    save_path = mod_conf_path
)

# -------------------- STEP 7: Compute Denoised ROI Time Series --
corrected_ts_path = os.path.join(out_dir, f"{subj_id}_{roi}_corrected_ts.csv")

compute_functional_timeseries(
    func_mask_path, 
    threshold_roi_path, 
    mod_conf_path, 
    roi, 
    confound_vars = "Default", 
    save_path = corrected_ts_path
)

print(f"Pipeline completed. Outputs saved to {out_dir}")