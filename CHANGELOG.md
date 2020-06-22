hypoddpy/__init__.py
    Changed "from hypodd_relocator import HypoDDRelocator"
    to "from .hypodd_relocator import HypoDDRelocator"

CONVERSION TO PYTHON3
=====================
ran 2to3 -p -v -w
changed "import md5" to "import hashlib"
Set subprocess.Popen(unversal_newlines=True) in hypodd_compiler.compile_hypodd()
    so that the stdout output will be a text string (as in Python 2)
    rather than a byte string
2 to 3 bug?: changed Exception.message to str(Exception) (lines 1104)

MODERNISATION
=====================
changed hypodd_relocator.HyopDDRelocator._parse_station_files() to
    read StationXML files
modified station_id to not include network if {net}.{sta} > 7 characters
added shift_stations attribute (and associated code) to HypDDRelocator class
- hypodd_relocator._create_output_event_file(): changed res_id.getRefferedObject()
    to res_id.get_referred_object()

BUGFIXES
=====================
- corrected bug in  _write_ph2dt_inp_file(self) where maxsep was 
  calculated using depth differences in meters instead of km
- hypodd_relocator.setup_velocity_model(): Added check for > 30 model layers
    
ADDITIONS:
=====================
- Added option to shift stations and model upwards so that all elevs are >= 0
  (bypasses bug in hypoDD)
- Added method hypodd_relocator.modify_compile_parameters()
    - changes new parameter hypodd_relocator.compile_param, dictionary
      containing all compile options to modify from defaults

TODO:
=====================
- SHIFT EVENTS BACK DOWN AFTER RELOCATION IF STATIONS WERE SHIFTED UPWARD**
- iteration distance values should be calculable or 
  enterable for DATA_WEIGHTING_AND_REWEIGHTING variable in
  _write_hypoDD_inp_file().
