v0.0.2:
======================

* Works on python 3.6+
* Added StationXML file read to HypoDDRelocator._parse_station_files()
* If {net}.{sta} > 7 characters (hypoDD limitation), only puts {sta} in
  input files
* fixed distance dimensions bug in _write_ph2dt_inp_file() (maxsep was 
  calculated using depth differences in meters instead of km)
- Added check for > 30 model layers to HypoDDRelocator.setup_velocity_model()
- Added shift_stations parameter to HypDDRelocator class, to overcome
  HypoDD limitation that any stations with negative elevation are shifted to
  zero elevation.  Shifts stations and model so that minimum station elevation
  is zero, then shifts event depth back when writing to QuakeML file (SHIFTING
  BACK ONLY WORKS IF THE station.json file didn't already exist, so if you just
  modify hypoDD.inc and rerun the depths will not be shifted: see TODO.md).
- Added  HypoDDRelocator.modify_compile_parameters(): allows the user to
  specify parameters used to compile hypoDD
- Added class HypoDDPlotter, which makes more geometrically accurate plots
- Added method hypodd_relocator.plot_events(), which uses HypoDDPlotter
  to plot events after they are relocated