import os, yaml, sys, shutil, subprocess

#TODO handle secondaryFiles
#TODO handle JSON?

def dict_processor(raw_dict, dest_dir):
    if "class" in raw_dict:
        if raw_dict["class"] == "File":
            abs_path = os.path.abspath(raw_dict["path"])
            raw_dict["path"] = copier(abs_path, dest_dir, True)
        elif raw_dict["class"] == "Directory":
            abs_path = os.path.abspath(raw_dict["path"])
            raw_dict["path"] = copier(abs_path, dest_dir, False)
    return raw_dict

#TODO handle edge cases- what to do with naming collisions, links
def copier(abs_src_path, dest_path, is_file):
    if is_file:
        subprocess.call(["cp", "-n", abs_src_path, dest_path])
        #TODO
        #note- can check return code and handle collisions accordingly; -n is a temporary
        #fix for early development
    else:
        subprocess.call(["cp", "-r", abs_src_path, dest_path])
        
    #return new path to file/directory so it can be updated in the processed output
    #TODO should this be an absolute path?
    return dest_path + os.path.split(abs_src_path)[1]

input_yaml = sys.argv[1]
yaml_dir = os.path.split(input_yaml)[0]
yaml_name = os.path.split(input_yaml)[1]
processed_yaml = "staged_" + yaml_name
dest_dir = sys.argv[2]
if dest_dir[-1] != "/":
    dest_dir += "/"
#curr_dir = os.getcwd()

#load yaml into memory as a dictionary
with open(input_yaml) as yaml_file:
    data = yaml.load(yaml_file)

#switch into the same directory as the yaml file, in order
#to properly resolve any relative paths it specifies
if yaml_dir != "":
    os.chdir(yaml_dir)

subprocess.call(["mkdir", "-p", dest_dir])

final_output = {}
for key in data:
    if type(data[key]) is list:
        new_list = []
        for element in data[key]:
            if type(element) is dict:
                processed = dict_processor(element, dest_dir)
                new_list.append(processed)
            else:
                new_list.append(element) #TODO what if this is another list? make this recursive to handle any level of nesting
        final_output[key] = new_list
    elif type(data[key]) is dict:
        processed = dict_processor(data[key], dest_dir)
        final_output[key] = processed
    else:
        final_output[key] = data[key]

with open(processed_yaml, "w+") as output_file:
    yaml.dump(final_output, output_file)

