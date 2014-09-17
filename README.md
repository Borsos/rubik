[![Build Status](https://coveralls.io/repos/simone-campagna/rubik/badge.png?branch=master)](https://coveralls.io/r/simone-campagna/rubik?branch=master)
[![Coverage Status](https://travis-ci.org/simone-campagna/rubik.svg?branch=master)](https://travis-ci.org/simone-campagna/rubik.svg?branch=master)

rubik
======
Read, process, visualize and write N-dimensional cubes.

Rubik is based on the *numpy* python module; it allows to manage numpy arrays from the command line.

Rubik can also visualize 3D volumes using the *MayaVi* python module (if it is installed); this is an example:

```text
$ rubik -s 100 'cb.random_cube("100x125x70")' '_r[12:40,20:35,10:45] *= 8.0' -G

```

![VolumeSlicer](https://github.com/simone-campagna/rubik/wiki/VolumeSlicer.png)



