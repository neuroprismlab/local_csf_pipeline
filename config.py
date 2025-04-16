import os

# Subject from environment variable
SUBJECT_ID = os.environ['SUBJ']
os.environ.get("SUBJ")

# Base directories
BASE_DIR = "/scratch"
DATA_DIR = os.path.join(BASE_DIR, "data")
ROI_DIR = os.path.join(BASE_DIR, "roi_masks")
TEMPLATE_DIR = os.path.join(BASE_DIR, "template")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# MNI template path
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "mni_icbm152_t1_tal_nlin_asym_09c.nii")

# ROIs and run settings
DEFAULT_REST_RUNS = ["run-01", "run-02", "run-03"]
DEFAULT_ROIS = [
    "R_pallidum", "L_pallidum", "R_hippocampus", "L_hippocampus",
    "R_thalamus", "L_thalamus", "R_putamen", "L_putamen",
    "R_caudate", "L_caudate", "R_amygdala", "L_amygdala",
    "R_accumbens", "L_accumbens", "brainstemNav_PAG", "sub_PAG_across_runs"
]
CONDITION = 'rest'

DEFAULT_MOTION_CONFOUNDS = ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ'] 