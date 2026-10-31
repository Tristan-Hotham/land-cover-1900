# Reddit post

**Subreddit:** r/dataisbeautiful

**Title:** [OC] In 1900 farms covered 19% of the world's ice-free land. Today they cover 37%: cropland and grazing land, 1900 vs 2023

**Image:** `world_farmland_1900_2023.png`

**Body:**

Two maps from HYDE 3.3, the historical land use reconstruction from Utrecht University, showing the share of every 9 km square used for crops or grazing in 1900 and in 2023.

- Farmland grew by 23.5 million km², 2.6 times the area of the US. Most of it is grazing on natural rangeland.
- The frontier moved into the tropics and drylands: the Brazilian Cerrado went from 3% farmed to 41%, the Sahel from 26% to 64%.
- Europe is the only region with less farmland than in 1900, and in the eastern US much of the old farmland grew back to woods.

The 1900 map is a model built from historical statistics, so trust the big picture more than single squares. Interactive swipe map (cropland, grazing, forest zone, anthromes, 2019 satellite land cover): https://maps.tristanhotham.com/land-cover-1900/

**Source comment:**

Data: HYDE 3.3 baseline (Klein Goldewijk et al., Utrecht University, CC BY 4.0, doi:10.24416/UU01-94FNH0) for 1900 and 2023 at 5 arc-minutes; world series 1700 to 2016 from HYDE 3.2 via Our World in Data; outlines Natural Earth. Farmland = cropland + pasture + rangeland + converted rangeland; ice-free land excludes Antarctica and the Greenland ice sheet. Tools: Python (numpy, rasterio, matplotlib), Equal Earth projection. Paper, data and code: https://maps.tristanhotham.com/land-cover-1900/
