# Installation

## Dependencies

### Java Development Kit

In order to interface with R5, **r5py** requires a *Java Development Kit* (jdk) in version 11. [OpenJDK](https://openjdk.java.net/) works fine.


### R5

**R5py** searches for a local R5 installation in the default class path (`/usr/share/java/r5/r5-all.jar`). If it is not found, it automatically downloads its own copy of R5. The class path can be configured to point to a different location, see *[Configuration](configuration)*). 


### Python

**R5py** requires Python in version 3.8 or later. <!--// TODO: how does conda handle this? //-->


### Python modules

If installed using `pip`, all Python modules that **r5py** depends on are installed as dependencies. <!--// TODO: conda //-->


## Installation

**R5py** is available from PyPi, and can be installed using `pip`:

```sh
pip install r5py
```

<!--// TODO: 
Add conda installation (including environment). Maybe as the first/recommended method?
--//>
