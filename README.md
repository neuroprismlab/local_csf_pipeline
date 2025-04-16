# Local CSF Correction Pipeline for fMRI

This pipeline performs local cerebrospinal fluid (CSF) artifact correction to improve subcortical fMRI signal quality. It includes steps for ROI preprocessing, CSF extraction, and nuisance regression — tailored for high-resolution (7T) fMRI data.

--- 
## Purpose
Subcortical regions are especially prone to distortion due to low signal-to-noise ratio, small anatomical volume, and proximity to CSF [1, 2]. Standard CSF correction methods pool signals across anatomically distinct CSF compartments, which may failt to capture the spatial heterogeneity of CSF-related noise, risking residual noise or signal loss in anatomically specific regions.

---
## Project Structure
```
local_csf_pipeline/
├── pipeline.py             # Main script to run the full pipeline
├── config.py               # Paths, constants, and default variables
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and usage
└── utils/                  # Utility functions grouped by functionality
    ├── __init__.py
    ├── roi_processing.py   # ROI loading, resampling, thresholding, dilation
    ├── csf.py              # Local CSF mask extraction and time series
    └── timeseries.py       # Functional time series extraction and regression
```
--- 
## Input requirements
This pipeline works on processed fMRI data (fMRIprep) only.

To run this pipeline, you will need:

- Preprocessed BOLD images (NifTI)
    'sub-001_task-rest_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'

- Confound files (TSV) 
    'sub-001_task-rest_run-01_bold_confounds.tsv'

- CSF probability tissue masks (NifTI)
    'sub-001_T1w_space-MNI152NLin2009cAsym_class-CSF_probtissue.nii.gz'

- MNI template (NifTI)
    'mni_icbm152_t1_tal_nlin_asym_09c.nii.gz'

- ROI masks (e.g., Harvard-Oxford Atlas)


---
## Configuration 
Edit `config.py` to customize:
- SUBJECT_ID: Subject ID read from environment variable (SUBJ)
- BASE_DIR, DATA_DIR, ROI_DIR, OUTPUT_DIR: Directory paths
- TEMPLATE_PATH: MNI template used for ROI resampling
- DEFAULT_REST_RUNS *(optional)*: List of run labels (e.g., ['run-01', 'run-02']) — adjust if your data has a different format
- DEFAULT_ROIS: List of subcortical ROIs to include in the pipeline
- CONDITION *(optional)*: Name of scan condition (e.g., 'rest')
- DEFAULT_MOTION_CONFOUNDS: Motion regressors to include in the nuisance regression step

---
## Modules overview
This pipeline is performed executing a sequence of operations, each of which corresponds to a function in the helper files.

Helper files (inside /utils) include:
- `process_roi.py` for all ROI-related operations
- `extract_csf.py` for local CSF mask and time series extraction
- `func_timeseries.py` for functional signal denoising

There are 8 available operations:
**ROI Processing**
- `initialize_roi_dict` – Creates a dictionary of available ROIs
- `process_roi_mask` – Loads and resamples ROIs to MNI space
- `threshold_roi_mask` – Binarizes probabilistic ROI masks
- `dilate_binary_roi_mask` – Expands binary ROIs outward to define a local search region

**CSF Extraction**
- `extract_local_csf_mask` – Identifies CSF voxels within the dilated mask but outside the gray matter ROI
- `extract_local_csf_time_series` – Extracts average local CSF time series from the functional image
- `add_local_csf_time_series_to_confound_file` – Appends local CSF regressors to fMRIPrep confounds

**Time Series Correction**
- `compute_functional_timeseries` – Applies nuisance regression and returns cleaned functional signals


The Jupyter Notebook `example_pipeline_demo.ipynb` provides a step-by-step example of how to run the local CSF correction pipeline using sample inputs.

---
## Output directory structure
```
output/
├── 1.proc_roi/         # Resampled ROI masks
├── 2.thresh_roi/       # Thresholded binary ROI masks
├── 3.dilated_roi/      # Dilated ROI masks
├── 4.local_csf_mask/   # Extracted local CSF masks
├── 5.local_csf_ts/     # Local CSF time series
├── 6.mod_confounds/    # Confounds with CSF appended
└── 7.corrected_ts/     # Final denoised ROI time series
```

---
## Dependencies
Python packages listed in `requirements.txt`:

- `numpy==2.0.2`
- `pandas==2.2.3`
- `nibabel==5.3.2`
- `nilearn==0.10.4`
- `scipy==1.13.1`

To install the required packages:
```bash
pip install -r requirements.txt
```
---
## License 
This project is licensed under the terms of the MIT License. This means you can freely use, modify, and distribute the code, as long as you provide attribution to the original authors and source.

---
## References 
[1] Brooks, J. C. W. P., Faull, O. K., Pattinson, K. T. S. Dp. F., & Jenkinson, M. P. (2013). Physiological Noise in Brainstem fMRI. Frontiers in Human Neuroscience, 7. https://doi.org/10.3389/fnhum.2013.00623

[2] Sclocco, R., Beissner, F., Bianciardi, M., Polimeni, J. R., & Napadow, V. (2018). Challenges and opportunities for brainstem neuroimaging with ultrahigh field MRI. NeuroImage, 168, 412–426. https://doi.org/10.1016/j.neuroimage.2017.02.052

---
## About 
This pipeline was developed by Alexandra Fischbach.

For questions, feedback, or collaboration inquiries: 📧 fischbach.a [at] northeastern.edu

### Citation 
If you use this pipeline in your work, please cite:

Fischbach, A.K. (2025). *Local CSF Correction Pipeline for fMRI* [Computer software]. GitHub. https://github.com/AlexFischbach/local_csf_pipeline. Retrieved *[Month Day, Year]*.
> Replace *[Month Day, Year]* with the date you accessed the repository.
