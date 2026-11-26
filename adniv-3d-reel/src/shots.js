// Shot programs for the style frames. Each returns {sc, state(sc)}; the HUD state is a pure function of time.
export function makeShots(E) {
  const {get} = E;
  const street = (look, t, p, st) => { const sc = get('street', look); sc.update(t, p); return {sc, state: () => st}; };
  const labelsFor = (sc, t) => {
    const m = sc.project('module'), d = sc.project('driver');
    return [{x: m[0], y: m[1], lx: 585, ly: m[1] + 30, text: 'LED MODULE', n: '01', p: E.clamp((t - 1.2) / 0.6)},
            {x: d[0], y: d[1], lx: 585, ly: d[1] - 10, text: 'LED DRIVER', n: '02', p: E.clamp((t - 1.5) / 0.6)}];
  };
  return {
    still_s1: (look, t) => street(look, 1.6, {sFixed: 0, camT: 1.6},
      {t: 2.4, chip: 'SODIUM LAMP · PEELI ROSHNI', head: {lines: ['Woh *Peeli*', 'Roshni...'], t0: 0.2, y: 392}, cap: {t: 1.3}, logoOp: 1}),
    still_s2: (look, t) => street(look, 3.0, {sFixed: 1, camT: 2.8},
      {t: 2.4, chip: 'LED · SAFED ROSHNI', head: {lines: ['Ab Har Gali', '*Safed*'], t0: 0.2, y: 392}, cap: {t: 4.9}, logoOp: 1}),
    still_s8: (look, t) => { const sc = get('inside', look); sc.update(2.0, {explode: 1, orbit: 0.38, on: 1});
      return {sc, state: s => ({t: 2.6, chip: 'INSIDE · LED MODULE + DRIVER', head: {lines: ['Light Ke', '*Andar* Kya?'], t0: 0.2, y: 392}, cap: {t: 33.6}, labels: labelsFor(s, 2.6), logoOp: 1})}; },
    still_cta: (look, t) => { const sc = get('cta', look); sc.update(3, {}); return {sc, state: () => ({t: 3.6, logo: false, cta: {t: 3.6}})}; },
    flip_test: (look, t) => {
      const vo = 3.0 + t; const flipT0 = 1.69;
      const chip = t < flipT0 + 0.15 ? 'SODIUM LAMP · PEELI ROSHNI' : 'LED · SAFED ROSHNI';
      return street(look, t, {camT: t + 0.5, flipT0}, {t: t, chip, chipT0: 0, head: {lines: ['Ab Har Gali', '*Safed*'], t0: 0.72, y: 392}, cap: {t: vo, hold: true}, logoOp: 1,
        flash: Math.max(0, 0.22 * Math.exp(-Math.pow((t - flipT0 - 0.05) / 0.06, 2)))});
    },
  };
}
