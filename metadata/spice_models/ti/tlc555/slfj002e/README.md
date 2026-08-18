# TI TLC555_6 PSpice model

This directory contains the unmodified Texas Instruments PSpice model used by
the exploratory integrated-circuit validation.

- Device: TLC555 / TLC556
- Subcircuit: `TLC555_6`
- TI package: `SLFJ002E`
- Package revision: E
- Model release: Final 1.1, 2023-02-06
- Official download: <https://www.ti.com/lit/zip/slfj002>
- Downloaded archive SHA-256:
  `B29DCFCDC0464374D87B036A913DBBDBF1DEFAD7818EBA7E8AB754D46B37F986`
- `TLC555_6.LIB` SHA-256:
  `7C091782CC4931DDA4FEBF25605083F47161C5E1592C076689B04B70DD749034`

The model is loaded through `metadata/pipeline2_spice_models.yaml`, verified,
and written to the run-local `07_external_models.lib` bundle. The generated
netlist includes that bundle so web and scenario copies remain portable. The
registry requests ngspice PSpice compatibility (`ngbehavior=ps`); no
device-specific behavior is implemented in Python.

The original copyright, warranty disclaimer, usage notes and revision history
are preserved inside `TLC555_6.LIB`.
