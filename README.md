# MHz Utilities

This is a collection of small utilities for interacting with the various pieces of equipment in the MHz system (a time-resolved circular dichroism spectrometer).
Everything is currently written in Python, but I suspect most things will be rewritten in Rust for robustness and ease of packaging/deployment.

## Contents

The `equipment` package contains classes for communicating with different pieces of equipment. This is the list so far:

* `pem.py`: A Hinds photoelastic modulator, used to modulate intensity or polarization depending on the optical elements surrounding it.
* `zaber_stepper.py`: A Zaber translation stage in the Ti:Sapph oscillator. When used with a slit, this allows you to tune the wavelength of the oscillator.
* `lia.py`: A Stanford Research Systems SR865A lock-in amplifier. This is crucial to most experiments done with this system.
* `pump.py`: A Spectra-Physics Millenia eV 5W pump laser. This is mostly here so that I can start warming up the laser before I get to work :)

The `scripts` directory contains some scripts for very specific purposes:

* `stepper_move.py`: Allows you to move the Zaber translation stage to an absolute position given in steps of the stepper motor. If you have a file calibrating a wavelength to a position, you can specify the desired wavelength and the script will roughly interpolate the position.
* `stepper_position.py`: This just reads the position of the Zaber translation stage at a single point.
* `stepper_stream_position.py`: This constantly polls the position of the translation stage so that you can move it by hand and see the position without needing to execute another script.
* `scan_steady_state_cd.py`: This coordinates the PEM, LIA, and stepper motor to collect a CD spectrum over a range of wavelengths.

## License

Licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in the work by you, as defined in the Apache-2.0
license, shall be dual licensed as above, without any additional terms or
conditions.
