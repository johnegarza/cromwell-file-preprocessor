import os, yaml, sys

def dict_processor(raw_dict):
    if "class" in raw_dict:
        if raw_dict["class"] == "File":
            abs_path = os.path.abspath(raw_dict["path"])
            print(abs_path)
        elif raw_dict["class"] == "Directory":
            #TODO fix
            return raw_dict
        else:
            return raw_dict
    else:
        return raw_dict

input_yaml = sys.argv[1]
yaml_dir = os.path.split(input_yaml)[0]
curr_dir = os.getcwd()

with open(input_yaml) as yaml_file:
    data = yaml.load(yaml_file)

if yaml_dir != "":
    os.chdir(yaml_dir) #so os.path.abspath will work properly

final_output = {}
for key in data:
    if type(data[key]) is list:
        new_list = []
        for element in data[key]:
            if type(element) is dict:
                processed = dict_processor(element)
                new_list.append(processed)
            else:
                new_list.append(element)
        final_output[key] = new_list
    elif type(data[key]) is dict:
        processed = dict_processor(data[key])
        final_output[key] = processed
    else:
        final_output[key] = data[key]

## sort final_output alphabetically (?), then dump
