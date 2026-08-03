# TI LM1875 PSpice model

This directory contains the unmodified Texas Instruments PSpice model used by
the exploratory integrated-circuit validation.

- Device: LM1875
- Subcircuit: `LM1875_0`
- TI package: `SNAM066A`
- Package revision: A
- Model version: 1.0
- Model release: 2012-03-29
- Official download: <https://www.ti.com/lit/zip/snam066>
- Downloaded archive SHA-256:
  `5C8777C936D6C1279E6F9F6117E57F954D487AE3F4EE67EFCE1927C6542EB50B`
- `LM1875.lib` SHA-256:
  `28BF3FC1D14AD5929C3151A7BCB6F97922BD59B38539FE334B7018522551B1F2`

The model is loaded through `metadata/pipeline2_spice_models.yaml`, verified,
and written to the run-local `07_external_models.lib` bundle. The generated
netlist includes that bundle so web and scenario copies remain portable. The
registry requests ngspice PSpice compatibility (`ngbehavior=ps`); no
device-specific behavior is implemented in Python.

The subcircuit port order declared by TI is:

`Vin Vip VSS VDD Vout`

An independent ngspice 46 transient probe used +/-25 V supplies, a 20 mV peak
1 kHz input, a 180 kohm / 10 kohm feedback network and a 4 ohm load. The run
completed successfully and measured 0.7595 Vpp at the output for 0.0400 Vpp at
the source, corresponding to a gain of 18.99.

The original copyright, warranty disclaimer, usage notes and revision history
are preserved inside `LM1875.lib`.
