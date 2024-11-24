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
        standarize_items = [item.replace('\"', '\'') for item in final_items]
        standarize_items = [item.replace('`', '\'') for item in standarize_items]
        if standarize_items == ["0-9"]:
            return [f'{i}' for i in range(0, 10)]
        return standarize_items
    else:
        print("No match found.")
        return []

def add_ref(path, function_name, composition_rule='__init__'):
    """
        path: string of the form module/object/
        function_name: string name of the function
        composition_rule: parent rule of this function, points
        to file __init__
    """
    file_construct = f"{path}/{composition_rule}.json"
    # Read file
    with open(file_construct, 'r') as file:
        data = json.load(file)
    file.close()
    # Add reference
    add_f = True
    for prop, v in data["properties"].items():
        if prop.lower() == function_name.lower() or prop == function_name:
            add_f = False
    if add_f:
        new_ref = dict({
            function_name : {
                "$ref": f"{path}/{function_name}"
            }
        })
        data["properties"].update(new_ref)
    
    # Update
    with open(file_construct, 'w') as file:
        json.dump(data, file, indent=4)
    file.close()


def find_docstring_params(func, func_docstring, json_schema):
    mandatory_p = []
    opt_defaults = []
    pattern = rf"{func}\([^)]*\)"
    # Search for the pattern in the text
    match = re.search(pattern, func_docstring)    
    if match:
        definition = match.group()
        # Find declaration with default assignments
        if '=' in definition:
            pattern = r"(\w+)(?==)"
            opt_defaults = re.findall(pattern, definition)
        else:
            pattern = r"\(([^()]*)\)"
            match = re.search(pattern, definition)
            if match:
                def_params = match.group(1)
                def_paramss = def_params.split("[")
                for dp in def_paramss:
                    dps = dp.split(",")
                    dps = [d.strip().replace("]", "") if d != '' else d for d in dps]
                    if len(dps) > 2:
                        mandatory_p = dps
                    elif len(dps) == 2:
                        opt_defaults.append(dps[1])
                    elif dps[0] != '':
                         opt_defaults.append(dps[0])
    
    for param_name in mandatory_p:
            json_schema["properties"][param_name] = {
                    "type": ['value']
                }
    for param_name in opt_defaults:
        json_schema["properties"][param_name] = {
                "type": ['value']
            }
    # Add required parameters for function
    json_schema["required"] = mandatory_p
    
    return json_schema

def build_json(path, function_name, function, composition_rule, kwargs, module_name):
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
    time_optional = 0
    time_default = 0
    if "param_map" in function:
        for k, v in function["param_map"].items():
            k_name = k.split(":")[0]
            if "args" in k or k == "kw" or k == "kwds" or k.startswith("\\") or k == "...":
                if kwargs == False:
                    continue
                else:
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
                        lst_enum = create_enum(param_type_info)
                        if len(lst_enum) > 0:
                            json_schema["properties"][k_name] = {
                                "enum": create_enum(param_type_info)
                            }
                        else:
                            json_schema["properties"][k_name] = {
                                "type": ["value"]
                            }
                    #  Add required parameters
                    if "optional" in function["param_map"][k]:
                        if  function["param_map"][k]["optional"] == False:
                            json_schema["required"].append(k_name)
                            time_optional = time_optional+1
                    # This is to be changed maybe
                    elif ('default ''' in param_type_info):
                        json_schema["required"].append(k_name)
                        time_optional = time_optional+1
                    elif ('optional' not in param_type_info):
                        json_schema["required"].append(k_name)
                    else:
                        time_optional = time_optional+1

                else:
                    json_schema["properties"][k_name] = {
                            "type": ["value"]
                    }
        # If everything is required, because of default, save just the first var a required
        if time_optional == 0:
            if len(json_schema["required"]) > 0:
                json_schema["required"] = json_schema["required"][:1]
    elif "param_names" in function:
        for i in range(0, len(function["param_names"])):
            param_name = function["param_names"][i].split(':')[0]
            if ("args" in param_name or param_name == "kwds" or param_name == "kw" or param_name == "..." or param_name.startswith("\\")) and kwargs == False:
                continue
            # Unknown type info mark as unknown
            if ("param_types" not in function) or (i >= len(function["param_types"])):
                json_schema["properties"][param_name] = {
                    "type": ['value']
                }
            else:
                param_type = function["param_types"][i].strip()
            
                if "args" in param_name or param_name == "kw" or param_name == "kwds" or param_name == "..." or param_name.startswith("\\"):
                    if kwargs == False:
                        continue
                    else:
                        json_schema["properties"]["kwargs"] = {
                            "type":["kwargs"]
                        }
                else:
                    sep_type = param_type.split('|')
                    param_type_vars = return_types(sep_type)
                    if param_name in  json_schema["properties"]:
                        json_schema["properties"][param_name]['type'] =  json_schema["properties"][param_name]['type'] + param_type_vars[0]
                    else:
                        json_schema["properties"][param_name] = {
                            "type": param_type_vars[0]
                        }
                    param_t_str = [param.strip() for param in sep_type]
                    if 'None' not in param_t_str:
                        json_schema["required"].append(param_name)
                    else:
                        time_default = time_default + 1
        # If everything is required, because of default, save just the first var a required
        if time_default == 0:
            if len(json_schema["required"]) > 0:
                json_schema["required"] = json_schema["required"][:1]
    elif "function_docstring" in function and function["function_docstring"] is not None:
        json_schema = find_docstring_params(function["function"], function["function_docstring"], json_schema)
    elif "class_docstring" in function and function["class_docstring"] is not None:
        json_schema = find_docstring_params(function_name, function["class_docstring"], json_schema)

    # Add return type if any
    if function_name == "__init__":
        json_schema["return"] = ""
        json_schema["biggerRule"] = ""
        if composition_rule != module_name:
            json_schema["return"] = composition_rule
        else:
            json_schema["return"] = module_name
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

def add_property_module(module, builtin_class, composition_rule='__init__'):
    """
        Adds the class as a constant to the module
    """
    file_construct = f"{module}/{module}/{composition_rule}.json"
    # Read file
    try:
        with open(file_construct, 'r') as file:
            data = json.load(file)
        file.close()
    except:
        data = {
                "type": "object",
                "title": "__init__",
                "properties": {},
                "return": module,
                "required": [],
                "biggerRule": "",
                "additionalProperties": False
            }

    parts = builtin_class.split(module + '.')
    if len(parts)>1:
        name = parts[1]
    else:
        return
    
    new_builtin = dict({
            name : {
                "enum": [""]
            }
        })
    
    data["properties"].update(new_builtin)
    
    # Update
    with open(file_construct, 'w') as file:
        json.dump(data, file, indent=4)
    file.close()

def build_init(module, data, kwargs):
    """
        Creates documents based on init
    """

    # Iterate through the list to find constructors
    function_set = set()
    builtin_set = set()
    for function in data:
        if "klass" in function and "function" in function:
            if function["module"]:
                submodule = function["module"]
            else:
                submodule = "NA"
            if function["klass"] not in function_set or function["klass"] not in builtin_set:
                # Constructors and attributes, without private functions
                if (function["function"] == "__init__" or function["function"] == "__builtins__") and '._' not in function["klass"]:
                    if not function["klass"].startswith('_'):
                        function["klass"] = function["klass"].replace("enum ", "")
                        function_rule = function["klass"].replace('.', '-')
                        function_rule = function["klass"].replace('_', '-')
                        path_to_function = f"{module}/{function_rule}"
                        os.makedirs(path_to_function, exist_ok=True)
                        if function["function"] == "__init__":
                            function_set.add(function["klass"])
                            build_json(path_to_function, "__init__", function, function_rule, kwargs, module)
                            add_property_module(module, function["klass"])
                        elif function["function"] == "__builtins__":
                            if function_rule not in function_set:
                                builtin_set.add(function["klass"])
                            build_json(path_to_function, "__builtins__", function, function_rule, kwargs, module)
                            add_property_module(module, function["klass"], "__builtins__")

    # Iterate through the list to find non-private functions from the constructors above
    for function in data:
        if "klass" in function and "function" in function:
            # Omits functions different from init and private functions
            function["klass"] = function["klass"].replace("enum ", "")
            function_rule = function["klass"].replace('.', '-')
            function_rule = function["klass"].replace('_', '-')
            if not function["function"].startswith('_'):
                if function_rule in function_set and function["function"] != "__init__":
                    path_to_function = f"{module}/{function_rule}"
                    build_json(path_to_function, function["function"], function, function_rule, kwargs, "")
                    add_ref(path_to_function, function["function"])
                if function_rule in builtin_set and function["function"] != "__builtins__":
                    path_to_function = f"{module}/{function_rule}"
                    build_json(path_to_function, function["function"], function, function_rule, kwargs, "")
                    add_ref(path_to_function, function["function"], "__builtins__")
        elif function["module"] in builtin_set and "function" not in function:
            # Add class objects this is particular for CPython modules, such as datetime
            function_name = function["klass"].split('.')[-1]
            if not function_name.startswith('_'):
                path_to_function = f"{module}/{function_name}"
                build_json(path_to_function, function_name, function, function_name, kwargs, "")
                add_ref(path_to_function, function_name, "__builtins__")

def consider_function(func_str):
    """
        Accepts wrappers and non-private functions
        Returns bool_to_add, function name, and biggerRule
    """
    if func_string.find('._') > 0:
        return False, "", ""

    idx = func_string.find('__')
    if idx > 0:
        # Regular expression pattern
        pattern = r"__([^_]+)__"
        # Find all matches
        matches = re.findall(pattern, func_string)
        if idx > 0:
            return True, matches[0],func_str[0:idx-1]
    else:
        lst_functions = func_str.split('.')
        return True, lst_functions[-1], '.'.join(lst_functions[0:-1])

def convert_data_to_schema(module, file_path, kwargs):
    """
        module: name of the module to transform
    """

    # Create folder for the module
    os.makedirs(module, exist_ok=True)

    # Read json file
    with open(file_path, 'r') as file:
        data = json.load(file)

    build_init(module, data, kwargs)
    
    # Save files
    with open(f"{module}/{module}.txt", 'w') as file_one:
        for root, dirs, files in os.walk(module):
            # Create a file for each directory
            dir_name = os.path.basename(root)
            output_file_path = os.path.join(root, f'{dir_name}.txt')
            with open(output_file_path, 'w') as file:
                for name in files:
                    if '.json' in name:
                        file_path = os.path.join(root, name)
                        file.write(file_path + '\n')
                        file_one.write(file_path + '\n')

    # Global file
    global_file_path = f"{module}.txt"
    with open(global_file_path, 'w') as file_two:
        file_two.write(f"{module}/{module}.txt" + '\n')

if __name__ == "__main__":
    """ Execute modules' jsons into schema """
    """ Example usage: python grammar/module_to_schema.py --module='pandas' --file='pandas.json' --kwargs=False"""
    """ Example usage: python grammar/module_to_schema.py --module='numpy' --file='Data/graph4code/output/modules_out/numpy/numpy.json' --kwargs=False """
    parser = argparse.ArgumentParser(description="Transform module to json schema.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--module", help="Name of the module to transform.")
    parser.add_argument("--file", help="Path to the json file.")
    parser.add_argument("--kwargs", help="Add kwargs as parameter.")

    args = parser.parse_args()
    convert_data_to_schema(args.module, args.file, eval(args.kwargs))