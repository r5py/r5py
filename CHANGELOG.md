- **1.0.7** (2025-09-05):
    - Fix wrong max_time (#504)

- **1.0.6** (2025-06-04):
    - Workaround for #492 (clamping geopandas version)

- **1.0.5** (2025-05-13):
    - Fix OpenJDK64 issue (#486)
    - Improve build environments

- **1.0.4** (2025-04-24):
    - Added terrain-sensitive routing
    - Improved handling of cached transport networks
    - Based on R⁵-v7.4

- **1.0.3** (2025-03-30):
    - More precise checking of GTFS coverage for departure date
    - Report issues in input GTFS data
    - Relaxed unit tests for isochrones

- **1.0.2** (2025-03-13):
    - Include test fixtures and data in sdist
    - Remove unused parameter breakdown
    - Fixed a few typos in documentation

- **1.0.1** (2025-03-11):
    - Added typing-extensions to dependencies
    - Optimised binder integration and environment
    - Updated to Python>=3.10

- **1.0.0** (2025-03-09):
    - introduced Isochrones: compute areas of equal travel time from an origin
    - introduced TravelTimeMatrix, DetailedItineraries that inherit from
      pandas.DataFrame
    - TransportNetworks are now cached and loaded from disk on subsequent runs
    - deprecated TravelTimeMatrixComputer, DetailedItinerariesComputer
    - more detailed output (additional columns on routes, stops, etc.) for
      detailed itineraries
    - testing with different R5 versions
    - numerous minor improvements and bug fixes

- **0.1.2** (2024-07-28):
    - numerous smaller improvements and bug fixes
    - remodelled build environment
    - support for Python 3.12
    - fully compliant with pydocstyle
    - based on R⁵-v7.1, with our own patches

- **0.1.1** (2023-10-25):
    - BREAKING: retired support for Python 3.8
    - implemented support for pandas>=2.1 and geopandas>=0.14
    - added --temporary-directory configuration option/argument
    - created sample data packages r5py.sampledata.helsinki and
      r5py.sampledata.sao_paulo
    - improved documentation
    - numerous smaller fixes

- **0.1.0** (2023-08-15):
    - added class to compute detailed itineraries
    - simplified transport modes
    - rewrote and restructured documentation
    - improved test coverage to 99.5%
    - numerous bug fixes and improvements

- **0.0.4** (2022-09-09):
    - a new logo
    - created DOI to properly cite r5py in academic research
    - improved and expanded documentation
    - enable interactive notebooks (using binder)
    - added more sample data
    - provide Markdown and Jupyter notebooks
    - fix calculation of memory limits
    - better input data validation
    - improved test coverage to 94%
    - fixed Python-3.8 compatibility

- **0.0.3** (2022-05-12):
    - refreshed documention
    - added contribution guidelines
    - added issue templates
    - added tests, set up matrix testing infrastructure
    - setup coverage reports (codecov.io)
    - bugfixes, refactoring
    - license change: now GPL/MIT dual license
    - first release to PyPi

- **0.0.2** (2022-05-03):
    - migrated CI/CD from GitLab to GitHub

- **0.0.1** (2022-04-11):
    - very first release
    - feature-parity to r5r concerning the travel time matrix, only
