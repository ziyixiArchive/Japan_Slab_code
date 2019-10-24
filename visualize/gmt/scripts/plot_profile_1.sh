CPT=red,purple,blue,chocolate,green4,darkred,cyan,black

gmt begin ../figures/profile_1 pdf
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1

    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p
    gmt coast -JD125/35/30/40/7.0i -R70/180/0/70 -G244/243/239 -S167/194/223 -Bxafg -Byafg #-Lg85/11+o-0.3c/0.0c+c11+w1000k+f+u+l'scale'
    gmt psxy -St0.08c -C$CPT ../data/2014_stations.txt

    # gmt colorbar -C$CPT -DjBR+w3c/0.2c+ml+o3.0c/0.0c -By+l"event count" -L -S
# the hybrid region
    gmt plot -W1p,red  << EOF
>
91.3320117152011 9.37366242174489
74.6060844556399 61.1396992149365
>
74.6060844556399 61.1396992149365
174.409435753150 48.6744705245903
>
174.409435753150 48.6744705245903
144.284491292185 2.08633373396527
>
144.284491292185 2.08633373396527
91.3320117152011 9.37366242174489
EOF

    gmt legend -DjBR+w1.0c+o3.5c/-0.5c << EOF
H 6 - Networks
S 0.05c t 0.05i red 0.5p 0.26c CEArray
S 0.05c t 0.05i purple 0.5p 0.26c F-net
S 0.05c t 0.05i blue 0.5p 0.26c KMA Network
S 0.05c t 0.05i chocolate 0.5p 0.26c Central Mongolia Seismic Experiment
S 0.05c t 0.05i green4 0.5p 0.26c NCISP7
S 0.05c t 0.05i darkred 0.5p 0.26c NECESSAray
S 0.05c t 0.05i cyan 0.5p 0.26c INDEPTH IV
S 0.05c t 0.05i black 0.5p 0.26c other Regional or Global Networks
EOF

    # gmt meca  -Sd0.6c/0.15c -M -Cblack ../data/validation_event.txt

    # plate boundaries
    # gmt psxy -W1p,255/0/0 ../gmt_database/Plate_Boundaries/nuvel1_boundaries
    # gmt psxy ../gmt_database/japan_slab_contour -W0.7p -C../gmt_database/cpts/slab.cpt -V


    gmt psxy -Sa0.3c -Gblack << EOF
140.0 36.4
EOF

    gmt plot -W0.01c,black << EOF
>
140 38.3
143 35.9
>
143 35.9
131 31.5
>
131 31.5
128 34.0
> 
128 34.0
140 38.3
EOF

    gmt plot -Wthin,magenta << EOF
148.63 38.56
124.95 30.7
EOF
gmt end
