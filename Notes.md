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
- hypodd_relocator._create_output_event_file(): changed res_id.getRefferedObject()
    to res_id.get_referred_object()
