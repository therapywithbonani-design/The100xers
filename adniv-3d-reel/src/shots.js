// Shot programs. 'reel' is the full B+C hybrid timeline in global voiceover time T (0 - 53.6 s).
export function makeShots(E) {
  const {get, clamp, sstep} = E;
  const eo3 = x => 1 - Math.pow(1 - clamp(x), 3);
  const street = (look, t, p, st) => { const sc = get('street', look); sc.update(t, p); return {sc, state: () => st}; };
  const labelsFor = (sc, t, t0m, t0d) => {
    const m = sc.project('module'), d = sc.project('driver');
    return [{x: m[0], y: m[1], lx: 585, ly: m[1] + 30, text: 'LED MODULE', n: '01', p: clamp((t - t0m) / 0.6)},
            {x: d[0], y: d[1], lx: 585, ly: d[1] - 10, text: 'LED DRIVER', n: '02', p: clamp((t - t0d) / 0.6)}];
  };
  const CUTS = [7.4, 14.2, 24.0, 27.65, 30.35, 41.35, 44.85];
  const flashAt = T => CUTS.reduce((f, b) => Math.max(f, Math.exp(-Math.pow((T - b) / 0.07, 2)) * (b === 44.85 ? 1 : 0.85)), 0);
  const comma = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const SRC = 'SOURCE · PIB · 6 JAN 2025';

  const reel = (look, T) => {
    const st = {t: T, cap: {t: T}, logoOp: 1, flash: flashAt(T)};
    let sc, post = null;
    if (T < 7.4) {                                            // 1-2: street, flip on "safed"
      sc = get('street', 'B'); sc.update(T, {camT: T + 0.5, flipT0: 4.69}); st.chipT0 = 0;
      st.chip = T < 4.78 ? 'SODIUM LAMP · PEELI ROSHNI' : 'LED · SAFED ROSHNI';
      st.head = T < 3.62 ? {lines: ['Woh *Peeli*', 'Roshni...'], t0: 0.25, y: 392, out: clamp((3.62 - T) / 0.18)} : {lines: ['Ab Har Gali', '*Safed*'], t0: 3.72, y: 392};
      st.flash = Math.max(st.flash, 0.22 * Math.exp(-Math.pow((T - 4.74) / 0.06, 2)));
    } else if (T < 14.2) {                                    // 3: sodium macro + colour ring
      sc = get('sodium', 'B'); sc.update(T - 7.4, {drain: sstep(12.57, 13.7, T)}); st.chip = 'SODIUM LAMP · EK JAISA RANG'; st.chipT0 = 7.4;
      st.head = T < 12.57 ? {lines: ['Woh *Sodium*', 'Lamp'], t0: 7.63, y: 392, out: clamp((12.57 - T) / 0.2)} : {lines: ['Sab Ek', '*Jaisa*'], t0: 12.6, y: 392};
    } else if (T < 24.0) {                                    // 4-5: aerial city, sweep on "2015", 1.34 Crore+
      sc = get('city', 'B'); const lt = T - 14.2; let num = null;
      if (T >= 20.1) { const v = 1.34 * eo3((T - 20.25) / 1.3); num = {text: v.toFixed(2) + ' Crore+', fit: '1.34 Crore+', a: clamp((T - 20.1) / 0.5)}; }
      sc.update(lt, {sweepT0: 15.4 - 14.2, num});
      if (T < 19.2) { st.chip = 'SLNP · 5 JAN 2015'; st.chipT0 = 14.2; st.head = {lines: ['5 *Jan* 2015'], t0: 14.5, y: 392, sub: {text: 'Street Lighting National Programme', t0: 17.0}}; }
      else { st.chip = 'SLNP · LED STREETLIGHTS'; st.chipT0 = 19.2; st.head = {lines: ['Kitni *LED*', 'Lights?'], t0: 19.4, y: 392};
        if (num) { st.label = {text: 'LED streetlights installed', t0: 20.5, y: 925}; st.src = {text: SRC, y: 1062, op: clamp((T - 20.6) / 0.4)}; } }
      if (T >= 15.4 && T < 15.5) st.flash = Math.max(st.flash, 0.25);
    } else if (T < 27.65) {                                   // 6: street (white), 9,001 MU+
      sc = get('street', 'B'); let num = null;
      if (T >= 24.55) { const v = 9001 * eo3((T - 24.7) / 1.6); num = {text: comma(v) + ' MU+', fit: '9,001 MU+', a: clamp((T - 24.55) / 0.5)}; }
      sc.update(T, {sFixed: 1, camT: (T - 24.0) + 3, num}); st.chip = 'SLNP · BIJLI KI BACHAT'; st.chipT0 = 24.0;
      st.head = {lines: ['Har Saal', '*Bijli* Ki Bachat'], t0: 24.15, y: 392};
      if (num) { st.label = {text: 'Million units bijli bachat / saal', t0: 25.3, y: 925}; st.src = {text: SRC, y: 1062, op: clamp((T - 25.4) / 0.4)}; }
    } else if (T < 30.35) {                                   // 7: street (white), 6.2 Mn Tonnes
      sc = get('street', 'B'); let num = null;
      if (T >= 27.8) { const v = 6.2 * eo3((T - 27.96) / 1.3); num = {text: v.toFixed(1) + ' Mn Tonnes', fit: '6.2 Mn Tonnes', a: clamp((T - 27.8) / 0.5)}; }
      sc.update(T, {sFixed: 1, camT: (T - 27.65) + 12, camX: 3.2, camLift: 2.2, num}); st.chip = 'SLNP · CO2 KAM'; st.chipT0 = 27.65;
      st.head = {lines: ['Aur *CO2*', 'Kam'], t0: 27.86, y: 392};
      if (num) { st.label = {text: 'CO2 kam / saal (62 lakh tonne)', t0: 28.5, y: 925}; st.src = {text: SRC, y: 1062, op: clamp((T - 28.6) / 0.4)}; }
    } else if (T < 35.25) {                                   // 8: inside the light - push in, exploded view, labels
      sc = get('inside', 'C'); const e = sstep(32.45, 33.55, T), lt = T - 30.35;
      sc.update(lt, {explode: e, on: 0.8, dist: 26 + 24 * (1 - sstep(30.35, 32.7, T)), orbit: -0.5 + 0.95 * sstep(30.35, 35.25, T)});
      st.chip = 'INSIDE · LED MODULE + DRIVER'; st.chipT0 = 30.35; st.head = {lines: ['Light Ke', '*Andar* Kya?'], t0: 30.6, y: 392};
      post = s => { st.labels = e > 0.9 ? labelsFor(s, T, 33.44, 34.56) : []; };
    } else if (T < 41.35) {                                   // 9: reassemble, light switches on, "Yahi Tech: Adniv"
      sc = get('inside', 'C'); const e = 1 - sstep(35.4, 36.3, T), on = 0.15 + 0.85 * sstep(36.36, 36.5, T);
      sc.update(T - 30.35, {explode: e, on, beam: sstep(36.38, 36.7, T), elev: 4.2 - 8.7 * sstep(35.9, 36.5, T), dist: 26 - 4 * sstep(36.3, 38, T), orbit: 0.45 - 0.5 * sstep(35.25, 41.35, T), lookY: 0.5 + 0.4 * sstep(36, 36.6, T)});
      st.chip = 'ADNIV · LED TECH'; st.chipT0 = 35.25; st.head = {lines: ['Yahi Tech:', '*Adniv*'], t0: 35.6, y: 392};
      st.pills = {y: 1262, items: [{text: 'LED Modules', t0: 37.69}, {text: 'LED Drivers', t0: 38.82}, {text: 'Lighting Solutions', t0: 39.95}]};
      st.flash = Math.max(st.flash, 0.4 * Math.exp(-Math.pow((T - 36.42) / 0.07, 2)));
    } else if (T < 44.85) {                                   // 10: split street, one side yellow, one white
      sc = get('street', 'B'); sc.update(T, {sSide: {L: 0, R: 1}, camT: (T - 41.35) + 20}); st.chip = 'PEELI YA SAFED?'; st.chipT0 = 41.35;
      st.head = {lines: ['Aapke *Sheher*', 'Mein?'], t0: 41.5, y: 392};
      st.pills = {y: 1262, items: [{text: 'Comment karo', t0: 43.68, o: true}]};
    } else {                                                  // 11: CTA on Adniv navy
      sc = get('cta', 'C'); sc.update(T - 44.85, {}); st.logo = false; st.cta = {t: T - 44.85};
    }
    return {sc, state: s => { if (post) post(s); return st; }};
  };

  return {
    reel,
    flip_test: (look, t) => reel(look, 3.0 + t),
    cover: (look, t) => { const sc = get('street', 'B'); sc.update(2.0, {sSide: {L: 0, R: 1}, camT: 19.5});
      return {sc, state: () => ({t: 3.0, logoY: 300, logoOp: 1, head: {lines: ['Peeli Light', '*Kahan* Gayi?'], t0: -1, y: 470, size: 150, sub: {text: 'Sodium se LED tak, poori kahani', t0: -1}},
        pills: {y: 1190, items: [{text: 'Sahi roshni, sahi partner', t0: -1, o: true}]}})}; },
  };
}
