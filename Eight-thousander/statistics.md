# Column Statistics

| Directory   |   Total Columns |   Table Numbers |
|:------------|----------------:|----------------:|
| et          |               7 |               1 |
| de          |              14 |               1 |
| zh          |              12 |               1 |
| it          |              14 |               1 |
| nl          |               6 |               1 |
| en          |              13 |               2 |

# Model statistics

=== Using model: mT5-small ===
          et        de        zh        it        nl        en
et  1.000000  0.654533  0.533329  0.469724  0.746122  0.305862
de  0.654533  1.000000  0.723481  0.675615  0.830534  0.535959
zh  0.533329  0.723481  1.000000  0.739264  0.610165  0.693063
it  0.469724  0.675615  0.739264  1.000000  0.559181  0.735294
nl  0.746122  0.830534  0.610165  0.559181  1.000000  0.400599
en  0.305862  0.535959  0.693063  0.735294  0.400599  1.000000

=== Using model: XLM-R ===
          et        de        zh        it        nl        en
et  1.000000  0.818677  0.689062  0.749039  0.762848  0.534423
de  0.818677  1.000000  0.798003  0.827431  0.942281  0.722034
zh  0.689062  0.798003  1.000000  0.825682  0.813162  0.701197
it  0.749039  0.827431  0.825682  1.000000  0.797044  0.756496
nl  0.762848  0.942281  0.813162  0.797044  1.000000  0.690338
en  0.534423  0.722034  0.701197  0.756496  0.690338  1.000000

=== Using model: BLOOM ===
          et        de        zh        it        nl        en
et  1.000000  0.762815  0.594150  0.633407  0.745379  0.458558
de  0.762815  1.000000  0.764474  0.776810  0.929702  0.694411
zh  0.594150  0.764474  1.000000  0.808043  0.677324  0.786861
it  0.633407  0.776810  0.808043  1.000000  0.696742  0.756511
nl  0.745379  0.929702  0.677324  0.696742  1.000000  0.640004
en  0.458558  0.694411  0.786861  0.756511  0.640004  1.000000

Under XLM-R, de (German) and nl (Dutch) have very high similarity (0.94), meaning they likely share similar table structure/column content.

et (Estonian) and en (English) show lower similarity (0.53 in XLM-R), indicating more divergence.

This suggests that:

Language proximity and cultural context influence how tables are structured.

English (globalized) and Estonian (more localized) versions might prioritize different data fields.

