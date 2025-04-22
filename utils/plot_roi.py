def plot_roi_step(roi_path, template_path, title=None, cut_coords=(0, -34, -9), cmap='autumn', threshold=0.0, draw_cross=False, save_path=None):
    '''
    Plot an ROI mask over a template brain and optionally save the figure.
    '''

    from nilearn import plotting, image
    import matplotlib.pyplot as plt 
    import os
    
    # Load images
    roi_nii = image.load_img(roi_path)
    template_nii = image.load_img(template_path)

    # Set default title
    if title is None:
        title = f'ROI: {os.path.basename(roi_path)}'

    # Create plot
    display = plotting.plot_stat_map(
        roi_nii,
        bg_img=template_nii,
        title=title,
        display_mode='ortho',
        cut_coords=cut_coords,
        cmap=cmap,
        threshold=threshold,
        draw_cross=draw_cross
    )

    # Save if requested
    if save_path:
        display.savefig(save_path)
        print(f"Saved plot to {save_path}")

    plotting.show()