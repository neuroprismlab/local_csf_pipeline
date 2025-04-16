import os 
from config import (
    CONDITION, SUBJECT_ID, DATA_DIR, ROI_DIR, TEMPLATE_PATH, 
    OUTPUT_DIR, DEFAULT_REST_RUNS, CONDITION, DEFAULT_ROIS, 
    DEFAULT_MOTION_CONFOUNDS
)

from utils.process_roi import (
    initialize_roi_dict,
    process_roi_mask,
    threshold_roi_mask,
    dilate_binary_roi_mask,
)

from utils.extract_csf import (
    extract_local_csf_mask,
    extract_local_csf_time_series,
    add_local_csf_time_series_to_confound_file,
)

from utils.func_timeseries import compute_functional_timeseries
# ------------------- SETUP --------------------------------
subj = SUBJECT_ID 

data_dir = DATA_DIR
out_dir = OUTPUT_DIR
roi_dir = ROI_DIR

roi_files = initialize_roi_dict(ROI_DIR, subj)
template_path = TEMPLATE_PATH

run_numbers = DEFAULT_REST_RUNS
subcortical_roi = DEFAULT_ROIS
condition = CONDITION
motion_confounds = DEFAULT_MOTION_CONFOUNDS

# -------------------- STEP 1 ------------------------------
def run_process_roi_mask():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            is_subject_level = subj in os.path.basename(roi_path)

            output_file_name = f"{subj}_{roi_name}_mask_proc.nii.gz" if is_subject_level \
                        else f"{roi_name}_mask_proc.nii.gz"
            
            roi_out_dir = os.path.join(out_dir, "1.proc_roi", roi_name)
            os.makedirs(roi_out_dir, exist_ok=True)

            save_path = os.path.join(roi_out_dir, output_file_name)

            process_roi_mask(
                roi_path,
                roi_name,
                template_path,
                save_path = save_path
            )
# -------------------- STEP 2 ------------------------------
def run_threshold_roi_mask():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            is_subject_specific = subj in os.path.basename(roi_path)

            proc_filename = f"{subj}_{roi_name}_mask_proc.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_proc.nii.gz"
            
            processed_roi_path = os.path.join(out_dir, "1.proc_roi", roi_name, proc_filename)

            output_file_name = f"{subj}_{roi_name}_mask_binary.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_binary.nii.gz"
            
            roi_out_dir = os.path.join(out_dir, "2.thresh_roi", roi_name)
            os.makedirs(roi_out_dir, exist_ok=True)

            save_path = os.path.join(roi_out_dir, output_file_name)
            
            threshold_roi_mask(
                processed_roi_path,
                save_path = save_path
            )

# -------------------- STEP 3 --------------------
def run_dilate_binary_roi_mask():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            is_subject_specific = subj in os.path.basename(roi_path)

            binary_filename = f"{subj}_{roi_name}_mask_binary.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_binary.nii.gz"
            
            binary_roi_path = os.path.join(out_dir, "2.thresh_roi", roi_name, binary_filename)

            output_file_name = f"{subj}_{roi_name}_mask_dilated.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_dilated.nii.gz"
            
            roi_out_dir = os.path.join(out_dir, "3.dilated_roi", roi_name)
            os.makedirs(roi_out_dir, exist_ok=True)

            save_path = os.path.join(roi_out_dir, output_file_name)

            dilate_binary_roi_mask(
                binary_roi_path, 
                save_path = save_path
            )
# -------------------- STEP 4 --------------------
def run_extract_local_csf_mask():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            is_subject_specific = subj in os.path.basename(roi_path)

            binary_filename = f"{subj}_{roi_name}_mask_binary.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_binary.nii.gz"
            
            dilated_filename = f"{subj}_{roi_name}_mask_dilated.nii.gz" if is_subject_specific \
                else f"{roi_name}_mask_dilated.nii.gz"
            
            binary_roi_path = os.path.join(out_dir, "2.thresh_roi", roi_name, binary_filename)

            dilated_roi_path = os.path.join(out_dir, "3.dilated_roi", roi_name, dilated_filename)

            csf_mask_path = os.path.join(data_dir, subj, "anat", f"{subj}_T1w_space-MNI152NLin2009cAsym_class-CSF_probtissue.nii.gz")

            roi_out_dir = os.path.join(out_dir, "4.local_csf_mask", roi_name)
            os.makedirs(roi_out_dir, exist_ok=True)

            output_filename = f"{subj}_{roi_name}_local_csf_mask.nii.gz"

            save_path = os.path.join(roi_out_dir, output_filename)

            extract_local_csf_mask(
                csf_mask_path, 
                binary_roi_path, 
                dilated_roi_path, 
                save_path = save_path
            )

# -------------------- STEP 5 --------------------
def run_extract_local_csf_time_series():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            for run in run_numbers:
                func_mask_path = os.path.join(data_dir, subj, "func", f"{subj}_task-{condition}_{run}_bold_space-MNI152NLin2009cAsym_preproc.nii.gz")
                
                local_csf_filename = f"{subj}_{roi_name}_local_csf_mask.nii.gz"
                
                local_csf_path = os.path.join(out_dir, "4.local_csf_mask", roi_name, local_csf_filename)
                
                ts_out_dir = os.path.join(out_dir, "5.local_csf_ts", roi_name)
                os.makedirs(ts_out_dir, exist_ok=True)
                
                ts_filename = f"{subj}_task-{condition}_{run}_{roi_name}_local_csf_ts.csv"
                
                save_path = os.path.join(ts_out_dir, ts_filename)
            
                extract_local_csf_time_series(
                    func_mask_path, 
                    local_csf_path, 
                    roi_name, 
                    save_path = save_path)

# -------------------- STEP 6 --------------------
def run_add_local_csf_time_series_to_confound_file():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            for run in run_numbers:
                confound_file_path = os.path.join(data_dir, subj, "func", f"{subj}_task-{condition}_{run}_bold_confounds.tsv")
                
                ts_filename = f"{subj}_task-{condition}_{run}_{roi_name}_local_csf_ts.csv"
                
                local_csf_timeseries_path = os.path.join(out_dir, "5.local_csf_ts", roi_name, ts_filename)
                
                conf_out_dir = os.path.join(out_dir, "6.mod_confounds", roi_name)
                os.makedirs(conf_out_dir, exist_ok=True)
                
                output_filename = f"{subj}_task-{condition}_{run}_bold_confounds_mod.tsv"
                
                save_path = os.path.join(conf_out_dir, output_filename)
                
                add_local_csf_time_series_to_confound_file(
                    confound_file_path, 
                    local_csf_timeseries_path, 
                    roi_name,
                    save_path=save_path
                )

# -------------------- STEP 7 --------------------
def run_compute_functional_timeseries():
    for roi_name in subcortical_roi:
        for roi_path in roi_files.get(roi_name, []):
            for run in run_numbers:
                func_mask_path = os.path.join(data_dir, subj, "func", f"{subj}_task-{condition}_{run}_bold_space-MNI152NLin2009cAsym_preproc.nii.gz")
                
                binary_filename = f"{subj}_{roi_name}_mask_binary.nii.gz" if subj in os.path.basename(roi_path) \
                    else f"{roi_name}_mask_binary.nii.gz"
            
                binary_roi_path = os.path.join(out_dir, "2.thresh_roi", roi_name, binary_filename)
                
                mod_conf_path = os.path.join(out_dir, "6.mod_confounds", roi_name, f"{subj}_task-{condition}_{run}_bold_confounds_mod.tsv")
                
                ts_out_dir = os.path.join(out_dir, "7.corrected_ts", roi_name)
                os.makedirs(ts_out_dir, exist_ok=True)
                
                ts_filename = f"{subj}_task-{condition}_{run}_{roi_name}_corrected_ts.csv"
                
                save_path = os.path.join(ts_out_dir, ts_filename)

                compute_functional_timeseries(
                    func_mask_path, 
                    binary_roi_path, 
                    mod_conf_path, 
                    roi_name, 
                    confound_vars="Default", 
                    save_path=save_path
                )

if __name__ == "__main__":
    run_process_roi_mask()
    run_threshold_roi_mask()
    run_dilate_binary_roi_mask()
    run_extract_local_csf_mask()
    run_extract_local_csf_time_series()
    run_add_local_csf_time_series_to_confound_file()
    run_compute_functional_timeseries()
