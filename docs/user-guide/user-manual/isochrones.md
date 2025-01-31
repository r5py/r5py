---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell}
:tags: [remove-input, remove-output]

# this cell is hidden from READTHEDOCS output
# it’s used to
#    - force pandas to show all columns of the (very wide)
#      result data set

import pandas
pandas.set_option("display.max_columns", None)
```

```{code-cell}
:tags: [remove-input, remove-output]

# also this cell is hidden from READTHEDOCS output
# it’s used to set a stricter memory limit in binderhub notebooks
# as otherwise, the examples would fail

import os

if "MEM_LIMIT" in os.environ:  # binder/kubernetes!
    max_memory = int(os.environ["MEM_LIMIT"]) / 2
    sys.argv.extend(["--max-memory", f"{max_memory}"])
```

# Compute isochrones

TODO
