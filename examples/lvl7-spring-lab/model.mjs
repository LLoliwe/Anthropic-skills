/** An ideal vertical Hookean spring at static equilibrium; not a safety-rated instrument. */
export const GRAVITY = 9.81; // m s^-2, defined educational approximation
export const K_N_PER_M = 400;
export function calculate(massGrams, k=K_N_PER_M) {
  if (!Number.isFinite(massGrams) || massGrams < 0 || massGrams > 2000) throw new RangeError('mass must be 0–2000 g');
  if (!Number.isFinite(k) || k <= 0) throw new RangeError('positive spring constant required');
  const massKg = massGrams / 1000;
  const forceN = massKg * GRAVITY;
  const extensionM = forceN / k;
  return Object.freeze({ massGrams, massKg, forceN, extensionM, extensionMm: extensionM * 1000, k });
}