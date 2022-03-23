#!/usr/bin/env python3

"""Try running r5 from Python (geopandas!), using JPype."""

import datetime

import geopandas
import jpype
import jpype.imports
import pandas

from .mem import EIGHTY_PERCENT_OF_RAM

jpype.startJVM(
    "-Xmx{:d}G".format(EIGHTY_PERCENT_OF_RAM),
    classpath=["/usr/share/java/r5/r5-all.jar"]
)

import java.io  # noqa: E402
import java.lang  # noqa: E402

import ch.qos.logback.classic  # noqa: E402
import com.conveyal.r5  # noqa: E402
import org.slf4j.LoggerFactory  # noqa: E402

verbose = True
if not verbose:
    logger_context = org.slf4j.LoggerFactory.getILoggerFactory()
    for log_target in (
            "com.conveyal.r5",
            "com.conveyal.osmlib",
            "com.conveyal.gtfs",
            "com.conveyal.r5.profile.ExecutionTimer",
            "graphql.GraphQL",
            "org.mongodb.driver.connection",
            "org.eclipse.jetty",
            "org.eclipse.jetty",
            "com.conveyal.r5.profile.FastRaptorWorker",
    ):
        logger_context.getLogger(log_target).setLevel(
            ch.qos.logback.classic.Level.valueOf("ERROR")
        )

transport_network = com.conveyal.r5.transit.TransportNetwork.fromDirectory(
    java.io.File("/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki")  # noqa: E501
)
transport_network.transitLayer.buildDistanceTables(None)

ykr_centroids = geopandas.read_file("/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/YKR_250m_PKS.gpkg", layer="YKR 250m Pääkaupunkiseutu centroids (EPSG:4326)")  # noqa: E501

request = com.conveyal.r5.analyst.cluster.RegionalTask()
request.scenario = com.conveyal.r5.analyst.scenario.Scenario()
request.scenario.id = "id"
request.scenarioId = request.scenario.id
request.zoneId = transport_network.getTimeZone()

request.walkSpeed = 1.0  # m/s = 3.6 km/h
request.bikeSpeed = 3.3  # m/s = 11.88 km/h

request.maxWalkTime = 1200
request.maxBikeTime = 1200
request.maxCarTime = 1200
request.maxTripDurationMinutes = 1200

request.maxRides = 8
request.bikeTrafficStress = 4

access_modes = java.util.EnumSet.noneOf(com.conveyal.r5.api.util.LegMode)
access_modes.add(com.conveyal.r5.api.util.LegMode.valueOf("WALK"))
egress_modes = access_modes

request.directModes = access_modes  #java.util.EnumSet.noneOf(com.conveyal.r5.api.util.LegMode)  #[]  #["WALK", "BICYCLE", "CAR", "BICYCLE_RENT", "CAR_PARK"]
request.accessModes = access_modes
request.egressModes = egress_modes
request.transitModes = java.util.EnumSet.allOf(com.conveyal.r5.api.util.TransitModes)  #["TRANSIT", "TRAM", "SUBWAY", "RAIL", "BUS", "FERRY", "CABLE_CAR", "GONDOLA", "FUNICULAR"]

request.makeTauiSite = False
request.recordTimes = True  #?
request.recordAccessibility = False  #?

request.date = java.time.LocalDate.of(2022, 2, 22)  #datetime.date(2022, 2, 22)
request.fromTime = int(datetime.timedelta(hours=8, minutes=30).total_seconds()) # secondsFromMidnight!
request.toTime = (request.fromTime + int(datetime.timedelta(hours=1).total_seconds()))

request.monteCarloDraws = 60
request.percentiles = [50]

# *one* origin
origin = ykr_centroids.iloc[222, ]
request.fromLat = origin.geometry.y
request.fromLon = origin.geometry.x

# *many* destinations, enterprisely in a stream
output_stream = java.io.ByteArrayOutputStream()
data_output_stream = java.io.DataOutputStream(output_stream)

# number of records
data_output_stream.writeInt(len(ykr_centroids))

# data, one column after another, then ‘opportunies’
for id_ in ykr_centroids.id.astype(str):
    data_output_stream.writeUTF(id_)
for lat in ykr_centroids.geometry.y:
    data_output_stream.writeDouble(lat)
for lon in ykr_centroids.geometry.x:
    data_output_stream.writeDouble(lon)
for _ in range(len(ykr_centroids)):
    data_output_stream.writeDouble(0)  # ‘opportunities’

# convert to point set via an input_stream (yeah, I know)
input_stream = java.io.ByteArrayInputStream(output_stream.toByteArray())
destinationPointSet = com.conveyal.r5.analyst.FreeFormPointSet(input_stream)
request.destinationPointSets = [destinationPointSet]
transport_network.linkageCache.getLinkage(destinationPointSet, transport_network.streetLayer, com.conveyal.r5.profile.StreetMode.valueOf("WALK"))

travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(request, transport_network)
results = travel_time_computer.computeTravelTimes()

travel_times = pandas.DataFrame({"travel_times": results.travelTimes.getValues()[0]})
