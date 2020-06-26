# hypoDDpy

This a collection of tools to run
[HypoDD](http://www.ldeo.columbia.edu/~felixw/hypoDD.html) by Felix Waldhauser,
updated by Wayne Crawford.

It takes event files in the QuakeML format, station data in the SEED format and
waveform data in any format ObsPy can read and does all the rest.

The output is one QuakeML file with the relocated events having one additional
Origin node. The events that could not be relocated will not be changed.

![Flowchart 1](https://raw.github.com/krischer/hypoDDpy/master/img/flowchart.png)

### Did It Help You in Your Research?

If yes, consider citing this software! Just click on this button here to get all the required information:

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.18907.svg)](http://dx.doi.org/10.5281/zenodo.18907)


### Requirements

* Python 3.6+
* NumPy
* matplotlib
* progressbar
* cartopy
=======
* [ObsPy](http://obspy.org) (Tested on 1.2.0)

### Installation
hypoDDpy currently works with HypoDD 2.1b which you will have to acquire
separately from Felix Waldhauser.

Put the archive here:
```
hypoddpy/src/HYPODD_2.1b.tar.gz
```
The src directory will likely not exist.

Then run *either of the* following two commands, depending on which Python module installer you prefer:
```
pip install -v -e .
python setup.py develop
```

The in-place install is a good idea because there is a chance that you will
have to adjust the source code.


### Running it

It is steered via a Python script that you will have to create. It should be
rather self-explanatory.

After you created it, simply run it to perform the relocation.

```python
import glob
from hypoddpy import HypoDDRelocator


# Init the relocator with the working directory and some necessary
# configuration values.
#
# The working dir is where all the working files and some output files will be
# stored.
# All the other attributes are related to the cross correlation and should be
# self-explanatory.
relocator = HypoDDRelocator(working_dir="relocator_working_dir",
    cc_time_before=0.05,
    cc_time_after=0.2,
    cc_maxlag=0.1,
    cc_filter_min_freq=1.0,
    cc_filter_max_freq=20.0,
    cc_p_phase_weighting={"Z": 1.0},
    cc_s_phase_weighting={"Z": 1.0, "E": 1.0, "N": 1.0},
    cc_min_allowed_cross_corr_coeff=0.4)

# Add the necessary files. Call a function multiple times if necessary.
relocator.add_event_files(glob.glob("events/*.xml"))
relocator.add_waveform_files(glob.glob("waveform/*.mseed"))
relocator.add_station_files(glob.glob("station/*.xml"))

# Setup the velocity model. This is just a constant velocity model.
relocator.setup_velocity_model(
    model_type="layered_p_velocity_with_constant_vp_vs_ratio",
    layer_tops=[(-10000, 5.8)],
    vp_vs_ratio=1.73)

# Start the relocation with the desired output file.
relocator.start_relocation(output_event_file="relocated_events.xml")

# Plot events with a slightly better presentation than the default plots
# Have to use "replace_scatter_with_plot" until cartopy 0.18.1 comes out
relocator.plot_events(coastlines='10m', replace_scatter_with_plot=True)
```

You can also plot the results after the fact, using the output event file:
```python
from hypoddpy import HypoDDPlotter
from obspy.core.event import read_events

catalog_file = 'relocated_events.xml'
map_extent=[45.15, 45.75, -13, -12.6]
depth_extent=[0, 50]

print(f'Reading catalog file {catalog_file}...', end='', flush=True)
cat = read_events(catalog_file, 'QUAKEML')
print(f'read {len(cat)} events')
obj = HypoDDPlotter(cat, map_extent, depth_extent, coastlines='10m',
                    replace_scatter_with_plot=True)
obj.plot_events(file_base='main_swarm_EW',
                polygon=[[45.3, -12.78],
                         [45.3, -12.82],
                         [45.5, -12.82],
                         [45.5, -12.78]])
obj.plot_events(file_base='main_swarm_NS',
                polygon=[[45.39, -12.65],
                         [45.39, -12.95],
                         [45.42, -12.95],
                         [45.42, -12.65]])
obj.plot_events(file_base='secondary_swarm',
                polygon=[[45.50, -12.70],
                         [45.65, -12.80],
                         [45.65, -12.90],
                         [45.50, -12.80]])
```
