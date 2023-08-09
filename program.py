# Author: Dr. Shayan Taheri.
# File Content: The Python program for parsing a Verilog netlist and ...
# ... counting the number of instances of each module.

import re
import sys

# Function for parsing a Verilog netlist and ...
# ... positioning the extracted information into a dictionary/structure.

def parse_verilog(filename):
    with open(filename, 'r') as f:
        data = f.read()
        
    modules = re.findall(r'module ([a-zA-Z0-9_]+) \(', data)
    module_data = {}
    for module in modules:
        module_section = re.search(r'module ' + module + r'[^;]*;(.*?)endmodule', data, re.DOTALL).group(1)
        inputs = re.findall(r'input ([a-zA-Z0-9_\[\]:]+);', module_section)
        outputs = re.findall(r'output ([a-zA-Z0-9_\[\]:]+);', module_section)
        wires = re.findall(r'wire ([a-zA-Z0-9_\[\]:]+);', module_section)
        regs = re.findall(r'reg ([a-zA-Z0-9_\[\]:]+);', module_section)
        instances = re.findall(r'([a-zA-Z0-9_]+) ([a-zA-Z0-9_]+) \(', module_section)
        instance_data = {}
        for inst_module, inst_name in instances:
            inst_ports = re.findall(r'\.([a-zA-Z0-9_]+)\(([a-zA-Z0-9_\[\]:]+)\)', module_section)
            instance_data[inst_name] = {
                'module': inst_module,
                'input_ports': {port_name: net_name for port_name, net_name in inst_ports if port_name in inputs},
                'output_ports': {port_name: net_name for port_name, net_name in inst_ports if port_name in outputs}
            }
        
        module_data[module] = {
            'Inputs': inputs,
            'Outputs': outputs,
            'Wires': wires,
            'Registers': regs,
            'Instances': instance_data
        }
    
    return module_data

# Function for counting the number of instances of each module and primitive.

def count_instances(module_data, start_module):
    count = {}
    instances = module_data[start_module]['Instances']
    
    for inst_name, inst_details in instances.items():
        if inst_details['module'] in count:
            count[inst_details['module']] += 1
        else:
            count[inst_details['module']] = 1
            
        if inst_details['module'] in module_data:
            sub_counts = count_instances(module_data, inst_details['module'])
            for sub_module, sub_count in sub_counts.items():
                if sub_module in count:
                    count[sub_module] += sub_count
                else:
                    count[sub_module] = sub_count
                    
    return count

# The main function for running the program.

if __name__ == "__main__":
    filename = sys.argv[1] # Assuming the filename is the first command-line argument.
    module_data = parse_verilog(filename)
    print("Modules found:", list(module_data.keys()))
    selected_module = input("Select a module: ")
    
    if selected_module not in module_data:
        print("Module not found!")
    else:
        counts = count_instances(module_data, selected_module)
        print(f"In the {selected_module} module:")
        for mod, cnt in counts.items():
            print(f"There are {cnt} instances of {mod}")

# The end of the program.