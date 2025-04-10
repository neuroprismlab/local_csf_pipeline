# local_csf_pipeline

Local CSF Extraction and Denoising Pipeline
-------------------------------------------
This repository contains a collection of modular Python scripts for identifying and extracting local cerebrospinal fluid (CSF) time series for use as nuisance regressors in fMRI preprocessing pipelines.

Overview:
---------
This pipeline runs on the outputs of fMRIPrep and assumes that your data is organized according to the BIDS specification. It utilizes well-known neuroimaging libraries, including:

NiBabel, Nilearn, NumPy, SciPy, Pandas

Motivation:
-----------
Subcortical regions are especially prone to distortion due to low signal-to-noise ratio, small anatomical volume, and proximity to CSF. Standard CSF correction methods pool signals across anatomically distinct CSF compartments, which may failt to capture the spatial heterogeneity of CSF-related noise, risking residual noise or signal loss in anatomically specific regions.

Contact:
--------
For questions, feedback, or collaboration inquiries:
📧 fischbach.a [at] northeastern.edu

Citation:
---------
If you use this pipeline in your work, please cite: XX

References:
-----------

Example: