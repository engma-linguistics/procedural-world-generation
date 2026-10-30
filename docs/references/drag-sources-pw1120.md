# Land-sea drag sources for PW-1120 option (i)
All fetched 2026-10-30 by direct download (HTTP 200, PDF text extracted); local copies in scratchpad/dl/.

1. ECMWF IFS Documentation CY49R1, Part IV Physical Processes (Nov 2024). https://www.ecmwf.int/sites/default/files/elibrary/112024/81626-ifs-documentation-cy49r1-part-iv-physical-processes.pdf
   Open, no login. Table 8.3 (printed p.156): z0m land by cover: crops 0.25 m, short grass 0.1, tall grass 0.5, tundra 0.03, desert 0.013, shrubs 0.1-0.5, forests 1.1-2.0, glaciers 1.3e-3. Sec 3.2.4 (~p.50): over sea z0M = 0.11 nu/u* + alpha_Ch u*^2/g, Charnock alpha_Ch = 0.018 if no wave model; nu = 1.5e-5. Ch 8 text: land values were raised to remove a 10-m wind overestimate. Note z0 in metres.
2. Bretherton, Atm S 547 Boundary Layer Meteorology, lecture 6 (Univ. Washington; hosted at Utah). https://www.inscc.utah.edu/~krueger/6220/lect6-Turbulent_Ekman_Layer.pdf
   Open. pp. 6.7-6.10: neutral Ekman layer, u*/G = F(Ros), typical 0.01-0.1; Ros = G/(f z0) ~ 1e4-1e8; turning angle ~ asin(5 u*/G) (eq 6.32); example u*/G=0.053 gives ~15 deg and surface-layer-top wind 0.7G; smoother (ocean) gives smaller angle, rougher larger; BL depth 0.8 u*/f (eq 6.26). Gives the mechanism, not a land vs sea table.
3. Lecture chapter "13. Fundamental Forces" (pp. 68-71), Mustansiriyah Univ. https://uomustansiriyah.edu.iq/media/lectures/6/6_2021_05_01!12_29_02_PM.pdf
   Open. p.71: "typical values for the surface wind deflection are 15-30 deg over sea and 25-50 deg over land". The ratio values after it are garbled in text extraction (not verified). Author/book title not verified (file has none). Use as a quotable range only.
4. Karger & Bumke (1996), Spatial extension of coastal impact on the mean surface wind over the Baltic Sea, Eur. Union Wind Energy Conf., Goteborg. https://oceanrep.geomar.de/id/eprint/8127/1/Karger.pdf
   Open. Tables 1-2: ratio q of observed surface wind to geostrophic: 0.63 within 5 km of shore, 0.76 (10), 0.80 (15), 0.83 (20), 0.86 beyond 20 km (alongshore); onshore 0.74-0.86 and offshore 0.68-0.86 for open-sea coasts, 0.48-0.72 in semi-enclosed areas. Coastal impact reaches 50 km, most within 15-20 km. Mean ageostrophic angle 26.8 deg, eq (5) a = 24.9 + 1.8 dT (dT in +-3 K). C_DN open sea (1.11 +- 0.17)e-3 (5-12 m/s); within 10 km of coast (0.87+0.0673 U10)e-3. Page numbers are not marked in my extraction; Baltic only, sea side of coast only.
5. Edson (2008), Review of Air-Sea Transfer Processes, ECMWF Workshop slides. https://www.ecmwf.int/sites/default/files/elibrary/2008/15595-reciew-air-sea-transfer-processes.pdf
   Open. Slide ~7: Large & Pond (1981) 1e3 C_DN = 1.2 for 4-11 m/s, 0.49 + 0.065 U10N for 11-25 m/s. (Second-hand citation of L&P; the 1981 JPO paper itself not opened.)
6. Lindvall & Svensson, Wind turning in the boundary layer, obs vs CMIP5 (Stockholm U.). https://www.ecmwf.int/sites/default/files/elibrary/2016/16644-wind-turning-boundary-layer.pdf
   Open. Slides only; plots (turning angle vs wind speed, land sites and ocean) did not extract as text; the Cabauw ~32 deg point is on slide 3. Numbers on land vs ocean: not verified.

## Recommendation
Use (1) for land z0 (0.03-2 m) and the sea z0 formula; z0 ~ 1e-4 m at 10 m/s over sea gives C_DN ~1.2e-3 against land 5e-3 to 3e-2 (my arithmetic from kappa/ln(10/z0), not a quoted figure). Use (2) for the turning-angle and u*/G mechanism, and (3) for the land/sea angle ranges. (4) is the only one that quantifies the slowdown across a coast (q 0.63 to 0.86 over ~20 km); it is the sea side of a Baltic coast, so it supports a scale of ~20 km to 50 km for adjustment, not the land side.

## Manual download needed (not opened)
- Large & Pond (1981), J. Phys. Oceanogr. 11, 324-336 (AMS; open-access status not checked).
- Garratt, The Atmospheric Boundary Layer (CUP, book, paywalled); Stull, Intro to Boundary Layer Meteorology (book).
- Gap: no open source found for the land-side convergence/slowdown across a coastline.
