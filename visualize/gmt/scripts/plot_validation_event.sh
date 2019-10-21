CPT=red,purple,blue,chocolate,green4,darkred,cyan,black

gmt begin ../figures/validation_event pdf
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1

    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p
    gmt coast -JD115/30/30/40/7.0i -R50/180/-20/80 -G244/243/239 -S167/194/223 -Bxafg -Byafg #-Lg85/11+o-0.3c/0.0c+c11+w1000k+f+u+l'scale'
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

# the EARA2014 region

    gmt plot -W1p,blue  << EOF
>
117.915778257699 -16.6586412980043
57.4074304719772 10.0650870551211
>
57.4074304719772 10.0650870551211
54.0787269587550 75.5308108875256
>
54.0787269587550 75.5308108875256
165.126222399968 30.7867888632000
>
165.126222399968 30.7867888632000
117.915778257699 -16.6586412980043
EOF


# the FWEA18 region

    gmt plot -W1p,green  << EOF
>
89.4833259439912 7.22035292868921
77.6825212372205 64.8071481585122
>
77.6825212372205 64.8071481585122
164.566756581541 52.2373448567531
>
164.566756581541 52.2373448567531
132.466794941786 0.556612332658492
>
132.466794941786 0.556612332658492
89.4833259439912 7.22035292868921
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

    gmt meca  -Sd0.2c/0.05c -M -Cblack ../data/validation_event.txt

    # plate boundaries
    # gmt psxy -W1p,255/0/0 ../gmt_database/Plate_Boundaries/nuvel1_boundaries
    # gmt psxy ../gmt_database/japan_slab_contour -W0.7p -C../gmt_database/cpts/slab.cpt -V
gmt end
