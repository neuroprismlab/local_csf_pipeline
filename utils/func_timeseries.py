def compute_functional_timeseries(
    func_mask_path,
    binary_roi_path,
    mod_conf_path,
    roi_name,
    confound_vars="Default",
    save_path=None,
    verbose=True
):
    '''
    Input Parameters
    ----------------
    func_mask_path : str
        Full path to the 4D functional image (e.g., preprocessed BOLD image in MNI space).
        (e.g., 'sub-001_task-rest_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz')

    binary_roi_path : str
        Full path to the binary ROI mask (e.g., 'R_amygdala.nii.gz').

    save_path : str, optional
        If provided, saves the resulting time series as a CSV to this path.
    
    verbose : bool, optional
        Whether to print progress messages. Default is True.
    
    Returns
    -------
    
    '''

    import numpy as np 
    import os 
    import pandas as pd
    import nibabel as nib
    from nilearn.image import resample_img
    from nilearn.input_data import NiftiMasker # For masking and extracting time series
    from nilearn import signal                 # For cleaning time series data

    func_nii = nib.load(func_mask_path)                # Load the 4D functional image
    func_data_subset = func_nii.get_fdata() # Keep only first 3 timepoints
    func_nii = nib.Nifti1Image(func_data_subset, affine=func_nii.affine)

    binary_roi_nii = nib.load(binary_roi_path)         # Load the binary ROI mask

    # Resample ROI if shape doesnt match 
    if binary_roi_nii.shape != func_nii.shape[:3]:
        if verbose:
            print("Functional image and ROI mask shapes do not match.")
        binary_roi_nii = resample_img(binary_roi_nii,
            target_affine=func_nii.affine,
            target_shape=func_nii.shape[:3],
            interpolation='nearest'    # Nearest neighbor for binary mask
        )
    else:
        if verbose:
            print("Functional image and ROI mask shapes match. No resampling needed.")
    
    # Extract mean ROI time series
    masker = NiftiMasker(mask_img=binary_roi_nii)       # Masker object to apply the BOLD image
    func_nii_masked = masker.fit_transform(func_nii)    # Shape: (n_timepoints, n_voxels)
  
    conf_df = pd.read_csv(mod_conf_path, sep='\t')
   
    if confound_vars == "Default": 
        local_csf_col = f"{roi_name}_local_csf"
        motion_cols = ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']
        confound_vars =  motion_cols + [local_csf_col]
    if confound_vars is None:
        confound_matrix = None
    else:
        missing = [c for c in confound_vars if c not in conf_df.columns]
        if missing:
            raise ValueError(f"Missing confound variables in confound file: {missing}")

    confound_matrix = conf_df[confound_vars].values if confound_vars is not None else None

    corrected_ts_np = signal.clean(func_nii_masked, confounds=confound_matrix, standardize=False)

    # Average across voxels AFTER cleaning - seed analysis
    mean_corrected_ts_np = np.mean(corrected_ts_np, axis=1, keepdims=True)  # (TRs, 1)

    if save_path:
        corrected_ts_df = pd.DataFrame(mean_corrected_ts_np, columns=['mean_time_series'])
        corrected_ts_df.to_csv(save_path, index=False)
        if verbose:
            print(f"Corrected time series saved to: {save_path}")

    return corrected_ts_np, mean_corrected_ts_np