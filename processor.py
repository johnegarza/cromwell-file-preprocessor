import os, yaml, sys, shutil

#TODO handle secondaryFiles
#TODO handle JSON?

def dict_processor(raw_dict, dest_dir):
    if "class" in raw_dict:
        if raw_dict["class"] == "File":
            abs_path = os.path.abspath(raw_dict["path"])
            raw_dict["path"] = copier(abs_path, dest_dir, True)
            #print(abs_path)
        elif raw_dict["class"] == "Directory":
            abs_path = os.path.abspath(raw_dict["path"])
            raw_dict["path"] = copier(abs_path, dest_dir, False)
            #return raw_dict
    else:
        return raw_dict

def copier(abs_src_path, dest_path, is_file):
    if is_file:
        shutil.copy(abs_src_path, dest_path)
    else:
        shutil.copytree(abs_src_path, dest_path)
    #return new path to file/directory so it can be updated in the processed output
    #TODO should this be an absolute path?
    return dest_path + os.path.split(abs_src_path)[1]

input_yaml = sys.argv[1]
yaml_dir = os.path.split(input_yaml)[0]
dest_dir = sys.argv[2]
#curr_dir = os.getcwd()

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
                processed = dict_processor(element, dest_dir)
                new_list.append(processed)
            else:
                new_list.append(element)
        final_output[key] = new_list
    elif type(data[key]) is dict:
        processed = dict_processor(data[key], dest_dir)
        final_output[key] = processed
    else:
        final_output[key] = data[key]

## sort final_output alphabetically (?), then dump
print yaml.dump(final_output)
