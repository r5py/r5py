---
jupytext:
  formats: md:myst
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

# Decomposed travel times

```{code-cell} ipython3
:tags: [remove-input, remove-output]


```

:::{dropdown} Why decompose a travel time?
:open:
:color: light
:margin: 1 5 0 0

A single transit travel time hides a lot of structure. Two trips of thirty
minutes are not equivalent if one is spent entirely on a train while the other
is half spent waiting at a stop and walking to it: riders perceive time spent
waiting, walking, and transferring differently from time spent moving on a
vehicle, and many transport models weight these components separately.

{class}`TravelTimeMatrixDecomposed<r5py.TravelTimeMatrixDecomposed>` reports, for
each origin and destination, how the travel time splits into its **in-vehicle**,
**waiting**, **access** (to the first stop), **egress** (from the last stop), and
**transfer** components, along with the routes and stops that make up each path.
R5 computes this breakdown internally on every routing request; this class simply
surfaces it.
:::


## Load a transport network

As for a {doc}`travel time matrix <travel-time-matrices>`, we need a transport
network and a set of origins and destinations. We reuse the São Paulo [sample
data sets](../installation/installation.md#sample-data-sets):

```{code-cell} ipython3
:tags: [remove-output]

import r5py
import r5py.sampledata.sao_paulo

transport_network = r5py.TransportNetwork(
    r5py.sampledata.sao_paulo.osm_pbf,
    [
        r5py.sampledata.sao_paulo.gtfs,
    ]
)
```

```{code-cell} ipython3
import geopandas

hexagon_grid = geopandas.read_file(r5py.sampledata.sao_paulo.hexgrid_gpkg)

origins = hexagon_grid.copy()
origins["geometry"] = origins.geometry.centroid
```

To keep the example small, we route from a handful of origins to all grid cells:

```{code-cell} ipython3
origins = origins.iloc[:5]
destinations = hexagon_grid.copy()
destinations["geometry"] = destinations.geometry.centroid
```


## Compute a decomposed travel time matrix

The constructor mirrors {class}`TravelTimeMatrix<r5py.TravelTimeMatrix>`. Because
the breakdown only makes sense for public transport, we route with
{attr}`r5py.TransportMode.TRANSIT` (and {attr}`r5py.TransportMode.WALK` for access
and egress):

```{code-cell} ipython3
import datetime

decomposed = r5py.TravelTimeMatrixDecomposed(
    transport_network,
    origins=origins,
    destinations=destinations,
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    departure=datetime.datetime(2019, 5, 13, 14, 0, 0),
    departure_time_window=datetime.timedelta(minutes=60),
)
decomposed.head()
```

Unlike a travel time matrix, which has exactly one row per origin/destination
pair, a decomposed matrix has **one row per origin, destination, and path
template** — a distinct sequence of routes and stops that R5 found between the
pair. A pair can therefore appear in several rows (several ways of getting there)
or in none (it is not reachable). Rows with `n_rides == 0` are direct
(walk-only) paths.

The columns are:

| column | description |
| --- | --- |
| `from_id`, `to_id` | origin and destination ids |
| `routes` | `\|`-separated GTFS route ids, one per transit leg |
| `route_types` | GTFS `route_type` of each leg (e.g. `3` for bus) |
| `board_stops`, `alight_stops` | GTFS stop ids where each leg is boarded / alighted |
| `feed_ids` | GTFS feed each leg belongs to |
| `in_vehicle_time` | per-leg in-vehicle time (a list, in minutes) |
| `wait_time` | per-leg waiting time (a list, in minutes) |
| `access_time`, `egress_time` | walk time to the first / from the last stop (minutes) |
| `transfer_time` | time transferring between stops (minutes) |
| `total_time` | total travel time of this path template (minutes) |
| `n_rides` | number of transit legs |
| `n_iterations` | number of departure minutes served by this template |

The per-leg `in_vehicle_time` and `wait_time` are kept as lists rather than
pre-summed, so that, for example, the wait before the first boarding can be
weighted differently from a mid-trip transfer wait. The scalar components of a
single row always reconcile to its `total_time`:

```{code-cell} ipython3
transit = decomposed[decomposed["n_rides"] > 0]

reconstructed = (
    transit["in_vehicle_time"].map(sum)
    + transit["wait_time"].map(sum)
    + transit["access_time"]
    + transit["egress_time"]
    + transit["transfer_time"]
)
(reconstructed - transit["total_time"]).abs().max()
```


## Which iteration is reported?

Over the `departure_time_window`, R5 computes a separate result for every
departure minute (an *iteration*). A path template’s in-vehicle, access, and
egress times are the same in every iteration it appears in, but its waiting time
— and therefore its transfer and total times — varies with when the rider sets
off. The `breakdown_stat` argument selects which iteration represents the
template:

- {attr}`r5py.BreakdownStat.MEAN` (default): the iteration whose total waiting
  time is closest to the *mean* over the template’s iterations.
- {attr}`r5py.BreakdownStat.MINIMUM`: the iteration whose total waiting time is
  closest to the *minimum* (i.e. a best-case, just-caught-the-bus wait).

```{code-cell} ipython3
best_case = r5py.TravelTimeMatrixDecomposed(
    transport_network,
    origins=origins,
    destinations=destinations,
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    departure=datetime.datetime(2019, 5, 13, 14, 0, 0),
    departure_time_window=datetime.timedelta(minutes=60),
    breakdown_stat=r5py.BreakdownStat.MINIMUM,
)
```


:::{admonition} The components do not sum to a travel time matrix’s `travel_time`
:class: attention

A {class}`TravelTimeMatrix<r5py.TravelTimeMatrix>` reports a *percentile* (by
default the median) of the total travel time over the departure time window,
whereas the decomposition summarises the iterations of a *single path template*
(see `breakdown_stat` above). These are different statistics, so the reported
components will **not**, in general, add up to the `travel_time` a travel time
matrix reports for the same origin/destination pair.

There is also a selection effect: if a pair is not reachable in every departure
minute, its component means are conditional on it being reachable at all, which
understates waiting time in particular. Use `n_iterations` (how many of the
departure minutes each template serves) to weight or filter the templates for
your analysis. The components of any *single* row are always internally
consistent, as shown above.
:::


:::{admonition} At most 5000 destinations
:class: note

R5 records path details for at most 5000 destinations per request
(`PathResult.MAX_PATH_DESTINATIONS`). Requesting more raises a `ValueError`;
split the destinations into batches and concatenate the resulting frames.
:::
