#!/bin/sh

set -x
pushd ../../data
unzip -qq mni_colin27_1998_nifti.zip
popd

input_id=colin27_t1_tal_lin

# inputs
patient_image=../../data/${input_id}.nii
atlas_image=../../data/atlasImage.mha
atlas_mask_image=../../data/atlasMask.mha

# outputs
patient_mask=../../data/${input_id}_mask.mha
masked_patient=../../data/${input_id}_masked.mha

chmod +x ./build/StripSkull
./build/StripSkull $patient_image $atlas_image $atlas_mask_image $patient_mask $masked_patient
