import geopandas

import jnius_config
jnius_config.add_options('-Xrs', '-Xmx16G', '-XX:MaxHeapSize=1G')
jnius_config.add_classpath("/usr/share/java/r5/r5-all.jar")

import jnius  # noqa: E402

# Java ‘imports’
ByteArrayInputStream = jnius.autoclass("java.io.ByteArrayInputStream")
ByteArrayOutputStream = jnius.autoclass("java.io.ByteArrayOutputStream")
DataInputStream = jnius.autoclass("java.io.DataInputStream")
DataOutputStream = jnius.autoclass("java.io.DataOutputStream")
JavaIoFile = jnius.autoclass("java.io.File")
JavaLangDouble = jnius.autoclass("java.lang.Double")
JavaLangInteger = jnius.autoclass("java.lang.Integer")
JavaLangString = jnius.autoclass("java.lang.String")
JavaLangReflectArray = jnius.autoclass("java.lang.reflect.Array")
FreeFormPointSet = jnius.autoclass("com.conveyal.r5.analyst.FreeFormPointSet")
PointSet = jnius.autoclass("com.conveyal.r5.analyst.PointSet")
RegionalTask = jnius.autoclass("com.conveyal.r5.analyst.cluster.RegionalTask")
Scenario = jnius.autoclass("com.conveyal.r5.analyst.scenario.Scenario")
TransportNetwork = jnius.autoclass("com.conveyal.r5.transit.TransportNetwork")
TravelTimeComputer = jnius.autoclass("com.conveyal.r5.analyst.TravelTimeComputer")  # noqa: E501

transport_network = TransportNetwork.fromDirectory(
    JavaIoFile("/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki"),  # noqa: E501
    verbose=False
)

ykr_centroids = geopandas.read_file("/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/YKR_250m_PKS.gpkg", layer="YKR 250m Pääkaupunkiseutu centroids (EPSG:4326)")  # noqa: E501

ids = ykr_centroids.id.astype(str).tolist()
lats = ykr_centroids.geometry.y.tolist()
lons = ykr_centroids.geometry.x.tolist()

request = RegionalTask()
request.scenario = Scenario()
request.scenario.id = "id"
request.scenarioId = request.scenario.id
request.zoneId = transport_network.getTimeZone()
request.fromLat = lats[222]
request.fromLon = lons[222]

output_stream = ByteArrayOutputStream()
data_output_stream = DataOutputStream(output_stream)
data_output_stream.writeInt(len(ids))
for i in range(len(ids)):
    data_output_stream.writeUTF(ids[i])

for i in range(len(lats)):
    data_output_stream.writeDouble(lats[i])

for i in range(len(lons)):
    data_output_stream.writeDouble(lons[i])

for i in range(len(ids)):
    data_output_stream.writeDouble(0)  # opportunities

input_stream = ByteArrayInputStream(output_stream.toByteArray())

request.destinationPointSets = JavaLangReflectArray.newInstance(PointSet, 1)
request.destinationPointSets[0] = FreeFormPointSet(input_stream)

# travel_time_computer = TravelTimeComputer(request, transport_network)
# results = travel_time_computer.computeTravelTimes()
