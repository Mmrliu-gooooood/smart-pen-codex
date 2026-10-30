# Dependency notices

This candidate does not vendor Bleak or its backend packages. Optional radio integration
uses the already-installed official `bleak==3.0.2`, MIT license (copyright Henrik Blidh),
whose installed license and metadata hashes are recorded in DEPENDENCY_EVIDENCE.json.
The existing Linux installation also contains `dbus-fast==5.2.0`, MIT according to its
installed metadata. Platform-specific WinRT/PyObjC packages are not bundled or validated.
Consult their distribution notices before redistribution.

Python and SQLite are provided by the runtime; this directory does not redistribute them.
Frozen project C sources are read-only inputs to an optional interoperability test, not
vendored dependencies. No license change for the original project is asserted here.
