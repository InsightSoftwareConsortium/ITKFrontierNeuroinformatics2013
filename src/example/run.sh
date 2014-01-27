#!/bin/sh

set -x
pushd ../../data
unzip -qq mni_colin27_1998_minc2.zip
popd

patient_image=../../data/colin27_t1_tal_lin.mnc
atlas_image=../../data/atlasImage.mha
atlas_mask_image=../../data/atlasMask.mha
chmod +x ./build/StripSkull
./build/StripSkull $patient_image $atlas_image $atlas_mask_image
