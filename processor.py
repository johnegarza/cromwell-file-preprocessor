import os, yaml

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

with open("test_yaml.yaml") as yaml_file:
    data = yaml.load(yaml_file)

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
