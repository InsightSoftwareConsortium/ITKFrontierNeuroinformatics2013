#!/bin/sh

# Run to create the submission.

dexy

out=output/submission
doc=output/doc
width=3000

mkdir -p $out
rm $out/*

cp output/doc/frontiers.pdf $out/ITKEnablingReproducibleResearchAndOpenScience.pdf

# EPS or covert to tiff?
cpconvert="convert -compress lzw -resize ${width}x"
epstiff=tiff

convert -resize ${width}x $doc/itk_module_dependency.png $out/figure_1_itk_module_dependency.tiff
convert -resize ${width}x $doc/itk_code_contribution.png $out/figure_2_itk_code_contribution.tiff
$cpconvert $doc/itk_git_contributors.eps $out/figure_3_itk_git_contributors.$epstiff
$cpconvert $doc/gerrit_patch_set_histogram.eps $out/figure_4_gerrit_patch_set_histogram.$epstiff
$cpconvert $doc/gerrit_fix_ups.eps $out/figure_5_gerrit_fix_ups.$epstiff
convert -resize ${width}x $doc/GerritGraphRender.png $out/figure_6_gerrit_graph_render.tiff
$cpconvert $doc/gerrit_closeness.eps $out/figure_7_gerrit_closeness.$epstiff
$cpconvert $doc/insight_journal_submissions.eps $out/figure_8_insight_journal_submissions.$epstiff
let w=$width/3
montage -compress lzw -geometry $wx$w $doc/colin_axial.png $doc/colin_sagittal.png $doc/colin_coronal.png $doc/atlas_axial.png $doc/atlas_sagittal.png $doc/atlas_coronal.png $doc/mask_axial.png $doc/mask_sagittal.png $doc/mask_coronal.png $out/figure_9_skull_strip_inputs.tiff
montage -geometry $wx$w $doc/output_axial.png $doc/output_sagittal.png $doc/output_coronal.png /tmp/lower.png
convert -compress lzw -resize ${width}x $doc/output_surface.png /tmp/lower.png $out/figure_10_skull_strip_outputs.tiff
rm /tmp/lower.png
