# Adniv "Peeli Light Kahan Gayi?" 3D reel: QA report

File: `adniv_peeli_light_3d_reel.mp4`, H.264 High, 1080x1920, 30 fps, about 8 Mbps, bt709, AAC 48 kHz stereo, 53.6 s. Look: B (Realistic Night) for the street, sodium, city and split scenes; C (Studio Product-Viz) for the inside, Adniv and end screens. Website on the end screen: www.adniv.in (as confirmed).

| Check | Result |
|---|---|
| Frame at every beat and transition | `qa_frames_every_beat.jpg` (36 frames) and `qa_frames_every_transition.jpg` (8 cuts x 4 frames), all viewed |
| Safe zone x64-1016, y230-1500, icon column x>940 / y1000-1500 | Every HUD element (chip, logo, headline, caption, label, source chip, pills, callouts, end-screen items) measured at 0.4 s steps, 3,112 checks, 0 violations. Extremes: left 64, right 1016, top 244, bottom 1492. 3D number plate x66-1014, y669-989 |
| Safe-zone proof | `safezone_overlay_check.jpg` (12 frames) |
| Caption sync | 127 words aligned to vo.mp3 (speech recognition, snapped to measured speech onsets after pauses). 127/127 start on an energy rise or inside continuous speech. Eleven words that the recogniser missed or mis-timed were corrected by hand from the pause map: sab ek jaisa dikhta tha (12.57), Street Lighting National Programme (17.43-18.44), ek (19.96), hai... (27.30) |
| Triggers | flip on "safed" 4.69; colours drain on "sab ek jaisa" 12.57; city sweep on "2015" 15.40; counts start on crore 20.25, nau hazaar 24.70, 62 lakh 27.96; labels on LED module 33.44 and driver 34.56; light on at Adniv 36.38 |
| Spelling and numbers | On screen: 5 Jan 2015, Street Lighting National Programme, 1.34 Crore+, 9,001 MU+, 6.2 Mn Tonnes (62 lakh tonne), source chip SOURCE · PIB · 6 JAN 2025, LED Modules / LED Drivers / Lighting Solutions, 99108 13339, 93190 74766, www.adniv.in. The count-ups end exactly on the verified figures |
| Audio | Integrated -15.1 LUFS, LRA 4.1 LU, peak -3.0 dBFS (no clipping). Voiceover alone -14.5 LUFS. Music 19 dB under the voice, +3 dB on the end screen, fade-out over the last 2.6 s |
| Voiceover not cut off | vo.mp3 is 52.19 s; speech ends at 51.8 s; the video runs to 53.6 s, so the last word is followed by 1.4 s of music tail |
| Logo | Top-right on every scene, hidden on the end screen (large logo card there only) |

Notes
- adniv_logo.png was not in the upload; the Adniv logo supplied earlier (identical pixels to the file re-sent later) is used on a white rounded card.
- Count-up numbers are real 3D text (extruded, bevelled) drawn in a separate pass after the bloom so they stay crisp; they sit on a navy plate.
- Stylised or schematic by design: the street, city and street-light head are original models, not a real place or product.
- A faster pace on "Street lights lag" (22.7-23.1 s) is the voice itself; those three words share about 0.36 s.
