import os

import nibabel as nb
import numpy as np

from nilearn.image import resample_img
import nipype.interfaces.matlab as matlab
from nipype.interfaces import spm
from pypreprocess.io_utils import compute_output_voxel_size
import joblib as gaelos
from nipype.caching import Memory

root_dir = '/home/vivi/vivi/retraite/ds101_dartel'
root_dir = '/storage/workspace/yschwart/dartel_vs_newsegment/ds101_dartel'
root_dir = '/home/ys218403/Data/dartel_vs_newsegment/ds101_dartel'

spm_dir = os.environ['SPM_DIR']
matlab_cmd = '%s run script' % os.environ['SPM_MCR']
spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_cmd, use_mcr=True)
matlab.MatlabCommand.set_default_paths(spm_dir)

dartelnorm2mni = spm.DARTELNorm2MNI().run
createwarped = spm.CreateWarped().run

func = [
    '%s/sub011/cache_dir/nipype_mem/nipype-interfaces-spm-preprocess-Coregister/8654d3bc4ab17cc25ebe615130929ef9/rbold.nii' % root_dir,
    '%s/sub011/cache_dir/nipype_mem/nipype-interfaces-spm-preprocess-Coregister/8654d3bc4ab17cc25ebe615130929ef9/rbold_c0000.nii' % root_dir]
ref_func = '/home/ys218403/Data/dartel_vs_newsegment/ds101_dartel/sub011/task001_run001/bold.nii.gz'
flow_fields = '%s/sub021/cache_dir/nipype_mem/nipype-interfaces-spm-preprocess-DARTEL/01577a0cd4650a2bae6a429689995f03/u_rc1highres001_brain_c0009_Template.nii' % root_dir

template_file = '%s/sub021/cache_dir/nipype_mem/nipype-interfaces-spm-preprocess-DARTEL/01577a0cd4650a2bae6a429689995f03/Template_6.nii' % root_dir
anat_file = '/%s/sub011/highres001_brain.nii' % root_dir

# func_write_voxel_sizes = (3, 3, 4)

# func_write_voxel_sizes = compute_output_voxel_size(
#     func, func_write_voxel_sizes)

anat_niimg = nb.load(anat_file)

resampled_func = []

gaelmem = gaelos.Memory('/home/ys218403/Data/cache')

for func_file in func:
    name = os.path.split(func_file)[1]
    func_data = nb.load(func_file).get_data()[..., :2]
    img = nb.Nifti1Image(func_data, affine=nb.load(func_file).get_affine())
    img.to_filename('/home/ys218403/Data/dartel_cache/sub_%s' % name)
    func_file = '/home/ys218403/Data/dartel_cache/sub_%s' % name
    func_niimg = gaelmem.cache(resample_img)(
        nb.load(func_file),
        target_affine=anat_niimg.get_affine(),
        target_shape=anat_niimg.shape)
    func_niimg.to_filename(
        '/home/ys218403/Data/dartel_cache/oversampled_%s' % name)
    resampled_func.append(
        '/home/ys218403/Data/dartel_cache/oversampled_%s' % name)

print resampled_func

cache_dir = "/home/ys218403/Data/dartel_cache"
if not os.path.exists(cache_dir): os.makedirs(cache_dir)
mem = Memory(cache_dir)

tricky_kwargs = {}

dartelnorm2mni_result = mem.cache(spm.DARTELNorm2MNI)(
    apply_to_files=resampled_func[:1],
    flowfield_files=[flow_fields],
    template_file=template_file,
    ignore_exception=False,
    modulate=False,  # don't modulate
    fwhm=0.,  # don't smooth
    **tricky_kwargs)

normalized_func = dartelnorm2mni_result.outputs.normalized_files

# createwarped_result = mem.cache(spm.CreateWarped)(
#     image_files=resampled_func[:1],
#     flowfield_files=[flow_fields],
#     ignore_exception=False)

# warped_func = createwarped_result.outputs.warped_files

# ref_func = nb.load(ref_func)
# for func_file in warped_func:
#     data = nb.load(func_file).get_data()
#     data[np.isnan(data)] = 0
#     func_niimg = nb.Nifti1Image(data, affine=nb.load(func_file).get_affine())

#     name = os.path.split(func_file)[1].split('oversampled')[1]
#     func_niimg = gaelmem.cache(resample_img)(
#         func_niimg,
#         target_affine=ref_func.get_affine(),
#         target_shape=ref_func.shape[:-1])
#     func_niimg.to_filename(
#         '/home/ys218403/Data/dartel_cache/downsampled_%s' % name)


