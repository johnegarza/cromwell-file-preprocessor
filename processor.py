import os, yaml, sys, shutil, subprocess
from collections import defaultdict

def dict_processor(raw_dict, dest_dir, parameter_name, parameter_map):
    if "class" in raw_dict:
        if raw_dict["class"] == "File":
            abs_path = os.path.abspath(raw_dict["path"])
            #make a map from parameter name to original path, to help
            #find potential cwl secondaryFiles later
            parameter_map[parameter_name].append(abs_path)
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

        #saving the following block for now, in case we decide to try links again in the future
        '''
        src_name = os.path.split(abs_src_path)[1]
        link_name = dest_path + src_name
        print link_name
        subprocess.call(["ln", "-s", abs_src_path, link_name])
        '''
    else:
        subprocess.call(["cp", "-r", abs_src_path, dest_path])
        
    #return new path to file/directory so it can be updated in the processed output
    #TODO should this be an absolute path?
    return dest_path + os.path.split(abs_src_path)[1]

def str_to_list(string):
    last_char = len(string) - 1
    if string[0] != "[" or string[last_char] != "]":
        assert(False) #TODO handle this better
    raw = string[1:last_char] #[inclusive, exclusive]
    return raw.split(",")

def secondary_handler(file_string, parameter_path, dest_dir):
    param_dir = os.path.split(parameter_path)[0]
    basename = os.path.split(parameter_path)[1]
    extension_list = str_to_list(file_string)
    for ext in extension_list:
        count = ext.count("^")
        if count != 0:
            basename = basename.split(".")
            ext_remove = len(basename) - count
            basename = basename[:ext_remove]
            basename = ".".join(basename)
            ext = ext.replace("^", "")
        if param_dir[-1] != "/":
            param_dir += "/" #TODO look into this- might always be the case, if so can add this in earlier without the if statement
        secondary_file_name = param_dir + basename + ext
        if os.path.exists(secondary_file_name):
            copier(secondary_file_name, dest_dir, True) #TODO technically it's possible to specify directories as secondaryFiles, need to implement handling
        else:
            #assert(False) #TODO handle this
            print(secondary_file_name + " could not be found")

input_yaml = sys.argv[1]
yaml_dir = os.path.split(input_yaml)[0]
yaml_name = os.path.split(input_yaml)[1]
processed_yaml = "staged_" + yaml_name
dest_dir = sys.argv[2]
if dest_dir[-1] != "/":
    dest_dir += "/"
workflow_cwl = sys.argv[3]
#curr_dir = os.getcwd()

#load yaml into memory as a dictionary
with open(input_yaml) as yaml_file:
    data = yaml.load(yaml_file)

#switch into the same directory as the yaml file, to ensure
#os.path.abspath() properly resolves any relative paths
if yaml_dir != "":
    os.chdir(yaml_dir)

subprocess.call(["mkdir", "-p", dest_dir])
parameter_to_path = defaultdict(list)

final_output = {}
for key in data:
    if type(data[key]) is list:
        new_list = []
        for element in data[key]:
            if type(element) is dict:
                processed = dict_processor(element, dest_dir, key, parameter_to_path)
                new_list.append(processed)
            else:
                new_list.append(element) #TODO what if this is another list? make this recursive to handle any level of nesting
        final_output[key] = new_list
    elif type(data[key]) is dict:
        processed = dict_processor(data[key], dest_dir, key, parameter_to_path)
        final_output[key] = processed
    else:
        final_output[key] = data[key]

#check for secondaryFiles from top level cwl
#TODO cwl can be parsed as yaml- this will be more robust
with open(workflow_cwl) as cwl_file:
    lines = cwl_file.readlines()
    found_inputs = False
    for line in lines:
        if found_inputs:
            if line[0] != " ": #no indents, so next major section
                break
            line_arr = line.strip().replace(" ", "").replace('"','').split(":")
            if line_arr[1] == "":
                parameter_name = line_arr[0]
            elif line_arr[0].lower() == "secondaryfiles":
                parameter_paths = parameter_to_path[parameter_name] #TODO error possible here if there's a mistake in the yaml and parameters don't have a one to one mapping with those in the workflow inputs section
                for parameter_path in parameter_paths:
                    secondary_handler(line_arr[1], parameter_path, dest_dir)
                
        if line.strip() == "inputs:":
            found_inputs = True
with open(processed_yaml, "w+") as output_file:
    yaml.dump(final_output, output_file)

