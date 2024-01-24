# Build Seafile manually

You can build the Seafile on your own device.

## Usage

* Run `./seafile-build.sh 11.0.x`
* The stript will clone source codes to `./src`, and compile Seafile
* Finally, the `seafile-server-11.0.x` folder will be generated

Or build Seafile in the ubuntu docker container

* Run `docker run --rm -it --volume=/$(pwd):/seafile ubuntu:22.04 /seafile/seafile-build.sh 11.0.x`
