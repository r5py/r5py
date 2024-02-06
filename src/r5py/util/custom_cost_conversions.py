import jpype
import jpype.imports

import com.conveyal.r5
from r5py.util.exceptions import CustomCostConversionError


def convert_python_dict_to_java_hashmap(custom_cost_data):
    """
    Convert custom cost python dict items into the Java HashMap (Long, Double) format.

    Arguments:
    ----------
    custom_cost_data : Dict[str, float]
        custom cost data to be used in routing.
        str key is osmid, float value is custom costs per edge (way)

    Returns:
    --------
    custom_cost_java_hashmap : jpype.java.util.HashMap
        custom cost data in Java HashMap format
    """
    custom_cost_java_hashmap = jpype.JClass("java.util.HashMap")()
    for key, value_cost in custom_cost_data.items():
        long_key = jpype.JLong(key)
        int_value = jpype.JDouble(value_cost)
        custom_cost_java_hashmap.put(long_key, int_value)
    return custom_cost_java_hashmap


def convert_custom_cost_data_to_custom_cost_instance(
    name, sensitivity, custom_cost_data, allow_null_costs
):
    """
    Convert custom cost data into the Java CustomCostField instance.

    Arguments:
    ----------
    name : str
        name of the custom cost instance
    sensitivity : float
        sensitivity of the custom cost field
        this is used to get different route suggestions by weighting the custom cost field
    custom_cost_data : jpype.java.util.HashMap[Long, Double]
        custom cost data to be used in routing.
    allow_null_costs : bool
        whether to allow null costs in routing. Default is True.
        If set to False and ANY edges have null costs, routing will fail.
        Only use False if you are sure that ALL edes have custom costs.

    Returns:
    --------
    custom_cost_java_instance : com.conveyal.r5.rastercost.CustomCostField
        custom cost data in Java CustomCostField instance format
    """
    return com.conveyal.r5.rastercost.CustomCostField(
        jpype.JString(name),
        jpype.JDouble(sensitivity),
        custom_cost_data,
        allow_null_costs,
    )


def convert_custom_cost_instances_to_java_list(custom_cost_instances):
    """
    Convert custom cost instance(s) into the Java List format.
    R5 expects a List of CustomCostField instances.

    Parameters:
    -----------
    custom_cost_instances : List[com.conveyal.r5.rastercost.CustomCostField]
        Python list of Custom cost instance(s)

    Returns:
    --------
    custom_cost_java_list : jpype.java.util.List
        Java array list of CustomCostField instances
    """
    CostField = jpype.JClass("com.conveyal.r5.rastercost.CustomCostField")
    custom_cost_java_array = jpype.JArray(CostField)(custom_cost_instances)
    return CostField.wrapToEdgeStoreCostFieldsList(custom_cost_java_array)


def convert_java_hashmap_to_python_dict(hashmap):
    """
    Convert Java HashMap to Python dict.

    Arguments:
    ----------
    hashmap : jpype.java.util.HashMap
        Java HashMap to be converted to Python dict

    Returns:
    --------
    base_travel_time_values : Dict[str, float]
        Python dict with str keys and float values
    """
    base_travel_time_values = {}
    for key, value in hashmap.entrySet().toArray():
        base_travel_time_values[str(key)] = float(value)
    return base_travel_time_values


def convert_python_custom_costs_to_java_custom_costs(
    names, sensitivities, custom_cost_data_sets, allow_null_costs
):
    """
    Convert custom cost python dict items into the Java HashMap (Long, Double) format.

    Returns:
    --------
    custom_cost_list: jpype.java.util.List
        java list of custom cost instance(s)
    """
    try:
        custom_cost_instances = []
        for name, sensitivity, custom_cost in zip(
            names, sensitivities, custom_cost_data_sets
        ):
            # convert custom cost item from python dict to java hashmap
            java_hashmap_custom_cost = convert_python_dict_to_java_hashmap(custom_cost)
            # convert custom cost params to java customCostField instance
            custom_cost_instance = convert_custom_cost_data_to_custom_cost_instance(
                name, sensitivity, java_hashmap_custom_cost, allow_null_costs
            )
            custom_cost_instances.append(custom_cost_instance)
        # convert all java custom cost instances to java list
        custom_cost_list = convert_custom_cost_instances_to_java_list(
            custom_cost_instances
        )
        return custom_cost_list
    except:
        raise CustomCostConversionError(
            "Failed to convert python custom cost data to java custom cost data. Custom_cost_data must be provided for custom cost transport network"
        )
