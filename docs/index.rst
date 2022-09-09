R5py
====

**R5py** is a Python library for rapid realistic routing on multimodal transport networks (walk, bike, public transport and car).
It provides a simple and friendly interface to R\ :sup:`5`\ , the Rapid Realistic Routing on Real-world and Reimagined networks,
the `routing engine <https://github.com/conveyal/r5>`_ developed by Conveyal. ``r5py`` is inspired by `r5r, a wrapper for R <https://ipeagit.github.io/r5r/>`_,
and it is designed to interact with `GeoPandas <https://geopandas.org/>`_ GeoDataFrames.

``R5py`` offers a simple way to run R5 locally with Python, allowing the users to calculate travel time matrices and accessibility by different travel modes.
To get started, see a detailed demonstration of the ``r5py`` in action from the :doc:`notebooks/basic-usage` -section.
Over time, ``r5py`` will be expanded to incorporate other functionalities from R5.


.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   configuration
   notebooks/basic-usage.ipynb
   CONTRIBUTING
   Code of conduct <CODE_OF_CONDUCT>
   citation

.. toctree::
    :caption: Reference

    Module contents <reference>
