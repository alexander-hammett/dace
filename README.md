[![General Tests](https://github.com/spcl/dace/actions/workflows/general-ci.yml/badge.svg)](https://github.com/spcl/dace/actions/workflows/general-ci.yml)
[![GPU Tests](https://github.com/spcl/dace/actions/workflows/gpu-ci.yml/badge.svg)](https://github.com/spcl/dace/actions/workflows/gpu-ci.yml)
[![FPGA Tests](https://github.com/spcl/dace/actions/workflows/fpga-ci.yml/badge.svg)](https://github.com/spcl/dace/actions/workflows/fpga-ci.yml)
[![Documentation Status](https://readthedocs.org/projects/spcldace/badge/?version=latest)](https://spcldace.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/dace.svg)](https://badge.fury.io/py/dace)
[![codecov](https://codecov.io/gh/spcl/dace/branch/master/graph/badge.svg)](https://codecov.io/gh/spcl/dace)


![D](dace.svg)aCe - Data-Centric Parallel Programming
=====================================================

_Decoupling domain science from performance optimization._

DaCe is a parallel programming framework that takes code in Python/NumPy and 
other programming languages, and maps it to high-performance **CPU, GPU, and FPGA** 
programs, which can be optimized to achieve state-of-the-art. Internally, DaCe 
uses the Stateful DataFlow multiGraph (SDFG) *data-centric intermediate 
representation*: A transformable, interactive representation of code based on 
data movement.
Since the input code and the SDFG are separate, it is posible to optimize a 
program without changing its source, so that it stays readable. On the other 
hand, transformations are customizable and user-extensible, so they can be written 
once and reused in many applications.
With data-centric parallel programming, we enable **direct knowledge transfer** 
of performance optimization, regardless of the application or the target processor.

DaCe generates high-performance programs for:
 * Multi-core CPUs (tested on Intel, IBM POWER9, and ARM with SVE)
 * NVIDIA GPUs and AMD GPUs (with HIP)
 * Xilinx and Intel FPGAs

DaCe can be written inline in Python and transformed in the command-line/Jupyter 
Notebooks, or SDFGs can be interactively modified using the Data-centric 
Interactive Optimization Development Environment [Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=phschaad.sdfv).

For more information, see our [paper](http://www.arxiv.org/abs/1902.10345).

See an example SDFG [in the standalone viewer (SDFV)](https://spcl.github.io/dace/sdfv.html?url=https://spcl.github.io/dace/examples/gemm.sdfg).

Quick Start
-----------

Install DaCe with pip: `pip install dace`

Having issues? See [Troubleshooting](#Troubleshooting)

Using DaCe in Python is as simple as adding a `@dace` decorator:
```python
import dace
import numpy as np

@dace
def myprogram(a):
    for i in range(a.shape[0]):
        a[i] += i
    return np.sum(a)
```

Calling `myprogram` with any NumPy array or 
`__{cuda_}array_interface__`-supporting tensor (e.g., PyTorch, Numba) will 
generate data-centric code, compile, and run it. From here on out, you can 
_optimize_ (interactively or automatically), _instrument_, and _distribute_ 
your code. The code creates a shared library (DLL/SO file) that can readily 
be used in any C ABI compatible language (C/C++, FORTRAN, etc.).

For more information on how to use DaCe, see the [samples](samples) or tutorials below:

* [Getting Started](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/getting_started.ipynb)
* [Benchmarks, Instrumentation, and Performance Comparison with Other Python Compilers](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/benchmarking.ipynb)
* [Explicit Dataflow in Python](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/explicit.ipynb)
* [NumPy API Reference](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/numpy_frontend.ipynb)
* [SDFG API](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/sdfg_api.ipynb)
* [Using and Creating Transformations](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/transformations.ipynb)
* [Extending the Code Generator](https://nbviewer.jupyter.org/github/spcl/dace/blob/master/tutorials/codegen.ipynb)

Dependencies
------------

Runtime dependencies:
 * A C++14-capable compiler (e.g., gcc 5.3+)
 * Python 3.7 or newer (Python 3.6 is supported but not actively tested)
 * CMake 3.15 or newer

Running
-------

**Python scripts:** Run DaCe programs (in implicit or explicit syntax) using Python directly.

**[SDFV (standalone SDFG viewer)](https://spcl.github.io/dace/sdfv.html):** To view SDFGs separately, run the `sdfv` installed script with the `.sdfg` file as an argument. Alternatively, you can use the link or open `dace/viewer/webclient/sdfv.html` directly and choose a file in the browser.

**Visual Studio Code extension**: Install from the [VSCode marketplace](https://marketplace.visualstudio.com/items?itemName=phschaad.sdfv) or open an `.sdfg` file for interactive SDFG viewing and transformation.

**The sdfgcc tool:** Compile `.sdfg` files with `sdfgcc program.sdfg`. Interactive command-line optimization is possible with the `--optimize` flag.

**Jupyter Notebooks:** DaCe is Jupyter-compatible. If a result is an SDFG or a state, it will show up directly in the notebook. See the [tutorials](tutorials) for examples.

**Octave scripts (experimental):** `.m` files can be run using the installed script `dacelab`, which will create the appropriate SDFG file.

**Note for Windows/Visual C++ users:** If compilation fails in the linkage phase, try setting the following environment variable to force Visual C++ to use Multi-Threaded linkage:
```
X:\path\to\dace> set _CL_=/MT
```


Publication
-----------

If you use DaCe, cite us:
```bibtex
@inproceedings{dace,
  author    = {Ben-Nun, Tal and de~Fine~Licht, Johannes and Ziogas, Alexandros Nikolaos and Schneider, Timo and Hoefler, Torsten},
  title     = {Stateful Dataflow Multigraphs: A Data-Centric Model for Performance Portability on Heterogeneous Architectures},
  year      = {2019},
  booktitle = {Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis},
  series = {SC '19}
}
```

Troubleshooting
---------------

* If you are using DaCe from the git repository and getting missing dependencies or missing include files, make sure you cloned the repository recursively (with `git clone --recursive`) and that the submodules are up to date.
* If you are running on Mac OS and getting compilation errors when calling DaCe programs, make sure you have OpenMP installed and configured with Apple Clang. Otherwise, you can use GCC to compile the code by following these steps:
    * Run `brew install gcc`
	* Set your `~/.dace.conf` compiler configuration to use the installed GCC. For example, if you installed version 9 (`brew install gcc@9`), run `which g++-9` and set the config entry called `compiler.cpu.executable` (empty string by default) to the resulting path
	* Remove any `.dacecache` folders to clear the cache

Other issues? Look for similar issues or start a discussion on our [GitHub Discussions](https://github.com/spcl/dace/discussions)!


Configuration
-------------

DaCe creates a file called `.dace.conf` in the user's home directory. It provides useful settings that can be modified either directly in the file (YAML), or overriden on a case-by-case basis using environment variables that begin with `DACE_` and specify the setting (where categories are separated by underscores). The full configuration schema is located [here](dace/config_schema.yml).

The priority order for configuration files is as follows:
 1. If a `DACE_*` environment variable is found, its value will always be used
 2. If `with dace.config.set_temporary(...)` is used ([see example here](samples/simple/laplace.py#L43))
 3. A `.dace.conf` located in the current working directory
 4. The `.dace.conf` located in the user's home directory or the path pointed to by the `DACE_CONFIG` environment variable

Useful environment variable configurations include:

 * `DACE_CONFIG` (default: `~/.dace.conf`): Override DaCe configuration file choice.

General configuration:
 * `DACE_debugprint` (default: False): Print debugging information.
 * `DACE_compiler_use_cache` (default: False): Uses DaCe program cache instead of re-optimizing and compiling programs.
 * `DACE_compiler_default_data_types` (default: `Python`): Chooses default types for integer and floating-point values. If `Python` is chosen, `int` and `float` are both 64-bit wide. If `C` is chosen, `int` and `float` are 32-bit wide.
 
Profiling:
 * `DACE_profiling` (default: False): Enables profiling measurement of the DaCe program runtime in milliseconds. Produces a log file and prints out median runtime.
 * `DACE_treps` (default: 100): Number of repetitions to run a DaCe program when profiling is enabled.
 
GPU programming and debugging:
 * `DACE_compiler_cuda_backend` (default: `cuda`): Chooses the GPU backend to use (can be `cuda` for NVIDIA GPUs or `hip` for AMD GPUs).
 * `DACE_compiler_cuda_syncdebug` (default: False): If True, calls device-synchronization after every GPU kernel and checks for errors. Good for checking crashes or invalid memory accesses.
 
FPGA programming:
 * `DACE_compiler_fpga_vendor`: (default: `xilinx`): Can be `xilinx` for Xilinx FPGAs, or `intel_fpga` for Intel FPGAs.
 
SDFG interactive transformation:
 * `DACE_optimizer_transform_on_call` (default: False): Uses the transformation command line interface every time a `@dace` function is called.
 * `DACE_optimizer_interface` (default: `dace.transformation.optimizer.SDFGOptimizer`): Controls the SDFG optimization process if `transform_on_call` is enabled. By default, uses the transformation command line interface.
 * `DACE_optimizer_automatic_simplification` (default: True): If False, skips automatic simplification in the Python frontend (see transformations tutorial for more information).
 

Contributing
------------
DaCe is an open-source project. We are happy to accept Pull Requests with your contributions! Please follow the [contribution guidelines](CONTRIBUTING.md) before submitting a pull request.

License
-------
DaCe is published under the New BSD license, see [LICENSE](LICENSE).

