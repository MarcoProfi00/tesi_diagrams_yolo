# TI LM317 transient PSpice model

This directory contains the unmodified Texas Instruments unencrypted PSpice
transient model used by the exploratory integrated-circuit validation.

- Device: LM317 / LM317T
- Subcircuit: `LM317_TRANS`
- TI package: `SLVMC40`
- Model version: Final 1.00
- Model release: 2014-12-11
- Official download: <https://www.ti.com/lit/zip/slvmc40>
- Downloaded archive SHA-256:
  `3691EAC9792C92D8C49722441F3A783DB987A28ACFF788220BC71358F8D8F299`
- `LM317_TRANS.LIB` SHA-256:
  `9B56D7C68B75D3C0FD1E0B55F5DDC448F89F82984F026FF31ACDF89BDE4BD7E1`

The model is loaded through `metadata/pipeline2_spice_models.yaml`, verified,
and written to the run-local `07_external_models.lib` bundle. The generated
netlist includes that bundle so web and scenario copies remain portable. The
registry requests ngspice PSpice compatibility (`ngbehavior=ps`); no
device-specific behavior is implemented in Python.

The subcircuit port order declared by TI is:

`IN ADJ OUT_0 OUT_1`

`OUT_1` is present in the interface but is not referenced by the model body.
The circuit values metadata maps both output names to the physical OUT node.

An independent ngspice 46 regulator probe completed successfully with a 12 V
input and measured a regulated output of 9.06477 V. A second probe used the
complete ic03 RC topology and a documented 12 ohm resistive lamp equivalent;
after startup, the 10 s to 20 s interval ranged from 0.0402 V to 11.5005 V.

The original copyright, warranty disclaimer, usage notes and revision history
are preserved inside `LM317_TRANS.LIB`.

