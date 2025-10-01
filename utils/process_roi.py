'''
Author: Alexandra Fischbach
Github repo: https://github.com/AlexFischbach/local_csf_pipeline/tree/main
Date: 04-18-2025
Contact: fischbach.a@northeastern.edu
'''


def initialize_roi_dict(
        roi_dir, subj
):
    '''
    Creates a dictionary of ROI NifTI mask file paths. 
    Key value corresponds to ROIs name (e.g., 'R_amygdala')

    Input Parameters
    ----------------
    roi_dir : str
        Root directory where ROI NifTI files are stored.
        (e.g., 'your/path/MNI_9cAsym_atlases/local_csf_pipeline_ROIs')
    
    subj : str
        Subject ID string in BIDS-style format.
        (e.g., 'sub-011')
    
    
    Returns
    -------
    roi_files : dict
        Dictionary where each key is an ROI name and the value is a list 
        containing the full path to the corresponding NIfTI file.
        
        Example:
        {
            'amygdala': ['/path/to/harvard_oxford/amygdala.nii.gz'],
            'brainstemNav_PAG': ['/path/to/brainstemNav/PAG_prob.nii.gz'],
            'sub_PAG_across_runs': ['/path/to/sub_PAG_across_runs/rest/sub-001/sub-001_pag_mask_averaged_all-runs.nii.gz']
        }

    '''
    import os

    roi_files = {}
    
    # Harvard-Oxford
    hosa_dir = os.path.join(roi_dir, 'harvard_oxford')
    for roi in os.listdir(hosa_dir):
        if roi.endswith('.nii.gz'):
            name = roi.replace('.nii.gz', '') #Removes .nii.gz extension to use as dictionary key (e.g., R_amygdala)
            roi_files[name] = [os.path.join(hosa_dir, roi)]

    # Brainstem Navigator (group-pag)
    bsn_path = os.path.join(roi_dir, 'brainstemNav', 'PAG_prob.nii.gz')
    if os.path.exists(bsn_path):
        roi_files['brainstemNav_PAG'] = [bsn_path]

    # Subject-specific PAGs
    sub_pag_path = os.path.join(roi_dir, 'sub_PAG_across_runs', 'rest', subj, f'{subj}_pag_mask_averaged_all-runs.nii.gz')
    if os.path.exists(sub_pag_path):
        roi_files['sub_PAG_across_runs'] = [sub_pag_path]

    return roi_files

def process_roi_mask(
    roi_path,
    template_path,
    save_path=None,
    verbose=True
):
    '''
    Author: Alexandra Fischbach
    Date: 2023-10-04
    
    Loads a gray matter (GM) ROI mask and resamples it to match a reference space (e.g., MNI template),
    if needed. Returns both the resampled NIfTI image and its NumPy array

    Input Parameters
    ----------------
    roi_path : str
        Full path to the input GM ROI mask NIfTI file (can be binary or probabilistic).
        (e.g., '/your/path/R_amygdala.nii.gz')
    
    template_path : str, optional 
        Full path to 3-dimensional coordinate space  NIfTI file (e.g., MNI152 template). 
        (e.g., '/your/path/mni_icbm152_t1_tal_nlin_asym_09c.nii.gz')

    verbose : bool, optional
        Whether to print status messages. Default is True.
    
    Returns
    -------
    processed_roi_nii : nibabel.Nifti1Image
        Resampled GM ROI image object.

    processed_roi_np : numpy.ndarray
        Resampled GM ROI image as a NumPy array.

    Notes
    -----
    - Resampling is only performed if the shape of the ROI does not match the template.
    - Interpolation method is determined automatically:
        * 'nearest' for binary masks
        * 'linear' for probabilistic masks

    '''
    import os
    import numpy as np 
    import nibabel as nib  
    from nilearn.image import resample_img 

    if not os.path.exists(roi_path):
        raise FileNotFoundError(f"ROI path not found: {roi_path}")
    
    roi_nii = nib.load(roi_path) 
    if verbose:
        print(f"Loading ROI image from: {roi_path}\n")
    roi_np = roi_nii.get_fdata()
    
    if template_path:
        if verbose:
            print(f"Loading template image from: {template_path}\n")
        template_nii = nib.load(template_path) # e.g., MNI152 template

        # Resample the ROI mask if shape doesn't match template
        # -----------------------------------------------------
        if roi_nii.shape != template_nii.shape:
            if verbose: 
                print(f"Resampling ROI to match template shape: {template_nii.shape}.")
            is_binary = np.all(np.logical_or(roi_np == 0, roi_np == 1)) # Determine if ROI is binary or probabilistic to set interpolation method
            interp_method = 'nearest' if is_binary else 'linear'
            processed_roi_nii = resample_img(                           # Resample the ROI image to the template's space
                roi_nii, 
                target_affine=template_nii.affine, 
                target_shape=template_nii.shape[:3],    
                interpolation=interp_method
            )

            if processed_roi_nii.shape != template_nii.shape:  # Confirm resampling was successful
                raise ValueError(f"Resampling failed. ROI shape {processed_roi_nii.shape} does not match template shape {template_nii.shape}.")
        else:
            if verbose:                                                  
                print("ROI mask already matches template space. No resampling applied.")  # If already aligned, keep original ROI image and data 
            processed_roi_nii = roi_nii
           
    else:
        processed_roi_nii = roi_nii
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        nib.save(processed_roi_nii, save_path)

        if verbose:
            print(f"Processed ROI mask saved to: {save_path}\n")
       
    return processed_roi_nii

def threshold_roi_mask(
        proc_roi_path,
        roi_threshold=0.3,
        save_path=None,
        verbose=True
):
    '''
    Thresholdes (binarizes) a probabilistic GM ROI mask if needed.

    Input Parameters
    ----------------
    proc_roi_path : str
        Full path to the processed ROI mask.
        (e.g., 'your/path/R_amygdala_mask_proc.nii.gz')
       

    roi_threshold : float, optional
        Threshold for binarizing probabilistic masks. Values ≥ threshold are set to 1, else 0.
        Default is 0.3. If the array has values in [0, 100], the threshold is scaled automatically.
    
    save_path : str, optional
        Full path to save the thresholded binary mask as a NIfTI file.
        If None, the file is not saved.

    verbose : bool, optional
        If True, prints status messages. Default is True.
    
    Returns
    -------
    binary_roi_nii : nibabel.Nifti1Image
        Binary mask as a NIfTI image with original affine and header.
    
    Notes
    -----
    - If the ROI mask is already binary (i.e., contains only 0 and 1), thresholding is skipped.
    '''
    import os
    import numpy as np
    import nibabel as nib
    
    if proc_roi_path is None:
        raise ValueError("Input ROI path is None.")
    if roi_threshold < 0 or roi_threshold > 1:
        raise ValueError("Threshold value must be between 0 and 1.")

    processed_roi_nii = nib.load(proc_roi_path) 
    processed_roi_np = processed_roi_nii.get_fdata() 
        
    # Determine whether thresholding is necessary for ROI mask 
    # --------------------------------------------------------
    is_binary = np.all(np.logical_or(processed_roi_np == 0, processed_roi_np == 1))
    if is_binary:
        if verbose:
            print("ROI mask is already binary. No thresholding applied.")
        binary_roi_np = processed_roi_np.copy()
    else:
        if verbose: 
            print("ROI mask is probabilistic. Thresholding to binary mask...")
        roi_max_val = np.max(processed_roi_np)    # Maximum value within the ROI 
        if roi_max_val > 1.1:                     # Check if the maximum value is greater than 1.1 to determine scaling
            if verbose:
                print(f"Detected range [0–100]. Scaled threshold to {roi_threshold}.")
            roi_threshold *= 100                  # Scale threshold if values are in [0, 100] range
        else:
            if verbose:
                print(f"Values are within the expected [0, 1] range. Using threshold: {roi_threshold}.")
        binary_roi_np = np.where(processed_roi_np >= roi_threshold, 1, 0)  # Apply threshold: values above threshold become 1, else 0

    # Create binary ROI NIfTI image
    # -----------------------------
    binary_roi_nii = nib.Nifti1Image(
        binary_roi_np.astype(np.uint8), 
        affine=processed_roi_nii.affine,
        header=processed_roi_nii.header)
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        nib.save(binary_roi_nii, save_path)
        if verbose:
            print(f"Saved thresholded mask to {save_path}")

    return binary_roi_nii

def dilate_binary_roi_mask(
    threshold_roi_path, 
    iterations=4,
    save_path=None,
    verbose=True,
):
    '''
    Applies binary dilation to a binarized ROI mask and saves the result as a NIfTI image.

    Input Parameters
    ----------------
    threshold_roi_path : str
        Full path to the input binary ROI mask (NIfTI format). Values must be 0 or 1.
        (e.g, '/your/output/PAG_mask_binary.nii.gz')

  
    iterations : int, optional
        Number of iterations for binary dilation. Each iteration expands the ROI outward by 
        one voxel in all directions. Default is 4.
    
    save_path : str, optional
        Full path where the dilated binary mask will be saved.
        If None, the file is not saved.

    verbose : bool, optional
        If True, prints status messages. Default is True.
    
    Returns
    -------
    dilated_roi_nii : nibabel.Nifti1Image
        The dilated binary ROI mask as a NIfTI image.
        
    Notes
    -----
    - Binary dilation is an operation that expands the region of interest (ROI) mask 
      by adding neighboring voxels to the binary mask.

    '''
    import os
    import numpy as np
    import nibabel as nib 
    from scipy.ndimage import binary_dilation # For binary dilation

    if threshold_roi_path is None:
        raise ValueError("Input binary mask path is None.")
    binary_roi_nii = nib.load(threshold_roi_path) 
    binary_roi_np = binary_roi_nii.get_fdata()
    
    # Validate the input (ROI mask) is binary
    # ----------------------------------------
    is_binary = np.all(np.logical_or(binary_roi_np == 0, binary_roi_np == 1))
    if not is_binary:
        raise ValueError("Input mask must be binary.")

   # Apply binary dilation 
   # ---------------------
    dilated_roi_np = binary_dilation(binary_roi_np, iterations=iterations)  
    dilated_roi_nii = nib.Nifti1Image(dilated_roi_np.astype(np.uint8), 
                                    binary_roi_nii.affine, 
                                    binary_roi_nii.header)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        nib.save(dilated_roi_nii, save_path)
        if verbose:
            print(f"Dilated mask saved to: {save_path}\n")

    return dilated_roi_nii
