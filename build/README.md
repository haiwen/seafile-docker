# Build Seafile manually

You can build the Seafile community edition package on your own device.

## Usage

You can build in a Ubuntu virtual machine:

* Run `./seafile-build.sh 11.0.x`
* The stript will clone source codes to `./src`, and compile Seafile
* Finally, the `seafile-server-11.0.x` folder will be generated

Or build Seafile in a Ubuntu docker container:

* Run `docker run --rm -it --volume=/$(pwd):/seafile ubuntu:22.04 /seafile/seafile-build.sh 11.0.x`
