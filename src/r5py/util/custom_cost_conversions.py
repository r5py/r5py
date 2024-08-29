import jpype
import jpype.imports

import com.conveyal.r5
from r5py.util.exceptions import CustomCostConversionError


def convert_python_dict_to_java_hashmap(custom_cost_segment_weight_factors):
    """
    Convert custom cost python dict items into the Java HashMap (Long, Double) format.

    Arguments:
    ----------
    custom_cost_segment_weight_factors : Dict[str, float]

    Returns:
    --------
    custom_cost_java_hashmap : jpype.java.util.HashMap
        Custom cost factors in Java HashMap format.
    """
    JInteger = jpype.JClass("java.lang.Integer")
    custom_cost_java_hashmap = jpype.JClass("java.util.HashMap")()
    for key, value_cost in custom_cost_segment_weight_factors.items():
        int_key = JInteger(int(key))
        int_value = jpype.JDouble(value_cost)
        custom_cost_java_hashmap.put(int_key, int_value)
    return custom_cost_java_hashmap


def convert_custom_cost_segment_weight_factors_to_custom_cost_instance(
    name, sensitivity, custom_cost_segment_weight_factors, allow_missing_osmid
):
    """
    Convert custom cost factors into the Java CustomCostField instance.

    Arguments:
    ----------
    name : str
    sensitivity : float
    custom_cost_segment_weight_factors : jpype.java.util.HashMap[Long, Double]
    allow_missing_osmid : bool

    Returns:
    --------
    custom_cost_java_instance : com.conveyal.r5.rastercost.CustomCostField
        Custom cost factors in Java CustomCostField instance format.
    """
    return com.conveyal.r5.rastercost.CustomCostField(
        jpype.JString(name),
        jpype.JDouble(sensitivity),
        custom_cost_segment_weight_factors,
        jpype.JBoolean(allow_missing_osmid),
    )


def convert_custom_cost_instances_to_java_list(custom_cost_instances):
    """
    Convert custom cost factor instance(s) into the Java List format.
    R5 expects a List of CustomCostField instances.

    Parameters:
    -----------
    custom_cost_instances : List[com.conveyal.r5.rastercost.CustomCostField]
        Python list of Custom cost factor instance(s).

    Returns:
    --------
    custom_cost_java_list : jpype.java.util.List
        Java array list of CustomCostField instances.
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
        Java HashMap to be converted to Python dict.

    Returns:
    --------
    base_travel_time_values : Dict[str, float]
        Python dict with str keys and float values.
    """
    base_travel_time_values = {}
    for key, value in hashmap.entrySet().toArray():
        base_travel_time_values[str(key)] = float(value)
    return base_travel_time_values


def convert_python_custom_costs_to_java_custom_costs(
    names, sensitivities, custom_cost_segment_weight_factors, allow_missing_osmids
):
    """
    Convert custom cost factors python dict items into the Java HashMap (Long, Double) format.

    Arguments:
    ----------
    names : List[str]
        Names of the custom cost factor instance(s).
    sensitivities : List[float]
        Sensitivities of the custom cost factor field(s).
        This is used to get different route suggestions by weighting the custom cost factor field.
    custom_cost_segment_weight_factors : List[Dict[str, float]]
        Custom cost data to be used in routing.
        Str key is osmid, float value is custom costs per road segment.
    allow_missing_osmids : List[bool]
        Whether to allow null costs in routing.
        Default is True.
        If set to False and ANY edge osmid is not found during routing, will crash the routing.
        Only use False if you are sure that ALL edge osmids are found from custom_cost_segment_weight_factors.
    Returns:
    --------
    custom_cost_list: jpype.java.util.List
        Java list of custom cost factor instance(s).
    """
    try:
        custom_cost_instances = []
        for name, sensitivity, custom_cost, allow_missing_osmid in zip(
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        ):
            java_hashmap_custom_cost = convert_python_dict_to_java_hashmap(custom_cost)
            custom_cost_instance = (
                convert_custom_cost_segment_weight_factors_to_custom_cost_instance(
                    name, sensitivity, java_hashmap_custom_cost, allow_missing_osmid
                )
            )
            custom_cost_instances.append(custom_cost_instance)
        custom_cost_list = convert_custom_cost_instances_to_java_list(
            custom_cost_instances
        )
        return custom_cost_list
    except CustomCostConversionError as e:
        raise CustomCostConversionError(
            "Failed to convert from python to java for custom cost factors. custom_cost_segment_weight_factors must be provided for custom cost transport network"
        ) from e
