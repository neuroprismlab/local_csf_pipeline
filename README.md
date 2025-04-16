# Local CSF Correction Pipeline for fMRI

A modular pipeline for correcting CSF-related artifacts in subcortical fMRI to improve signal sensitivity and reduce physiological confounds in ultra-high field (7T) imaging.


![Pipeline diagram](images/pipeline_summary.png)

---
## Purpose

Subcortical regions are vulnerable to noise due to low signal-to-noise ratio (SNR), small size, and proximity to CSF [1, 2]. Standard CSF correction averages signals across anatomically distinct CSF compartments, which can miss region-specific noise and reduce sensitivity.

To overcome these challenges, this pipeline introduces a localized CSF correction strategy that is region-specific, extracting and modeling CSF signals found directly adjacent to each subcortical ROI.

> For an overview of initial findings and methodological validation, see [supporting material](images/CNS_poster_2025.jpeg).


---
## Repository Structure
```
local_csf_pipeline/
├── pipeline.py             # Main script to run the full pipeline
├── config.py               # Paths, constants, and default variables
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and usage
└── utils/                  # Utility functions grouped by functionality
    ├── __init__.py
    ├── process_roi.py      # ROI loading, resampling, thresholding, dilation
    ├── extract_csf.py      # Local CSF mask extraction and time series
    └── func_timeseries.py  # Functional time series extraction and regression
```
--- 
## Input Requirements
This pipeline is designed to be used with preprocessed fMRI data (e.g., from [fMRIPrep](https://fmriprep.org/)).

To run the pipeline, you will need the following inputs:

- **Preprocessed BOLD images** (NifTI)
    > `sub-001_task-rest_run-01_bold_space-MNI152NLin2009cAsym_preproc.nii.gz`

- **Confound files** (TSV) 
    > `sub-001_task-rest_run-01_bold_confounds.tsv`

- **CSF probability tissue masks** (NifTI)
    > `sub-001_T1w_space-MNI152NLin2009cAsym_class-CSF_probtissue.nii.gz`

- **MNI template** (NifTI)
    > `mni_icbm152_t1_tal_nlin_asym_09c.nii.gz`

- **ROI masks**
  >(e.g., [Harvard-Oxford Atlas](https://nilearn.github.io/dev/modules/description/harvard_oxford.html/))
---
## Configuration 
Edit `config.py` to customize:
- `SUBJECT_ID`: Subject ID from the `SUBJ` environment variable  
- `BASE_DIR`, `DATA_DIR`, `ROI_DIR`, `OUTPUT_DIR`: Path configuration  
- `TEMPLATE_PATH`: MNI template for ROI resampling
- `DEFAULT_ROIS`: ROIs to include in the pipeline  
- `DEFAULT_REST_RUNS` *(optional)*: List of run labels (e.g., `'run-01'`)
- `CONDITION` *(optional)*: Scan label (e.g., `'rest'`)  
- `DEFAULT_MOTION_CONFOUNDS` *(optional)*: Motion regressors used in nuisance regression
---
## Modules Overview
Each step in the pipeline is handled by a modular function located in the `/utils` folder.

### ROI Processing (`process_roi.py`)
- `initialize_roi_dict` – Creates a dictionary of available ROIs
- `process_roi_mask` – Loads and resamples ROIs to MNI space
- `threshold_roi_mask` – Binarizes probabilistic ROI masks
- `dilate_binary_roi_mask` – Expands binary ROIs outward to define a local search region

### CSF Extraction (`extract_csf.py`)
- `extract_local_csf_mask` – Identifies CSF voxels within the dilated mask but outside the gray matter ROI
- `extract_local_csf_time_series` – Extracts average local CSF time series from the functional image
- `add_local_csf_time_series_to_confound_file` – Appends local CSF regressors to fMRIPrep confounds

### Time Series Correction (`func_timeseries.py`)
- `compute_functional_timeseries` – Applies nuisance regression and returns cleaned functional signals

> See the example notebook `example_pipeline_demo.ipynb` for a step-by-step walkthrough.
---
## Output Directory Structure
Each subfolder corresponds to a step in the pipeline.
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
The pipeline requires the following Python packages (see `requirements.txt`):

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
## Data Notes
> *Note: The pipeline was developed and tested on preprocessed 7T fMRI data acquired at* **1.1 mm isotropic resolution** *with a* **TR of 2.34 seconds** *.*
> For details on the MRI acquisition protocol, see [Fischbach et al., 2024](https://www.jneurosci.org/content/44/26/e1757232024/tab-article-info).

While the code is resolution-independent, results may vary depending on voxel size and temporal resolution.

---
## About 
This pipeline was developed by Alexandra Fischbach.

For questions, feedback, or collaboration inquiries: 📧 fischbach.a@northeastern.edu

---
## References 
[1] Brooks, J. C. W. P., Faull, O. K., Pattinson, K. T. S. Dp. F., & Jenkinson, M. P. (2013). Physiological Noise in Brainstem fMRI. Frontiers in Human Neuroscience, 7. https://doi.org/10.3389/fnhum.2013.00623

[2] Sclocco, R., Beissner, F., Bianciardi, M., Polimeni, J. R., & Napadow, V. (2018). Challenges and opportunities for brainstem neuroimaging with ultrahigh field MRI. NeuroImage, 168, 412–426. https://doi.org/10.1016/j.neuroimage.2017.02.052

## Citation 
---
If you use this pipeline in your work, please cite:

Fischbach, A.K., Noble, S. (2025). *Local CSF Correction Pipeline for fMRI* [Computer software]. GitHub. https://github.com/AlexFischbach/local_csf_pipeline. Retrieved *[Month Day, Year]*.
> Replace *[Month Day, Year]* with the date you accessed the repository.

---
## License 
This project is licensed under the terms of the MIT License. This means you can freely use, modify, and distribute the code, as long as you provide attribution to the original authors and source.


