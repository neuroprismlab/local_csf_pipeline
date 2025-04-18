'''
Author: Alexandra Fischbach
Github repo: https://github.com/AlexFischbach/local_csf_pipeline/tree/main
Date: 04-18-2025
Contact: fischbach.a@northeastern.edu
'''

def extract_local_csf_mask( 
    csf_mask_path,  
    threshold_roi_path,
    dilated_roi_path,
    csf_threshold=0.6,
    save_path=None,
    verbose=True
):
    '''
    Extracts a local CSF mask by identifying CSF voxels that lie within a dilated ROI 
    but outside the original binary ROI. Saves the result as a binary NIfTI image.

    Input Parameters
    ----------------
    csf_mask_path : str
        Full path to the CSF probability mask in MNI space
        (e.g., '/your/path/sub-001_T1w_space-MNI152NLin2009cAsym_class-CSF_probtissue.nii.gz').
    
    threshold_roi_path : str
        Full path to binary ROI mask 
        (e.g., 'your/path/PAG_mask_binary.nii.gz')
    
    dilated_roi_path : str
        Full path to dilated binary ROI
        (e.g., 'your/path/PAG_mask_dilated.nii.gz')
   
    csf_threshold : float, optional
        Threshold to binarize the CSF probability map. Default is 0.6.
        Thresholding is skipped if the CSF image is already binary.
    
    save_path : str, optional
        Full path to save the resulting local CSF mask (NIfTI format). If None, the file is not saved.

    verbose : bool, optional
        If True, prints progress messages. Default is True.
    
    Returns
    -------
    local_csf_nii : nibabel.Nifti1Image
        Binary NIfTI image of the extracted local CSF mask.

    Notes
    -----
    -  Local CSF is defined as: (CSF voxels) ∩ (dilated ROI) ∩ (outside original ROI).

    '''
    import os
    import numpy as np
    import nibabel as nib

    # Input validation
    # -----------------
    if not os.path.exists(csf_mask_path):
        raise FileNotFoundError(f"CSF probability mask not found: {csf_mask_path}")
    
    csf_nii = nib.load(csf_mask_path)   # Subject-specific CSF tissue probability mask 
    csf_np = csf_nii.get_fdata()

    # Threshold probabilistic CSF mask (if needed)
    # --------------------------------------------
    is_binary = np.all(np.logical_or(csf_np == 0, csf_np == 1))
    if not is_binary:
        csf_np = np.where(csf_np >= csf_threshold, 1, 0)
        if verbose:
            print(f"Thresholded CSF mask at {csf_threshold}.")
    else:
        if verbose:
            print("CSF mask is already binary. No thresholding applied.")
    
    binary_roi_nii = nib.load(threshold_roi_path) # Original binary ROI mask
    binary_roi_np = binary_roi_nii.get_fdata()

    dilated_roi_nii = nib.load(dilated_roi_path) # Dilated ROI mask
    dilated_roi_np = dilated_roi_nii.get_fdata()
    
    # Define local CSF mask
    # ---------------------
    local_csf_np = np.where(
        (csf_np > 0) & (dilated_roi_np > 0) & (binary_roi_np == 0), 1, 0)
    if np.sum(local_csf_np) == 0:
        raise ValueError("Extracted local CSF mask is empty.")
    
    # Create local CSF NIfTI image
    # ------------------------------
    local_csf_nii = nib.Nifti1Image(
        local_csf_np.astype(np.uint8), 
        dilated_roi_nii.affine,
        dilated_roi_nii.header)
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        nib.save(local_csf_nii, save_path)
        if verbose:
            print(f"Local CSF mask saved to: {save_path}\n")

    return local_csf_nii

def extract_local_csf_time_series(
    func_mask_path,
    local_csf_mask_path,
    roi,
    save_path=None,
    verbose=True
):
    '''
    Extracts the average CSF time series from a 4D functional image using a 
    binary local CSF mask. The resulting time series is saved as a CSV file.

    Input Parameters
    ----------------
    func_mask_path : str
        Full path to the 4D functional image (e.g., preprocessed BOLD image in MNI space).
        The image should be aligned to the same space as the CSF mask.
        (e.g., 'sub-011_task-rest_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz')
    
    local_csf_mask_path : str
        Full path to the binary local CSF mask (NIfTI image). 
        Must be aligned with the functional image.

    
    roi : str
        Name of the ROI used to label the output time series column.
        (e.g., 'PAG')
    
    save_path : str, optional
        Full path to save the resulting CSF time series as a CSV file.
        If None, the time series is not saved.

    verbose: bool, optional
        If True, prints status messages. Default is True.
    
    Returns
    -------
    csf_timeseries_df : pandas.DataFrame
        DataFrame containing the average CSF signal per timepoint (TR).

    Notes
    -----
    - NiftiMasker reduces the 4D image (x, y, z, time) to 2D (timepoints × voxels).
    - The time series is computed by averaging across all CSF voxels at each timepoint.
    - This time series can be used as a nuisance regressor in further analysis.
    
    '''
    import os 
    import numpy as np 
    import pandas as pd
    import nibabel as nib
    from nilearn.input_data import NiftiMasker # For masking and extracting time series

    if not os.path.exists(func_mask_path):
        raise FileNotFoundError(f"Functional mask not found: {func_mask_path}")
   
    func_nii = nib.load(func_mask_path)              # 4D functional BOLD image   
    local_csf_nii = nib.load(local_csf_mask_path)         # Local CSF mask (binary NIfTI image)          
    masker =  NiftiMasker(mask_img=local_csf_nii)    # Masker object to apply the BOLD image 
    func_nii_masked = masker.fit_transform(func_nii) # Shape: (n_timepoints, n_voxels)

    # Extract mean CSF time series
    # -----------------------------
    mean_csf_np = np.mean(func_nii_masked, axis=1)   # Average across all voxels per TR
    column_label = f"{roi}_local_csf"
    csf_timeseries_df = pd.DataFrame(mean_csf_np, columns=[column_label])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        csf_timeseries_df.to_csv(save_path, index=False)
        if verbose:
            print(f"CSF time series saved to: {save_path}\n")

    return csf_timeseries_df

def add_local_csf_time_series_to_confound_file(
    confound_file_path, 
    local_csf_ts_path, 
    roi, 
    save_path = None,
    verbose = True

       
):
    '''
    Adds a local CSF time series column for a given ROI to an existing fMRIPrep confound file.

    Input Parameters
    ----------------
    confound_file_path : str
        Path to the existing confound file (TSV format) generated by fMRIPrep.
        (e.g., '/your/path/sub-001_task-rest_run-01_bold_confounds.tsv')
    
    local_csf_ts_path : str
        Path to local CSF time-series.
       
    roi : str
        Name of the ROI used to identify the column in the CSF time series DataFrame
        (e.g., 'R_amygdala').
    
    save_path : str, optional
        If provided, saves the updated confound file to this path.
        If None, the updated confound DataFrame is returned without saving.
    
    verbose : bool, optional
        If True, prints status messages. Default is True.
    
    Returns
    -------
    modified_conf_df : pandas.DataFrame
        Updated confound DataFrame with CSF column appended.

    Notes
    -----
    - The function assumes row alignment between the fMRIPrep confound file and CSF regressor.

    '''
    import pandas as pd
    import os
    
    if not os.path.exists(confound_file_path):
        raise FileNotFoundError(f"Confound file not found: {confound_file_path}")
    
    local_csf_timeseries_df = pd.read_csv(local_csf_ts_path) # Load the CSF time series DataFrame

    csf_column_name = f"{roi}_local_csf"
    if csf_column_name not in local_csf_timeseries_df.columns:
        raise ValueError(f"CSF column '{csf_column_name}' not found in input DataFrame.")
    
    conf_df = pd.read_csv(confound_file_path, sep='\t')     # Subject-specific confound file 
    if len(conf_df) != len(local_csf_timeseries_df): 
        raise ValueError("Length (TR) mismatch between confound file and CSF time series.")

    # Append the local CSF column to the confound dataframe
    # ------------------------------------------------------
    conf_df[csf_column_name] = local_csf_timeseries_df[csf_column_name]
    modified_conf_df = conf_df.copy()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        modified_conf_df.to_csv(save_path, sep='\t', index=False)
        if verbose:
            print(f"Modified confound file saved to: {save_path}")

    return modified_conf_df