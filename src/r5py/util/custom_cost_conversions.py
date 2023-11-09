import jpype
import jpype.imports

import com.conveyal.r5


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
    name, sensitivity, custom_cost_data
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
        
    Returns:
    --------
    custom_cost_java_instance : com.conveyal.r5.rastercost.CustomCostField
        custom cost data in Java CustomCostField instance format
    """

    return com.conveyal.r5.rastercost.CustomCostField(
        jpype.JString(name), jpype.JDouble(sensitivity), custom_cost_data
    )


def convert_custom_cost_instances_to_java_list(*custom_cost_instances):
    """
    Convert custom cost instance(s) into the Java List format.
    R5 expects a List of CustomCostField instances.

    Parameters:
    -----------
    *custom_cost_instances : com.conveyal.r5.rastercost.CustomCostField
        Custom cost instance(s) to be used in routing.

    Returns:
    --------
    custom_cost_java_list : jpype.java.util.List
        List of CustomCostFiled instances in Java format
    """
    CostField = jpype.JClass("com.conveyal.r5.rastercost.CustomCostField")
    return CostField.wrapToEdgeStoreCostFieldsList(custom_cost_instances)
