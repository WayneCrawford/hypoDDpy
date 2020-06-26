# To Do

- Adjust events down after hypoDD run to compensate to station shift
    * won't be necessary if hypoDD accepted negative station elevations
    * will require comparison of station.sel/dat file with station.json file
      to see if the stations were shifted
      (hypoDD_relocator._station_elevation_offset())
    * same code could be used to decide whether to shift model up
- Add codes to configure input files:
    * set_hypoDD_params()
    * set_ph2dt_params()