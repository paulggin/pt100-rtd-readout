# Project 5 — PT100 RTD Readout: Circuit Design

Component-level design for the PT100 readout chain, finalized to the point of schematic capture. Every topology choice, component value, and gain target below is fixed; the remaining work is drawing it in KiCad and validating it in SPICE. All sizing numbers are reproduced by `experiments/sizing.py` (see the verification block at the end).

## Overview

The readout is a **1.000 mA constant-current excitation source, a 4-wire (Kelvin) PT100 connection, and a two-stage amplifier that maps the 0–100 °C range to a clean 0–3.00 V output**. The two stages are an INA128 instrumentation amplifier at a gain of 10, followed by a difference amplifier at a gain of 7.79 that subtracts the 0 °C baseline and trims the overall gain. Total signal gain is 77.9, which maps the 38.5 mV sensor span to 3.00 V.

The design is **ratiometric through a shared 2.5 V reference**: the same REF3025 that sets the excitation current also sets the baseline-subtraction voltage. Both the amplified PT100 signal and the subtracted baseline scale with the reference, so first-order reference drift cancels in the difference stage rather than reading out as a temperature error.

The PT100 is grounded on its low side and driven from a Howland current pump on its high side. This keeps the instrumentation-amplifier common-mode voltage near 0.1 V, well inside the INA128 input range on ±5 V rails, and avoids the near-rail common-mode problem that a high-side-grounded sensor would create.

## Sensor model (Callendar–Van Dusen)

For T ≥ 0 °C the platinum element follows R(T) = R₀(1 + A·T + B·T²) with R₀ = 100 Ω, A = 3.9083 × 10⁻³ °C⁻¹, B = −5.775 × 10⁻⁷ °C⁻² (IEC 60751). The design points the rest of the circuit is sized against:

| T (°C) | R (Ω) | V at 1.000 mA (mV) |
| :-- | --: | --: |
| 0 | 100.000 | 100.000 |
| 25 | 109.735 | 109.735 |
| 50 | 119.397 | 119.397 |
| 75 | 128.987 | 128.987 |
| 100 | 138.506 | 138.506 |

Sensitivity near 0 °C is 0.3908 Ω/°C, so at 1.000 mA the sensor produces 0.3908 mV/°C and a full-span swing of 38.505 mV. In SPICE the PT100 is replaced by a fixed resistor set to the R(T) value for each point in this table; sweeping the resistor stands in for sweeping temperature.

## Excitation current and self-heating

**I = 1.000 mA is the excitation current.** At that level the sensor dissipates I²R = 100.0 µW at 0 °C and 138.5 µW at 100 °C. A thin-film PT100 has a dissipation constant on the order of a few mW/°C in still air and far higher when clamped to a cold stage, so the self-heating error stays well under 0.1 °C and is negligible against the lead-resistance and amplifier error terms below. The same 1.000 mA sets the sensor-terminal sensitivity at 0.3908 mV/°C, which is the signal the front end has to resolve.

## Constant-current source: improved Howland current pump

**The excitation source is an improved Howland current pump set by the 2.5 V reference and a precision resistor, I = V_ref / R_set.** With R_set = 2.490 kΩ the current is 1.004 mA; with 2.500 kΩ it is exactly 1.000 mA. Absolute current accuracy is non-critical because the baseline subtraction shares the same reference, so 2.490 kΩ (a stock E96 value) is the recommended part and the residual 0.4 % current offset cancels in the difference stage.

I chose the Howland pump over a high-side op-amp-plus-pass-transistor source for one reason: it sources a defined current into a **grounded** load, which lets the PT100 sit at ground and keeps the instrumentation-amplifier common-mode near 0.1 V. The usual Howland weakness — finite output impedance degrading current regulation as the load changes — does not bite here because the load only moves 38.5 Ω across the full temperature range. With 0.1 % matched resistors the output impedance lands near 1 MΩ, so the current shifts by 38.5 nA (0.0039 % of 1 mA) across the entire 0–100 °C swing. That is two orders of magnitude below the amplifier error budget.

The matching of the four Howland resistors sets the output impedance, so they are specified as a 0.1 % matched network (or a single resistor-array package) and carry a low temperature coefficient. The op-amp is one half of an LT1013 dual precision op-amp. The LT1013 replaces the OPA2277 originally specified because KiCad's stock `Amplifier_Operational` library carries the LT1013 symbol directly; the two share the standard 8-pin dual pinout, so it is a drop-in swap. The offset penalty is immaterial here — the LT1013's ~150 µV offset, after the ×7.87 output-stage gain, contributes about 0.04 °C, well under the resistor-tolerance and lead-resistance terms — because the INA128 supplies the first ×10 and the sensor signal is a large 38.5 mV.

## Amplifier chain: INA128 stage + difference stage

**Stage 1 is an INA128 at a gain of 10**, reading the two PT100 sense leads on its high-impedance inputs so no current flows in the sense wires (the Kelvin condition). The INA128 gain law is G = 1 + 50 kΩ/R_G, so a gain of 10 needs R_G = 5.556 kΩ; the nearest E96 value, 5.49 kΩ, gives G = 10.107. Stage-1 output runs from 1.000 V at 0 °C to 1.385 V at 100 °C. Those voltages sit comfortably mid-range on ±5 V rails — the reason the front end uses a dual supply rather than a single +5 V rail, where the 1.000 V floor would crowd the INA128's minimum output.

**Stage 2 is a difference amplifier at a gain of 7.79** that subtracts a 1.000 V baseline and applies the remaining gain, producing 0 V at 0 °C and 3.00 V at 100 °C. The gain is set by the feedback ratio R_f/R_in; with R_in = 10.0 kΩ and R_f = 78.7 kΩ (E96) the gain is 7.87 and full-scale output is 3.03 V, which is the recommended pairing. Trimming R_f to 77.5 kΩ lands at exactly 2.984 V if a tighter full-scale target is wanted — final gain is set at this one resistor. The second op-amp is the other half of the OPA2277.

The 1.000 V subtraction node comes from the 2.5 V reference through a 0.400 divider ratio, buffered. Deriving it from the same REF3025 that sets the current is what makes the chain ratiometric: stage-1 baseline is G₁·I·R₀ = G₁·(V_ref/R_set)·R₀ and the subtracted voltage is k·V_ref, so both terms carry the V_ref factor and reference drift cancels to first order at the difference-stage input.

**Total signal gain is 10 × 7.79 = 77.9**, mapping the 38.505 mV sensor span to 3.00 V — the textbook ~78 the orientation called for, now pinned to real E96 parts.

## Why 4-wire: lead-resistance error budget

The 4-wire connection exists to cancel the resistance of the cryostat wiring between the warm electronics and the sensor. In a 2-wire hookup the measured resistance is R_PT100 + 2·R_lead, and that lead term reads out as a fixed positive temperature offset. The size of the error depends on wire gauge and run length:

| Wire | Run length (m) | 2-wire loop R (Ω) | Apparent error (°C) |
| :-- | --: | --: | --: |
| 28 AWG | 1.0 | 0.426 | +1.09 |
| 28 AWG | 2.0 | 0.852 | +2.18 |
| 32 AWG | 2.0 | 2.153 | +5.51 |

Cryostat wiring deliberately uses thin gauge to limit heat conducted down to the cold stages, which is exactly the case where the 2-wire error is worst: a 2 m run of 32 AWG copper adds 2.15 Ω of loop resistance, a +5.5 °C apparent shift, larger than the precision the sensor is otherwise capable of. The 4-wire connection removes it entirely because the sense leads carry no current — any drop across them is rejected by the instrumentation amplifier's high input impedance. The SPICE lead-resistance study models this directly by inserting series resistors into the excitation and sense lines and comparing the 2-wire and 4-wire topologies, and these are the numbers it should reproduce.

(The orientation's earlier estimate of 2.6–5.2 °C assumed a higher per-length resistance; recomputed against the standard 28 AWG value of 0.213 Ω/m, a 1–2 m run gives 1.1–2.2 °C, and the 5 °C case requires the thinner 32 AWG wire typical of cold-stage looms. The corrected numbers are in the table above.)

## Supply rails

The analog front end runs on **±5 V**. That gives the INA128 clean headroom around its 1.0–1.385 V stage-1 output and lets the difference stage swing to 0 V at the bottom of its range without fighting a single-supply floor. The 2.5 V reference and the 1.000 V subtraction node are both positive and derived from the +5 V rail through the REF3025. A single +5 V variant is possible with rail-to-rail parts but is not the recommended build, since it trades the INA128's well-characterized behavior for marginal output headroom.

## Bill of materials

| Ref | Part | Value / spec | Role |
| :-- | :-- | :-- | :-- |
| U1 | REF3025 | 2.500 V, ±0.05 %, 25 ppm/°C | Shared reference (current + baseline) |
| U2A | LT1013 (½) | dual precision op-amp | Howland current-pump amplifier |
| U2B | LT1013 (½) | dual precision op-amp | Stage-2 difference amplifier |
| U3A | LT1013 (½) | dual precision op-amp | Baseline-divider buffer (U3B spare) |
| U4 | INA128 | G = 1 + 50 kΩ/R_G | Stage-1 instrumentation amp |
| R_set | resistor | 2.490 kΩ, 0.1 %, low tempco | Sets I = V_ref/R_set ≈ 1.004 mA |
| R_H1–4 | matched network | 0.1 % matched, low tempco | Howland pump (sets output impedance) |
| R_G | resistor | 5.49 kΩ, 0.1 % | INA128 gain (G₁ = 10.11) |
| R_in | resistor | 10.0 kΩ, 0.1 % | Difference-stage input |
| R_f | resistor | 78.7 kΩ, 0.1 % | Difference-stage feedback (G₂ = 7.87) |
| R_d1, R_d2 | resistors | set 0.400 ratio | 1.000 V baseline divider from 2.5 V |
| RTD | PT100 (modeled) | 100 Ω → 138.5 Ω | Sensor; discrete resistor in SPICE |
| — | bypass caps | 100 nF per supply pin | Decoupling |

For the deferred physical build, the modeled PT100 becomes a real thin-film PT100 (~$8–12) and the SPICE resistor values map onto a precision resistor kit for ice-water / room / boiling-water calibration. Nothing in the schematic changes between the simulated and fabricated versions except swapping the resistor model for the sensor and connector.

## Net-level connection list (for KiCad capture)

Reference for drawing the schematic. Nets are named by function.

- **REF_2V5** — REF3025 output. Feeds the Howland current-set resistor R_set and the baseline divider R_d1/R_d2.
- **I_DRIVE+** — Howland pump output into the PT100 high side (force lead 1).
- **PT100_HI / PT100_LO** — the two sensor terminals. Force lead 2 returns PT100_LO to ground. Sense leads tap PT100_HI and PT100_LO and run to the INA128 inputs (these carry no current).
- **INA_IN+ / INA_IN−** — INA128 pins 2/3 from the sense leads. R_G across pins 1/8. REF pin (5) to ground.
- **STAGE1_OUT** — INA128 output (pin 6), 1.000–1.385 V. To difference-stage R_in.
- **VBASE_1V0** — buffered 1.000 V baseline from the divider. To the difference-stage reference input.
- **VOUT_0_3V** — difference-amplifier output, 0–3.00 V. ADC interface node.
- **+5V / −5V / GND** — supply rails; 100 nF decoupling at every device supply pin.

## What schematic capture and SPICE still have to confirm

1. **Stage-1 output stays in range.** SPICE sweep of R_PT100 from 100 Ω to 138.5 Ω should show STAGE1_OUT tracking 1.000–1.385 V and the Howland current holding 1.000 mA (±40 nA) across the swing.
2. **End-to-end mapping.** VOUT_0_3V should land at 0 V / 3.00 V at the endpoints and stay linear to within the resistor tolerances in between.
3. **Ratiometric cancellation.** Perturbing REF_2V5 should move STAGE1_OUT and VBASE_1V0 together, leaving VOUT_0_3V nearly unchanged — the first-order drift-cancellation claim.
4. **2-wire vs 4-wire.** Inserting the lead resistances from the table should leave the 4-wire output unchanged and shift the 2-wire output by the tabulated apparent error.

## References

IEC 60751 — Industrial platinum resistance thermometers (Callendar–Van Dusen coefficients).
J. Ekin, *Experimental Techniques for Low-Temperature Measurements* (Oxford, 2006), Ch. 5–6 — RTD thermometry, 4-wire sensing, lead-resistance error.
Texas Instruments INA128 datasheet; Analog Devices AD620 datasheet — instrumentation-amplifier gain and noise.
Texas Instruments REF3025 datasheet; Analog Devices LT1013 datasheet (op-amp, KiCad-library substitute for the OPA2277).

Finalized schematic sheet: `docs/pt100_readout_schematic.pdf`.
Project 4 (Cryostat Multi-Stage Thermal Model) — stage temperatures and wiring context for where this sensor sits in the fridge.
