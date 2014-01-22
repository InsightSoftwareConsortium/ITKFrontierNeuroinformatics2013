#!/bin/sh

fixed_image=../../data/Sim_074_T2.mha
moving_image=../../data/Sim_094_T2.mha
chmod +x ./build/Registration
./build/Registration $fixed_image $moving_image
