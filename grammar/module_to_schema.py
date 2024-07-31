import argparse
import json
import os
import re
import pandas as pd


def return_types(type_str):
    """
        Return a string of the generic type of the function parameter in the grammar
        type_str: list of types of function'parameter, separated by comma
    """
    full_type = []
    for e in type_str:
        # Divide by or
        e_full = e.split('or')
        for t in e_full:
            # Divide by parenthesis
            # Add to set if token larger than 2
            # Remove none, default and optional from set
            t_comparison =  t.strip().lower()
            if  'none' not in t_comparison and 'default' not in t_comparison and 'optional' not in t_comparison:
                full_type.append(t_comparison)
    
    if len(full_type) == 0:
        # More than two options,
        return (['value'], full_type)

    # Valid set of knowns
    known_vars = set({'integer', 'string', 'array', 'bool', 'array', 'object'})
    return_lst = []
    for chosen_type in full_type:
        if chosen_type.startswith('int'):
                return_lst.append('integer')
        elif chosen_type.startswith('str'):
                 return_lst.append('string')
        elif chosen_type.startswith('list'):
                 return_lst.append('array')
        elif chosen_type.startswith('bool'):
                 return_lst.append('bool')
        elif chosen_type.startswith('float'):
                 return_lst.append('number')
        elif chosen_type.startswith('dict'):
                 return_lst.append('object')
        else:
             return (['value'], full_type)
    return (return_lst, full_type)

def create_enum(type_str):
    """
        type_str: string in set format of available options
    """

    # Regex to match the contents inside the curly braces
    pattern = r"\{([^}]*)\}"
    
    # Find the contents inside the curly braces
    match = re.search(pattern, type_str)
    if match:
        contents = match.group(1)  # Get the matched group (the contents inside the curly braces)
        
        # Split the contents by comma and strip any surrounding whitespace and quotes
        items = [item.strip() for item in contents.split(',')]
        final_items = [element.strip() for item in items for element in re.split(r'[/]|\s+or\s+', item)]
        return final_items
    else:
        print("No match found.")
        return []

def build_json(path, function_name, function, composition_rule):
    """
        path: string of the form module/object/
        function_name: string name of the function
        function_dct: docstring dictionary of the function
        composition_rule: parent rule of this function
    """
    file_to_save = f"{path}/{function_name}.json"
    json_schema = {
        "type": "object",
        "title": function_name,
        "properties": {
        },
        "return": [],
        "required": [],
        "biggerRule": composition_rule,
        "additionalProperties": False
    }
    # 1. Fill properties
    # 2. Save types for future use
    if "param_map" in function:
        for k, v in function["param_map"].items():
            k_name = k.split(":")[0]
            if "kwargs" in k:
                json_schema["properties"]["kwargs"] = {
                    "type": ["kwargs"]
                }
            else:
                if 'type' in function["param_map"][k]:
                    param_type_info = function["param_map"][k]['type']
                    if "{" not in param_type_info:
                        t = param_type_info.split(',')
                        final_type = return_types(t)
                        json_schema["properties"][k_name] = {
                            "type": return_types(t)[0]
                        }
                    else:
                        # Create dictionary enum
                        json_schema["properties"][k_name] = {
                            "type": ["dictionary"]
                        }
                        json_schema["properties"][k_name] = {
                            "enum": create_enum(param_type_info)
                        }
                    
                    #  Add required parameters
                    if "optional" in function["param_map"][k]:
                        if  function["param_map"][k]["optional"] == False:
                            json_schema["required"].append(k_name)
                    elif ('default' not in param_type_info) and ('optional' not in param_type_info):
                        json_schema["required"].append(k_name)

                else:
                    json_schema["properties"][k_name] = {
                            "type": ["value"]
                    }
    else:
        if "param_names" in function:
            for i in range(0, len(function["param_names"])):
                param_name = function["param_names"][i].split(':')[0]
                # Unknown type info mark as unknown
                if ("param_types" not in function) or (i >= len(function["param_types"])):
                    json_schema["properties"][param_name] = {
                        "type": ['value']
                    }
                else:
                    param_type = function["param_types"][i].strip()
                
                    if param_name == "kwargs":
                        json_schema["properties"]["kwargs"] = {
                            "type":["kwargs"]
                        }
                    else:
                        sep_type = param_type.split('|')
                        param_type_vars = return_types(sep_type)
                        if function_name == '__init__' and composition_rule == 'pandas.DataFrame':
                            print(sep_type)
                            print(param_type_vars)
                        if param_name in  json_schema["properties"]:
                            json_schema["properties"][param_name]['type'] =  json_schema["properties"][param_name]['type'] + param_type_vars[0]
                        else:
                            json_schema["properties"][param_name] = {
                                "type": param_type_vars[0]
                            }
                        param_t_str = [param.strip() for param in sep_type]
                        if 'None' not in param_t_str:
                            json_schema["required"].append(param_name)
    
    # Add return type if any
    if function_name == "__init__":
        json_schema["return"] = composition_rule
        json_schema["biggerRule"] = ""
    elif "ret_types" in function:
        r_type = function["ret_types"].split('|')
        for r in r_type:
            json_schema["return"].append(r.strip())

    try: 
        with open(file_to_save, 'w') as json_file:
            json.dump(json_schema, json_file, indent=4)
        print(f"File saved: {file_to_save}")
    except (re.error, json.JSONDecodeError, IOError) as e:
        print(f"An error occurred: {e}, in file: {file_to_save}")


def convert_data_to_schema(module):
    """
        module: name of the module to transform
    """

    # Create folder for the module
    os.makedirs(module, exist_ok=True)

    # Read json file
    json_file = f"{module}.json"
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Iterate through the list to find constructors
    function_set = set()
    for function in data:
        if "klass" in function and "function" in function:
            if function["klass"] not in function_set:
                # Constructors and attributes, without private functions
                if function["function"] == "__init__" and '._' not in function["klass"]:
                    if 'pandas' in function["klass"]:
                        function_rule = function["klass"].replace('.', '-')
                        function_rule = function["klass"].replace('_', '-')
                        function_set.add(function_rule)
                        path_to_function = f"{module}/{function_rule}"
                        os.makedirs(path_to_function, exist_ok=True)
                        build_json(path_to_function, "__init__", function, function_rule)

    # Iterate through the list to find non-private functions from the constructors above
    for function in data:
        if "klass" in function and "function" in function:
            # Omits functions different from init and private functions
            function_rule = function["klass"].replace('.', '-')
            function_rule = function["klass"].replace('_', '-')
            if function_rule in function_set and function["function"] != "__init__" and not function["function"].startswith('_'):
                path_to_function = f"{module}/{function_rule}"
                build_json(path_to_function, function["function"], function, function_rule)

if __name__ == "__main__":
    """ Execute modules' jsons into schema """
    """ Example usage: python module_to_schema.py --module='pandas' """
    parser = argparse.ArgumentParser(description="Transform module to json schema.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--module", help="Name of the module to transform.")

    args = parser.parse_args()
    convert_data_to_schema(args.module)