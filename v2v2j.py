import json
import os
import re
from tqdm import tqdm
import networkx as nx
import graphviz

# type1
def get_type1_data(file):
    """
    功能：提取文档中的 module 数据,并返回
    参数：
        file： type1 文档路径
    返回：
        modules：module列表
    """
    modules = []  
    with open(file) as f :
        line = f.readline()   
        m = ''
        sub = False  # 验证是否是新的module
        while line: 
            txt = line.strip()
            if txt.startswith('module'):
                sub = True
            if sub:
                m +=line
            if txt.startswith('endmodule'):
                sub = False
                modules.append(m)
                m = ''
            line = f.readline()
    return modules


def get_type1_json(modules):
    """
    功能：将moules数据转为json
    参数：
        modules： type1 中提取的module 列表
    返回：
        [verilog_library, 'verilog_library = ']: 
            verilog_library：为提取的json数据
            'verilog_library = ' 用于写入json文件开始内容
    """
    verilog_library = []
    key_lst = ['input', 'output', 'inout']         # 要提取的信息
    
    for m in modules:
        lst = [l.strip() for l in m.split('\n')]  # 拆分moule各行信息
        
        temp = {}                                 # 保存临时数据
        
        for tt in lst:
            if tt.startswith("module"):            # 验证module开始，提取 component_name
                temp["component_name"] = re.search('module (.+?)\(',tt).groups()[0]
                temp["lib_pins"] = []
            else:
                for key in key_lst:                # 循环提取 pins 数据，并写入temp
                    if tt.startswith(key):
                        t = re.search(key+"(.+?);", tt).groups()[0].strip().split(',')  # 提取数据
                        for p in t:
                            temp["lib_pins"].append(
                                {
                                   "pin_name": p.strip(),
                                   "pin_type": key
                                }
                            )
        
        verilog_library.append(temp)
    return [verilog_library, 'verilog_library = ']
# get_type1_json(get_type1_data("./1_Verilog_Library.v"))


# type2
def get_type2_data(file):
    """
    功能：提取文档nodes数据,并返回
    参数：
        file： type2 文档路径
    返回：
        nodes：node 列表
    """
    nodes = []  
    
    with open(file) as f :
        line = f.readline() 
        node =''
        module_start = True   # 验证node数据
        node_start = False
        while line: 
            txt = line.strip()
            if not (txt=='' or txt.startswith("//")):   # 排除空行和注释
                if module_start:
                    if txt.startswith("module"):        # 处理model
                        node += txt
                        txt = txt.replace(");",'')      # 防止匹配误伤，删除不需要的内容
                    elif "(" in txt:
                        nodes.append(node)
                        module_start = False
                        node_start = True
                        node=''
                    else:
                        node += txt
                if node_start:                         # 验证node开始，并将 moudle数据保存到nodes中
                    node += txt
                if txt == ');' or txt.endswith(');'):                        # 验证node 结束，并保存各node信息
                    nodes.append(node)
                    node = ''

            line = f.readline()
    return nodes
# get_type2_data("./data2/test6_1.v")
# get_type2_data("./data2/2_verilog_netlist.v"), 


# type 2
def get_type2_json(nodes, type1_data):
    """
    功能：将nodes数据转为json
    参数：
        nodes： type2 中提取的数据
        type1_data： type1_file 的json数据
    返回：
        [data[main], main + ' = ']：
        data[main]：main为当前 工程的名称，data[main] 为提取的json数据
         main + ' = '： 用于写入json文档 头部
    """
    # 转换 type1_data 格式 便于后续匹配数据
    dic_value = {}
    for i in range(len(type1_data)):
        dic_value[type1_data[i]['component_name']] = {}
        for p in type1_data[i]['lib_pins']:
            dic_value[type1_data[i]['component_name']][p['pin_name']] = p['pin_type']
    
    data = {}
    excep_list = []
    key_lst = ['input', 'output']             # 要提取的信息
    for node in nodes:
        if node.startswith('module '):        # 验证开始

            main = re.search('module (.+?)\(',node).groups()[0]  #提取 工程的名称
            #print(main) # adder
            data[main] = {"project_name": main}
            #data[main] = {} #**************************************
            lst = node.split(';')            # 拆分数据

            for key in key_lst:             # 遍历要提取的信息
                temp = []
                for tt in lst:               # 遍历工和信息
                    
                    if tt.startswith(key):   # 提取input 和 output 并写入数据
                        t = [k.strip() for k in re.search(key+"(.+)", tt).groups()[0].strip().split(',')]
                        temp +=t
                data[main][key] = temp
            data[main]["nodes_list"]=[]
        else:
            dic_node = {}                   #保存node 数据
            component_name, object_name = re.search("^(.+?) ([^\(]+)", node).groups()   # 提取  component_name, object_name
            dic_node['component_name'] = component_name
            dic_node["object_name"] = object_name
            
            dic_node['node_type'] = ''
            dic_node["pins"] = []
            pins = re.search("\(.+\)", node).group()[1:-1].split(',')   # 提取 pin 信息
            
            # Ckecking the cell is in Vlib.
            try:
                dic_value[component_name]

                i = 0                         # 计数
                for p in pins:               # 提取各pin的数据，并保存
                    try:
                        # print(p.split("(")[0].split(".")[1])
                        pin_type = dic_value[component_name][p.split("(")[0].split(".")[1]] # [' .a']-->[' ', 'a'] take 2nd
                        # pin_type = dic_value[component_name][p.split("(")[0][1:]]
                        # print(dic_value[component_name], p.split("(")[0][1:]) #************************
                    except Exception as e2:
                        print('\n Cant find this pin_names type: '+component_name+'.'+object_name+'.'+p.split("(")[0].split(".")[1]) # cant.. or_bi.n_07_.c
                        pin_type = ''
                        excep_list.append(e2)
                    dic_node["pins"].append({
                        "pin_name": p.split("(")[0].strip()[1:], 
                        "pin_value": p.split("(")[1].strip()[:-1], 
                        "pin_index": i, 
                        "pin_type": pin_type
                    })
                    i += 1

            except Exception as e1:
                print('\n Cant find this cell define in V_Lib: ', component_name)
                excep_list.append(e1)
            
            # 添加固定数据
            dic_node["pins"].append({"pin_name": "xin", "pin_value": "", "pin_index": i, "pin_type": "inout"})
            dic_node["pins"].append({"pin_name": "xout", "pin_value": "", "pin_index": i+1, "pin_type": "inout"})
            dic_node["pins"].append({"pin_name": "din", "pin_value": "", "pin_index": i+2, "pin_type": "inout"})
            dic_node["pins"].append({"pin_name": "dout", "pin_value": "", "pin_index": i+3, "pin_type": "inout"})
            
            dic_node["prev"] = []
            dic_node["next"] = []
            dic_node["level"] = ""
            dic_node["link_to_out"] = ""
            
            data[main]["nodes_list"].append(dic_node)

    return [data[main], main + ' = '], excep_list


# type3
def get_type3_data(file):
    """
    功能：提取文档中各 器件信息数据 ,并返回
    参数：
        file： type3 文档路径
    返回：
        data：器件信息数据
    """
    data = []  
    with open(file) as f :
        line = f.readline() 
        node = ''                      # 保存临时数据
        while line: 
            txt = line.strip()
            if txt.startswith("***"):  # 验证3行数据，满足条件则提取到data中保存
                t1 = f.readline()
                t2 = f.readline()
                
                if t1.strip().startswith(".subckt") and t2.strip().startswith("***"):
                    node = line + t1 + t2
                    data.append(node)
            else:
                node = ''
            line = f.readline() 
    return data


def get_type3_json(nodes):
    """
    功能：从 器件信息数据 nodes 数据提取信息并返回
    参数：
        nodes： type3 中提取的数据
    返回：
        [josim_library, "josim_library = "]：
            josim_library：为提取的json数据
            main + ' = '： 用于写入json文档 头部
    """
    josim_library = []
    for node in nodes:
        temp = {}
        temp["component_name"] =  node.split('\n')[1].split(' ')[1]   # 提取 component_name
        temp['lib_pins'] = []
        pins = re.split(r" +", node.split('\n')[2])[1:]               # 提取 PINS
        for pin in pins:                                              # 遍历各pin数据, 并保存
            temp['lib_pins'].append({
                "pin_name": pin, 
                "pin_type": ""
            })
        josim_library.append(temp)
    return [josim_library, "josim_library = "]


def export_json(json_data, save_name):
    """
    功能：将提取的信息写入文档
    参数：
        json_data： 从各文档中提取返回的的数据
        save_name： 保存的json文件名
    """
    with open(save_name,"w") as f:
        json.dump(json_data[0],f,ensure_ascii=False, indent=4)
    with open(save_name, "r+") as f:
        old = f.read()
        f.seek(0)
        f.write(json_data[1])
        f.write(old)

def get_files(dir_path):
    """
    功能：获取文件夹下的文件列表,并返回
    参数：
        dir_path： 文件路径
    """
    files = []
    for f in os.listdir(dir_path):
        files.append(os.path.join(dir_path, f))
    return files


# write_Vcontent
def write_Vcontent(project_I):
    output_Vcontent = ''

    # write module project_I(A, B, O, );
    output_Vcontent += 'module '+project_I["project_name"]+'(' # project_I["project_name"]
    for elem in project_I["input"]:
        output_Vcontent = output_Vcontent + elem + ', '
    for elem in project_I["output"]:
        output_Vcontent = output_Vcontent + elem + ', '
    output_Vcontent += ');\r\n'
    # ***************************************

    # write input output
    output_Vcontent += '\t'+'input '
    for elem in project_I["input"]:
        output_Vcontent += elem+', '
    output_Vcontent += ";\n"

    output_Vcontent += '\t'+'output '
    for elem in project_I["output"]:
        output_Vcontent += elem+', '
    output_Vcontent += ";\n"
    # ***************************************

    # write nodes
    for node in project_I["nodes_list"]:
        cell_txt = '\t'+node["component_name"]+' '+node["object_name"]+' ('
        for pin in node["pins"]:
            cell_txt += '.'+pin['pin_name']+'('+pin["pin_value"]+'), '
        cell_txt+=');  //level: '+str(node["level"])+'\n'
        output_Vcontent+=cell_txt
    # ***************************************
    output_Vcontent+='endmodule'
    print(output_Vcontent)
    
    return output_Vcontent

# add_GlobIO_as_R_and_add_V
def add_GlobIO_as_R_and_add_V(project_I):
    for GlobI in project_I['input']:
        # append V
        project_I['nodes_list'].append(
            {"component_name": "V_GlobIn",
            "object_name": "V_"+GlobI,
            "pins":[{"pin_name": "a", "pin_value": "0", "pin_type": "input", "pin_index": 0},
                    {"pin_name": "q", "pin_value": "R_"+GlobI+"_pre", "pin_type": "output", "pin_index": 1}],
            "level": -2,
            "prev": ["top"],
            "next": ["R_"+GlobI],
            "driver": ["V_"+GlobI]
            }
        )
        # append R
        project_I['nodes_list'].append(
            {"component_name": "R_GlobIn",
             "object_name": "R_"+GlobI,
             "pins": [{"pin_name": "a", "pin_value": "R_"+GlobI+"_pre", "pin_type": "input", "pin_index": 0},
                      {"pin_name": "q", "pin_value": GlobI, "pin_type": "output", "pin_index": 1}],
             "level": -1,
             "prev": ["V_"+GlobI],
             "next": []
            }
        )
    for GlobO in project_I['output']:
        project_I['nodes_list'].append(
            {"component_name": "GlobOut",
             "object_name": GlobO,
             "pins": [{"pin_name": "a", "pin_value": GlobO, "pin_type": "input", "pin_index": 0},
                      {"pin_name": "q", "pin_value": "tail", "pin_type": "output", "pin_index": 1}],
             "level": "",
             "prev": [],
             "next": ["tail"]
            }
        )

    return project_I

# add spliter
def add_spliter(project_I):
    Glob_spl_id = 0
    for i, node_i in enumerate(project_I["nodes_list"]):
        # spl2
        if len(node_i["next"]) == 2:
            this_nod_out = node_i["next"][0][3] # this_pin_out value
            sp_pin0 = "wr_spII_"+str(Glob_spl_id)+"_x" # pinout name
            sp_pin1 = "wr_spII_"+str(Glob_spl_id)+"_y" # pinout name
            sp_pin_lis = [sp_pin0, sp_pin1]
            project_I["nodes_list"].append(
                {"component_name": "spl2", "object_name": "spII_"+str(Glob_spl_id),
                "pins": [{"pin_name": "a", "pin_value": this_nod_out, "pin_type": "input", "pin_index": 0},
                        {"pin_name": "x", "pin_value": sp_pin0, "pin_type": "output", "pin_index": 1},
                        {"pin_name": "y", "pin_value": sp_pin1, "pin_type": "output", "pin_index": 2},
                        {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 3},
                        {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                        {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 5},
                        {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 6}],
                "level": "",
                "prev": [],
                "next": []
                })

            for ii, (next_nodenm, next_pin_id, next_pin_name, next_pin_value, this_pin_name,this_p_val) in enumerate(node_i["next"]):
                foundpins = list(filter(lambda node: node["object_name"] == next_nodenm, project_I["nodes_list"]))[0]["pins"]
                foundpin = list(filter(lambda pin: pin["pin_name"] == next_pin_name, foundpins))[0]
                # print(foundpin, "---------2")
                foundpin["pin_value"] = sp_pin_lis[ii]
            
            Glob_spl_id += 1
        
         # spl3
        if len(node_i["next"]) == 3:
            this_nod_out = node_i["next"][0][3] # this_pin_out value
            sp_pin0 = "wr_spII_"+str(Glob_spl_id)+"_x" # pinout name
            sp_pin1 = "wr_spII_"+str(Glob_spl_id)+"_y" # pinout name
            sp_pin2 = "wr_spII_"+str(Glob_spl_id)+"_z" # pinout name
            sp_pin_lis = [sp_pin0, sp_pin1, sp_pin2]
            project_I["nodes_list"].append(
                {"component_name": "spl3", "object_name": "spIII_"+str(Glob_spl_id),
                "pins": [{"pin_name": "a", "pin_value": this_nod_out, "pin_type": "input", "pin_index": 0},
                        {"pin_name": "x", "pin_value": sp_pin0, "pin_type": "output", "pin_index": 1},
                        {"pin_name": "y", "pin_value": sp_pin1, "pin_type": "output", "pin_index": 2},
                        {"pin_name": "z", "pin_value": sp_pin2, "pin_type": "output", "pin_index": 3},
                        {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                        {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 5},
                        {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 6},
                        {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 7}],
                "level": "",
                "prev": [],
                "next": []
                })

            for ii, (next_nodenm, next_pin_id, next_pin_name, next_pin_value, this_pin_name,this_p_val) in enumerate(node_i["next"]):
                foundpins = list(filter(lambda node: node["object_name"] == next_nodenm, project_I["nodes_list"]))[0]["pins"]
                foundpin = list(filter(lambda pin: pin["pin_name"] == next_pin_name, foundpins))[0]
                # print(foundpin, "---------3")
                foundpin["pin_value"] = sp_pin_lis[ii]
            
            Glob_spl_id += 1
        
        # spl4
        if len(node_i["next"]) == 4:
            this_nod_out = node_i["next"][0][3] # this_pin_out value
            sp_pin0 = "wr_spII_"+str(Glob_spl_id)+"_w" # pinout name
            sp_pin1 = "wr_spII_"+str(Glob_spl_id)+"_x" # pinout name
            sp_pin2 = "wr_spII_"+str(Glob_spl_id)+"_y" # pinout name
            sp_pin3 = "wr_spII_"+str(Glob_spl_id)+"_z" # pinout name
            sp_pin_lis = [sp_pin0, sp_pin1, sp_pin2, sp_pin3]
            project_I["nodes_list"].append(
                {"component_name": "spl4L", "object_name": "spIII_"+str(Glob_spl_id),
                "pins": [{"pin_name": "a", "pin_value": this_nod_out, "pin_type": "input", "pin_index": 0},
                        {"pin_name": "w", "pin_value": sp_pin0, "pin_type": "output", "pin_index": 1},
                        {"pin_name": "x", "pin_value": sp_pin1, "pin_type": "output", "pin_index": 2},
                        {"pin_name": "y", "pin_value": sp_pin2, "pin_type": "output", "pin_index": 3},
                        {"pin_name": "z", "pin_value": sp_pin3, "pin_type": "output", "pin_index": 4},
                        {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 5},
                        {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 6},
                        {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 7},
                        {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 8}],
                "level": "",
                "prev": [],
                "next": []
                })

            for ii, (next_nodenm, next_pin_id, next_pin_name, next_pin_value, this_pin_name,this_p_val) in enumerate(node_i["next"]):
                foundpins = list(filter(lambda node: node["object_name"] == next_nodenm, project_I["nodes_list"]))[0]["pins"]
                foundpin = list(filter(lambda pin: pin["pin_name"] == next_pin_name, foundpins))[0]
                # print(foundpin, "---------4")
                foundpin["pin_value"] = sp_pin_lis[ii]
            
            Glob_spl_id += 1

    return project_I


# make conections
def make_connections(project_I, log=False):
    for i, node_i in enumerate(project_I["nodes_list"]):
        node_i["next"] = []
        node_i["prev"] = []

    for i, node_i in enumerate(project_I["nodes_list"]):
        for k, node_k in enumerate(project_I["nodes_list"]):
            if (i==k):
                continue
            else:
                for ii, pin in enumerate(node_i["pins"]):                 # {"pin_name": a, "pin_value": "A", "pin_type": "input"}
                    if pin["pin_type"] == "output":
                        ii_pin_value = pin["pin_value"]
                        for kk, pinn in enumerate(node_k["pins"]):
                            if pinn["pin_type"] == "input":
                                kk_pin_value = pinn["pin_value"]

                                if ii_pin_value == kk_pin_value:
                                    node_i["next"].append((node_k["object_name"],pinn["pin_index"],pinn["pin_name"],pinn["pin_value"],pin["pin_name"],pin["pin_value"])) # 0:next_node, 1:next_nod_pin
                                    # next: next_name, next's idx, next's pin, next's pinvalue, this pin name, this pin value
                                    node_k["prev"].append((node_i["object_name"]))
                                    if (log == True):
                                        print("find "+node_i["object_name"]+" link to "+node_k["object_name"]+", with pinidx"+str(pinn["pin_index"]))
                                    if (node_k["component_name"] == "GlobOut"):
                                        node_i["link_to_out"] = 1
    return project_I


def get_level(project_I):
    PAIR = []
    for i, node_i in enumerate(project_I["nodes_list"]):
        for ii, (next_node_nm, next_pin_id, next_pin_name, next_pin_value, this_pin_name, this_p_val) in enumerate(node_i["next"]):
            pair = (node_i["object_name"], next_node_nm)
            PAIR.append(pair)
    # print(PAIR)
    G = nx.DiGraph()
    G.add_edges_from(PAIR)
    
    # give all path    
    for i, node_i in enumerate(project_I["nodes_list"]):
        if (node_i["object_name"].startswith("V_")==False) and (node_i["object_name"].startswith("R_")==False):
            dist_2_Rs = []
            for k, node_k in enumerate(project_I["nodes_list"]):
                if i==k:
                    continue
                else:
                    # search from R
                    if (node_k["object_name"].startswith("R_")):
                        source = node_k["object_name"]
                        target = node_i["object_name"]
                        for path in nx.all_simple_paths(G, source, target):
                            pp = []
                            for p in path:
                                pp.append(p)
                            dist_2_Rs.append(len(pp)-2) # from 0

            #print(node_i["object_name"],dist_2_Rs)
            if len(dist_2_Rs)>0:
                node_i["level"] = max(dist_2_Rs)
            else:
                print('Graph Error (path not walkable)')
                      
    return project_I

def pull_all_GlobOut_to_same_level(project_I, Four_=True):
    lis = []
    for i, node_i in enumerate(project_I["nodes_list"]):
        if node_i["object_name"] in project_I['output']:
            lis.append(node_i["level"])
    #print(lis)#[13,15,15,15]
    cell_lvs = max(lis)
    # check cell_lvs could %4 ==0
    if (cell_lvs%4 != 0):
        cell_lvs = ((cell_lvs//4)+1)*4
        if cell_lvs%4 != 0:
            print("Err, level%4")

    if Four_==True:
        for i, node_i in enumerate(project_I["nodes_list"]):
            if node_i["object_name"] in project_I['output']:
                node_i["level"] = cell_lvs # all to 15
        return project_I
    else:
        for i, node_i in enumerate(project_I["nodes_list"]):
            if node_i["object_name"] in project_I['output']:
                node_i["level"] = max(lis) # all to 15
        return project_I

def print_level(project_I):
    for i, node_i in enumerate(project_I["nodes_list"]):
        print(node_i["object_name"]+", lv: "+str(node_i["level"]))


'''
if gap == 1: add 1 bfr, 
bfr's in_value = this.node.pinout_val; 
bfr's out_value = "w_bfr_"+bfrid
filiter next node, repalce it's pinname -> "w_bfr_"+bfrid
'''
def add_buffer(project_I):
    Glob_bfr_id = 0
    for i, node_i in enumerate(project_I["nodes_list"]):
        for ii, (next_nodenm, next_pin_id, next_pin_name, next_pin_value, this_pin_name, this_pin_val) in enumerate(node_i["next"]):
            foundnode = list(filter(lambda node: node["object_name"] == next_nodenm, project_I["nodes_list"]))[0]
            if (foundnode["level"] - node_i["level"]) == 1:
                continue
                # print("no need to insert bfr")
            elif (foundnode["level"] - node_i["level"]) == 2:
                print("insert "+str(1)+" bfr between "+node_i["object_name"]+" "+foundnode["object_name"])
                gap = 1 # only add 1 bfr
                project_I["nodes_list"].append(
                {"component_name": "bfr", "object_name": "bfr_"+str(Glob_bfr_id),
                "pins": [{"pin_name": "a", "pin_value": this_pin_val, "pin_type": "input", "pin_index": 0},
                        {"pin_name": "q", "pin_value": "w_bfr_"+str(Glob_bfr_id), "pin_type": "output", "pin_index": 1},
                        {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 2},
                        {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 3},
                        {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                        {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 5}],
                "level": "",
                "prev": [],
                "next": []
                })
                foundpin = list(filter(lambda pin: pin["pin_name"] == next_pin_name, foundnode["pins"]))[0]
                foundpin["pin_value"] = "w_bfr_"+str(Glob_bfr_id)
                Glob_bfr_id += 1
            
            elif (foundnode["level"] - node_i["level"]) > 2:
                gap = foundnode["level"] - node_i["level"] - 1
                print("insert "+str(gap)+" bfr between "+node_i["object_name"]+" "+foundnode["object_name"])
                for time in range(1,gap+1): #gap=6, 1,2,3,4,5,6
                    if time == 1:
                        project_I["nodes_list"].append( # in, 22
                        {"component_name": "bfr", "object_name": "bfr_"+str(Glob_bfr_id),
                        "pins": [{"pin_name": "a", "pin_value": this_pin_val, "pin_type": "input", "pin_index": 0},
                                {"pin_name": "q", "pin_value": "w_bfr_"+str(Glob_bfr_id), "pin_type": "output", "pin_index": 1},
                                {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 2},
                                {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 3},
                                {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                                {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 5}],
                        "level": "",
                        "prev": [],
                        "next": []
                        })
                        Glob_bfr_id += 1 #23
                    elif (time>1) and (time<gap):
                        project_I["nodes_list"].append( # 22,23; 23,24; 24,25
                        {"component_name": "bfr", "object_name": "bfr_"+str(Glob_bfr_id),
                        "pins": [{"pin_name": "a", "pin_value": "w_bfr_"+str(Glob_bfr_id-1), "pin_type": "input", "pin_index": 0},
                                {"pin_name": "q", "pin_value": "w_bfr_"+str(Glob_bfr_id), "pin_type": "output", "pin_index": 1},
                                {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 2},
                                {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 3},
                                {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                                {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 5}],
                        "level": "",
                        "prev": [],
                        "next": []
                        })
                        Glob_bfr_id += 1 #24; 25, 26...
                    elif (time == gap):
                        project_I["nodes_list"].append( # 25, 26
                        {"component_name": "bfr", "object_name": "bfr_"+str(Glob_bfr_id),
                        "pins": [{"pin_name": "a", "pin_value": "w_bfr_"+str(Glob_bfr_id-1), "pin_type": "input", "pin_index": 0},
                                {"pin_name": "q", "pin_value": "w_bfr_"+str(Glob_bfr_id), "pin_type": "output", "pin_index": 1},
                                {"pin_name": "xin", "pin_value": "", "pin_type": "inout", "pin_index": 2},
                                {"pin_name": "xout", "pin_value": "", "pin_type": "inout", "pin_index": 3},
                                {"pin_name": "din", "pin_value": "", "pin_type": "inout", "pin_index": 4},
                                {"pin_name": "dout", "pin_value": "", "pin_type": "inout", "pin_index": 5}],
                        "level": "",
                        "prev": [],
                        "next": []
                        })
                        foundpin = list(filter(lambda pin: pin["pin_name"] == next_pin_name, foundnode["pins"]))[0]
                        foundpin["pin_value"] = "w_bfr_"+str(Glob_bfr_id)
                        Glob_bfr_id += 1
    
    return project_I


def add_AC1_to_proj(project_I): # 0 2 4 6 8
    AC1_list = []
    for i in range(0,1000):
        AC1_list.append(2*i)
    ac1_id = 0
    # add V and R node for AC1
    project_I['nodes_list'].append(
        {"component_name": "V_xinI",
        "object_name": "V_xinI",
        "pins":[{"pin_name": "a", "pin_value": "0",         "pin_type":     "input", "pin_index": 0},
                {"pin_name": "q", "pin_value": "V_xinI_post", "pin_type":   "output", "pin_index": 1}],
        "level": -2,
        "prev": ["top"],
        "next": ["R_xinI"]
        }
    )
    # append R
    project_I['nodes_list'].append(
        {"component_name": "R_xinI",
            "object_name": "R_xinI",
            "pins": [{"pin_name": "a", "pin_value": "V_xinI_post", "pin_type": "input", "pin_index": 0},
                    {"pin_name": "q", "pin_value": "wr_acI_0", "pin_type": "output", "pin_index": 1}],
            "level": -1,
            "prev": ["V_xinI"],
            "next": []
        }
    )

    for node in project_I["nodes_list"]:
        for lev in AC1_list:
            if (node["level"] == lev) and (node["component_name"]!="GlobOut"):
                # generate AC conn
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "xin", node['pins']))
                #print(pin_val) # [{'pin_name': 'xin', 'pin_value': 'ukn', 'pin_index': 3, 'pin_type': 'inout'}]
                pin_val[0]["pin_value"] = "wr_acI_"+str(ac1_id) # modify value in project_I["nodes_list"]
                ac1_id+=1
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "xout", node['pins']))
                pin_val[0]["pin_value"] = "wr_acI_"+str(ac1_id)
    return project_I


def add_AC2_to_proj(project_I):
    AC2_list = []
    for i in range(0,1000):
        AC2_list.append(2*i+1)
    ac2_id = 0
    # add V and R node for AC1
    project_I['nodes_list'].append(
        {"component_name": "V_xinII",
        "object_name": "V_xinII",
        "pins":[{"pin_name": "a", "pin_value": "0",         "pin_type":     "input", "pin_index": 0},
                {"pin_name": "q", "pin_value": "V_xinII_post", "pin_type":   "output", "pin_index": 1}],
        "level": -2,
        "prev": ["top"],
        "next": ["R_xinII"]
        }
    )
    # append R
    project_I['nodes_list'].append(
        {"component_name": "R_xinII",
            "object_name": "R_xinII",
            "pins": [{"pin_name": "a", "pin_value": "V_xinII_post", "pin_type": "input", "pin_index": 0},
                    {"pin_name": "q", "pin_value": "wr_acII_0", "pin_type": "output", "pin_index": 1}],
            "level": -1,
            "prev": ["V_xinII"],
            "next": []
        }
    )
    for node in project_I["nodes_list"]:
        for lev in AC2_list:
            if (node["level"] == lev) and (node["component_name"]!="GlobOut"):
                # generate AC conn
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "xin", node['pins']))
                # print(lev, node["object_name"], pin_val)
                pin_val[0]["pin_value"] = "wr_acII_"+str(ac2_id) # modify value in project_I
                ac2_id+=1
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "xout", node['pins']))
                pin_val[0]["pin_value"] = "wr_acII_"+str(ac2_id)
    return project_I


def add_DC_to_proj(project_I):
    DC_list = []
    for i in range(0,1000):
        DC_list.append(i)
    dc_id = 0
    # add V and R node for AC1
    project_I['nodes_list'].append(
        {"component_name": "V_din",
        "object_name": "V_din",
        "pins":[{"pin_name": "a", "pin_value": "0",         "pin_type":     "input", "pin_index": 0},
                {"pin_name": "q", "pin_value": "V_din_post", "pin_type":   "output", "pin_index": 1}],
        "level": -2,
        "prev": ["top"],
        "next": ["R_din"]
        }
    )
    # append R
    project_I['nodes_list'].append(
        {"component_name": "R_din",
            "object_name": "R_din",
            "pins": [{"pin_name": "a", "pin_value": "V_din_post", "pin_type": "input", "pin_index": 0},
                    {"pin_name": "q", "pin_value": "wr_dc_0", "pin_type": "output", "pin_index": 1}],
            "level": -1,
            "prev": ["V_din"],
            "next": []
        }
    )
    for node in project_I["nodes_list"]:
        for lev in DC_list:
            if (node["level"] == lev) and (node["component_name"]!="GlobOut"):
                # generate AC conn
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "din", node['pins']))
                pin_val[0]["pin_value"] = "wr_dc_"+str(dc_id) # modify value in project_I
                dc_id+=1
                pin_val = list(filter(lambda sublis: sublis['pin_name'] == "dout", node['pins']))
                pin_val[0]["pin_value"] = "wr_dc_"+str(dc_id)
    return project_I


def reverse_AC_DC(jsjs):
    # reverse AC1
    rev_AC1 = []
    for i in range(500):
        rev_AC1.append(2+4*i) # 2,6,10,14,...
    for i, node_i in enumerate(jsjs["nodes_list"]): # AC1: 
        if node_i['level'] in rev_AC1:
            x_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xout')]
            x_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xin')]
            for pin in node_i['pins']:
                if pin['pin_name'] == 'xout':
                    pin['pin_value'] = x_in[0]
                if pin['pin_name'] == 'xin':
                    pin['pin_value'] = x_out[0]
    
    rev_AC2 = []
    for i in range(500):
        rev_AC2.append(3+4*i) # 3,7,11,15,...
    for i, node_i in enumerate(jsjs["nodes_list"]): # AC1: 
        if node_i['level'] in rev_AC2:
            x_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xout')]
            x_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xin')]
            for pin in node_i['pins']:
                if pin['pin_name'] == 'xout':
                    pin['pin_value'] = x_in[0]
                if pin['pin_name'] == 'xin':
                    pin['pin_value'] = x_out[0]
    
    rev_DC = []
    for i in range(500):
        rev_DC.append(1+2*i) # 1,3,5,7,9,...
    for i, node_i in enumerate(jsjs["nodes_list"]): # AC1: 
        if node_i['level'] in rev_DC:
            d_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='dout')]
            d_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='din')]
            for pin in node_i['pins']:
                if pin['pin_name'] == 'dout':
                    pin['pin_value'] = d_in[0]
                if pin['pin_name'] == 'din':
                    pin['pin_value'] = d_out[0]
    
    return jsjs


def resort_node_by_level(project_I):
    contain = {}
    contain["project_name"] = project_I["project_name"]
    contain["input"] = project_I["input"] # input
    contain["output"] = project_I["output"] # input
    contain["nodes_list"] = []

    for i in range(-2,1000):
        for node in project_I["nodes_list"]:
            if node["level"] == i:
                contain["nodes_list"].append(node)
    return  contain


# draw nodes

def draw_nodes(jsjs, AC1_visb, AC2_visb, DC_visb, reverse=True): # AC1_visb, AC2_visb, DC_visb,
    if reverse == True:
        # change the order of AC1, AC2, and DC ----------------------------
        for i, node_i in enumerate(jsjs["nodes_list"]): # AC1: 
            if node_i['level'] in [2,6,10,14,18,22,26,30]:
                x_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xout')]
                x_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xin')]
                for pin in node_i['pins']:
                    if pin['pin_name'] == 'xout':
                        pin['pin_value'] = x_in[0]
                    if pin['pin_name'] == 'xin':
                        pin['pin_value'] = x_out[0]

            if node_i['level'] in [3,7,11,15,19,23,27,31]:
                x_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xout')]
                x_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='xin')]
                for pin in node_i['pins']:
                    if pin['pin_name'] == 'xout':
                        pin['pin_value'] = x_in[0]
                    if pin['pin_name'] == 'xin':
                        pin['pin_value'] = x_out[0]

            if node_i['level'] in [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                d_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='dout')]
                d_in =  [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_name']=='din')]
                for pin in node_i['pins']:
                    if pin['pin_name'] == 'dout':
                        pin['pin_value'] = d_in[0]
                    if pin['pin_name'] == 'din':
                        pin['pin_value'] = d_out[0]
    
    # add may level ----------------------------
    may_level = []
    for i in range(500):
        may_level.append(i-1)

    # create global graph ----------------------------
    GlobG = graphviz.Digraph(filename='globg.gv')

    
    # create subgraph by levels
    max_lv = -100
    for i, node_i in enumerate(jsjs["nodes_list"]): # AC1:
        if node_i["level"] > max_lv:
            max_lv = node_i["level"]

    subGs = {}
    for i in range(-1, max_lv+1):
        subGs['subG_'+ str(i)] = graphviz.Digraph()
        subGs['subG_'+ str(i)].attr(rank='same') # set same level mode have same rank
    # create same level's nodes in subgraph ----------------------------
    for i, node_i in enumerate(jsjs["nodes_list"]):
        if node_i['level'] in may_level:
            if (node_i['component_name'] == 'bfr'):
                lev = node_i['level']
                subGs['subG_'+str(lev)].node(node_i['object_name'],style = "filled",color = 'lightgreen')
            elif ((node_i['component_name'] == 'spl2') or (node_i['component_name'] == 'spl3') or (node_i['component_name'] == 'spl4L') or (node_i['component_name'] == 'spl3L')):
                lev = node_i['level']
                subGs['subG_'+str(lev)].node(node_i['object_name'],style="filled",color='lightblue')
            else:
                lev = node_i['level']
                subGs['subG_'+str(lev)].node(node_i['object_name'])
                

    # combine subgraphs to global graph ----------------------------
    for subG in subGs.keys():
        GlobG.subgraph(subGs[subG])

    # make connections ----------------------------
    # normal conc (black) ----------------------------
    for i, node_i in enumerate(jsjs["nodes_list"]):
        for k, node_k in enumerate(jsjs["nodes_list"]):
            if i == k:
                continue
            else:
                if (node_i['level'] in may_level) and (node_k['level'] in may_level):
                    # find all inputs, outputs
                    wir_out = [pin['pin_value'] for pin in node_i['pins'] if (pin['pin_type']=='output')]
                    wir_in =  [pin['pin_value'] for pin in node_k['pins'] if (pin['pin_type']=='input')]

                    for x in wir_out:
                        if x in wir_in:
                            GlobG.edge(node_i['object_name'], node_k['object_name'], label=x,fontsize="8")
                            #print(i,k,'   ',wir_out, '   ', wir_in)
                            #print('find', node_i['object_name'],' next is ', node_k['object_name'])
                            

    if (AC1_visb == '1'):
        # conn AC1 (red) ----------------------------
        may_AC1 = []
        for i in range(500):
            may_AC1.append(2*i)
        for i, node_i in enumerate(jsjs["nodes_list"]):
            for k, node_k in enumerate(jsjs["nodes_list"]):
                if i == k:
                    continue
                else:
                    if (node_i['level'] in may_AC1) and (node_k['level'] in may_AC1) and (node_i['component_name']!="GlobOut") and (node_k['component_name']!="GlobOut"):
                        # find all inputs, outputs
                        wir_out = list(filter(lambda pin: pin['pin_name'] == "xout", node_i['pins']))[0]['pin_value']
                        wir_in  = list(filter(lambda pin: pin['pin_name'] == "xin", node_k['pins']))[0]['pin_value']

                        if wir_in == wir_out:
                            #print(wir_out)
                            GlobG.edge(node_i['object_name'], node_k['object_name'], color='red')
    
    if (AC2_visb == '1'):
        # conn AC2 (blue) ----------------------------
        may_AC2 = []
        for i in range(500):
            may_AC2.append(2*i+1)
        for i, node_i in enumerate(jsjs["nodes_list"]):
            for k, node_k in enumerate(jsjs["nodes_list"]):
                if i == k:
                    continue
                else:
                    if (node_i['level'] in may_AC2) and (node_k['level'] in may_AC2) and (node_i['component_name']!="GlobOut") and (node_k['component_name']!="GlobOut"):
                        # find all inputs, outputs
                        wir_out = list(filter(lambda pin: pin['pin_name'] == "xout", node_i['pins']))[0]['pin_value']
                        wir_in  = list(filter(lambda pin: pin['pin_name'] == "xin", node_k['pins']))[0]['pin_value']

                        if wir_in == wir_out:
                            #print(wir_out)
                            GlobG.edge(node_i['object_name'], node_k['object_name'], color='blue')

                        
    if (DC_visb == '1'):
        # conn DC (green) ----------------------------
        may_DC = []
        for i in range(500):
            may_DC.append(i)
        for i, node_i in enumerate(jsjs["nodes_list"]):
            for k, node_k in enumerate(jsjs["nodes_list"]):
                if i == k:
                    continue
                else:
                    if (node_i['level'] in may_DC) and (node_k['level'] in may_DC) and (node_i['component_name']!="GlobOut") and (node_k['component_name']!="GlobOut"):
                        # find all inputs, outputs
                        wir_out = list(filter(lambda pin: pin['pin_name'] == "dout", node_i['pins']))[0]['pin_value']
                        wir_in  = list(filter(lambda pin: pin['pin_name'] == "din", node_k['pins']))[0]['pin_value']

                        if wir_in == wir_out:
                            #print(wir_out)
                            GlobG.edge(node_i['object_name'], node_k['object_name'], color='green')

                
    GlobG.view()

def new_josim_leb(josim_json):
    new_jsm_lib = []
    for compnt in josim_json[0]:
        pin_lis = []
        for pin in compnt['lib_pins']:
            pin_lis.append(pin['pin_name'])
        new_jsm_lib.append({"component_name": compnt['component_name'], "lib_pins": pin_lis})
    #print(new_jsm_lib[0])
    return new_jsm_lib

def write_Josimcontent(project_I, new_jsm_lib):
    output_Josimcontent = ""
    output_Josimcontent += ".MODEL JJMOD JJ(RTYPE=1, VG=2.8MV, CAP=0.064PF, R0=100OHM, RN=17OHM, ICRIT=0.1MA)\n\n"
    
    for josim in new_jsm_lib:
        group_info = '\n'
        group_info += "*** "+josim["component_name"]+" \t"+str(josim["lib_pins"])+'\n'
        for node in project_I["nodes_list"]:
            if (node['component_name'] == josim["component_name"]):
                cell_txt = "X"+node["object_name"]+"\t"+node["component_name"]+' \t'
                for pin in josim["lib_pins"]:
                    pin_val = list(filter(lambda sublis: sublis['pin_name'] == pin, node['pins']))
                    cell_txt += pin_val[0]["pin_name"]+": "+pin_val[0]["pin_value"]+" "+' \t'
                cell_txt += "*** lv: "+str(node["level"])
                cell_txt += '\n'
                group_info += cell_txt
        if (group_info.endswith(']\n')==False):
            output_Josimcontent += group_info
    
    output_Josimcontent += '\n\n'
    
    return output_Josimcontent



def write_Josimcontent_number(project_I, new_jsm_lib):
    # make dict for all pin_value: record the biggest xout and dout
    may_AC1 = []
    may_AC2 = []
    may_DC = []
    for i in range(500):
        may_AC1.append(2*i)
        may_AC2.append(2*i+1)
        may_DC.append(i)

    max_ac1_out = -100
    max_ac2_out = -100
    max_dc_out = -100
    for i, node_i in enumerate(jsjs["nodes_list"]):
        if node_i["level"] in may_AC1 and node_i["component_name"].startswith("Glob")==False:
            # x1_out = list(filter(lambda pin: pin['pin_name'] == "xout", node_i['pins']))[0]['pin_value']
            x1_out = list(filter(lambda pin: pin['pin_value'].startswith("wr_acI"), node_i['pins']))
            for aa in x1_out:
                x1_out_id = int(aa["pin_value"].split("_")[2])
                if x1_out_id > max_ac1_out:
                    max_ac1_out = x1_out_id
    for i, node_i in enumerate(jsjs["nodes_list"]):
        if node_i["level"] in may_AC2 and node_i["component_name"].startswith("Glob")==False:
            # x2_out = list(filter(lambda pin: pin['pin_name'] == "xout", node_i['pins']))[0]['pin_value']
            x2_out = list(filter(lambda pin: pin['pin_value'].startswith("wr_acII"), node_i['pins']))
            for aa in x2_out:
                x2_out_id = int(aa["pin_value"].split("_")[2])
                if x2_out_id > max_ac2_out:
                    max_ac2_out = x2_out_id
    for i, node_i in enumerate(jsjs["nodes_list"]):
        if node_i["level"] in may_DC and node_i["component_name"].startswith("Glob")==False:
            #d_out = list(filter(lambda pin: pin['pin_name'] == "dout", node_i['pins']))[0]['pin_value']
            d_out = list(filter(lambda pin: pin['pin_value'].startswith("wr_dc"), node_i['pins']))
            for aa in d_out:
                d_out_id = int(aa["pin_value"].split("_")[2])
                #print(d_out_id)
                if d_out_id > max_dc_out:
                    max_dc_out = d_out_id
    #print(max_ac1_out, max_ac2_out, max_dc_out)
    # *********************************************    
    
    pin_val_dict = {}
    pin_id = 10
    for node in project_I["nodes_list"]:
        for pin in node["pins"]:
            
            pin_val_dict[pin["pin_value"]] = pin_id
            pin_id += 1

    output_Josimcontent = ""
    output_Josimcontent += ".MODEL JJMOD JJ(RTYPE=1, VG=2.8MV, CAP=0.064PF, R0=100OHM, RN=17OHM, ICRIT=0.1MA)\n\n"
    
    for josim in new_jsm_lib:
        group_info = '\n'
        group_info += "*** "+josim["component_name"]+" \t"+str(josim["lib_pins"])+'\n'
        for node in project_I["nodes_list"]:
            if (node['component_name'] == josim["component_name"]):
                cell_txt = "X"+node["object_name"]+"\t"+node["component_name"]+' \t'
                for pin in josim["lib_pins"]:
                    pin_val = list(filter(lambda sublis: sublis['pin_name'] == pin, node['pins']))
                    # change to 0: last q, last xout1, xout2, dout.
                    if pin_val[0]["pin_value"] == "wr_acI_"+str(max_ac1_out): # pin=="xout" and 
                        cell_txt += "0"+ " "+' \t'
                    elif pin_val[0]["pin_value"] == "wr_acII_"+str(max_ac2_out):
                        cell_txt += "0"+ " "+' \t'
                    elif pin_val[0]["pin_value"] == "wr_dc_"+str(max_dc_out):
                        cell_txt += "0"+ " "+' \t'
                    elif "link_to_out" in node.keys() and node["link_to_out"] == 1:
                        # if type not output:
                        if pin_val[0]["pin_type"] == "output":
                            cell_txt += "0"+ " "+' \t'
                        else: cell_txt += str(pin_val_dict[pin_val[0]["pin_value"]])+" "+' \t'
                    else:
                        cell_txt += str(pin_val_dict[pin_val[0]["pin_value"]])+" "+' \t'
                # cell_txt += "*** lv: "+str(node["level"])
                cell_txt += '\n'
                group_info += cell_txt
        if (group_info.endswith(']\n')==False):
            output_Josimcontent += group_info
    
    output_Josimcontent += '\n\n'
    
    return output_Josimcontent, pin_val_dict



def write_driver(inp, jsjs, pin_val_dict, config): # config
    # write 1000.0ohm before R
    for node in jsjs["nodes_list"]:
        if (node["component_name"] == "R_GlobIn") or (node["component_name"] == "R_xinI") or (node["component_name"] == "R_xinII") or (node["component_name"] == "R_din"): # V_GlobIn
            cell_txt = node["object_name"]+" \t\t\t"
            pin_a = list(filter(lambda sublis: sublis['pin_name'] == "a", node['pins']))
            pin_q = list(filter(lambda sublis: sublis['pin_name'] == "q", node['pins']))
            cell_txt += str(pin_val_dict[pin_a[0]["pin_value"]])+" "+' \t'
            cell_txt += str(pin_val_dict[pin_q[0]["pin_value"]])+" "+' \t'+'1000.0ohm'+'\n'
            inp += cell_txt
        
        if (node["component_name"] == "V_xinI"):
            cell_txt = node["object_name"]+" \t\t\t"
            pin_a = list(filter(lambda sublis: sublis['pin_name'] == "a", node['pins'])) # "0"
            pin_q = list(filter(lambda sublis: sublis['pin_name'] == "q", node['pins']))
            cell_txt += str(pin_val_dict[pin_q[0]["pin_value"]])+" "+' \t'
            cell_txt += "0"+" "+' \t'+ config['xin1']+'\n'
            inp += cell_txt
        if (node["component_name"] == "V_xinII"):
            cell_txt = node["object_name"]+" \t\t\t"
            pin_a = list(filter(lambda sublis: sublis['pin_name'] == "a", node['pins'])) # "0"
            pin_q = list(filter(lambda sublis: sublis['pin_name'] == "q", node['pins']))
            cell_txt += "0"+" "+' \t'
            cell_txt += str(pin_val_dict[pin_q[0]["pin_value"]])+" "+' \t'+ config['xin2']+'\n'
            inp += cell_txt
        if (node["component_name"] == "V_din"):
            cell_txt = node["object_name"]+" \t\t\t"
            pin_a = list(filter(lambda sublis: sublis['pin_name'] == "a", node['pins'])) # "0"
            pin_q = list(filter(lambda sublis: sublis['pin_name'] == "q", node['pins']))
            cell_txt += str(pin_val_dict[pin_q[0]["pin_value"]])+" "+' \t'
            cell_txt += "0"+" "+' \t'+config['din']+'\n'
            inp += cell_txt
        
        if (node["component_name"] == "V_GlobIn"):
            for key in list(config.keys()):
                if node["object_name"] == key:
                    cell_txt = node["object_name"]+" \t\t\t"
                    pin_a = list(filter(lambda sublis: sublis['pin_name'] == "a", node['pins'])) # "0"
                    pin_q = list(filter(lambda sublis: sublis['pin_name'] == "q", node['pins']))
                    cell_txt += str(pin_val_dict[pin_q[0]["pin_value"]])+" "+' \t'
                    cell_txt += "0"+" "+' \t' + config[node["object_name"]] + '\n'

            inp += cell_txt
     
    inp += '\n\n'
    return inp

def copy_josim_lib(inp):
    dir_path = './3_Jlib/'
    with open(dir_path+'josim_lib.inp','r') as firstfile:
        for line in firstfile:
            inp += line
    return inp

def generate_10010(value, offset, freq, zhenfu):# 10-->100ps
    txt = "0ps 0mV "
    time = int(1000/freq)
    txt += "1ps "+str(-zhenfu)+"mV"+" "+str(offset)+"ps"+" "+str(-zhenfu)+"mV "+" \t"
    for i, v in enumerate(value):
        if v==0:
            txt += str(offset+1+i*time)+"ps "+str(-zhenfu)+"mV"+" "+str(offset+(i+1)*time)+"ps "+str(-zhenfu)+"mV "+"\t"
        if v==1:
            txt += str(offset+1+i*time)+"ps "+str(zhenfu)+"mV"+" "+str(offset+(i+1)*time)+"ps "+str(zhenfu)+"mV "+"\t"
    out = "PWL("+txt+")"
    return out

# tttt = generate_10010([1,0,0,1], 20, 5, 5)
# print(tttt)


# ****** main *******************************
if __name__ == "__main__":

    save_path = './json'  # json保存路径
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 处理 type1
    dir_path = './1_Vlib'
    type1_file = "./1_Vlib/verilog_lib.v"
    t1_data = get_type1_data(type1_file)
    V_lib_json = get_type1_json(t1_data)

    # 保存的josn文档和原文件同名
    # save_name = os.path.join(save_path, os.path.splitext(os.path.split(f)[1])[0] + ".json")
    # export_json(t1_json, save_name)

    # 批量处理 type2
    dir_path = './2_Vnetlist'
    files = get_files(dir_path)
    for f in tqdm(files):
        t2_data = get_type2_data(f)
        netlist_json, exp_list = get_type2_json(t2_data, V_lib_json[0])
        
        # save_name = os.path.join(save_path, os.path.splitext(os.path.split(f)[1])[0] + ".json")
        # export_json(js, save_name)
    
    if len(exp_list) == 0:
        # 批量处理 type3
        dir_path = './3_Jlib'
        files = get_files(dir_path)
        for f in tqdm(files):
            data = get_type3_data(f)
            josim_json = get_type3_json(data)
            
            # save_name = os.path.join(save_path, os.path.splitext(os.path.split(f)[1])[0] + ".json")
            # export_json(js, save_name)
            
        jsjs = add_GlobIO_as_R_and_add_V(netlist_json[0])

        jsjs = make_connections(jsjs)

        # ****** from here *****************************
        # jsjs = add_spliter(jsjs)

        # jsjs = make_connections(jsjs)

        jsjs = get_level(jsjs)
        jsjs = pull_all_GlobOut_to_same_level(jsjs, Four_=True)

        jsjs = add_buffer(jsjs)

        jsjs = make_connections(jsjs)
        # ****** end here *****************************

        jsjs = get_level(jsjs)
        jsjs = pull_all_GlobOut_to_same_level(jsjs, Four_=True)

        jsjs = resort_node_by_level(jsjs)
        print_level(jsjs)

        jsjs = add_AC1_to_proj(jsjs)
        jsjs = add_AC2_to_proj(jsjs)
        jsjs = add_DC_to_proj(jsjs)

        jsjs = reverse_AC_DC(jsjs)

        jsjs = resort_node_by_level(jsjs)

        print('***********************')
        #print(jsjs)
        Vcontent = write_Vcontent(jsjs)
        with open("Vcontent.v", "w") as text_file:
            text_file.write(Vcontent)

        with open("json/all_nodes.json", "w") as outfile:
            json.dump(jsjs, outfile)


        new_jsm_lib = new_josim_leb(josim_json)

        inp_word = write_Josimcontent(jsjs, new_jsm_lib)
        with open("debug_"+jsjs["project_name"]+".inp", "w") as text_file:
            text_file.write(inp_word)

        inp, pin_val_dict = write_Josimcontent_number(jsjs, new_jsm_lib)
        

        # read config.txt from same dir and make a dict.
        config = {"xin1": "SIN (0 800mV 5GHz 100ps 0 )",
                "xin2": "SIN (0 800mV 5GHz 150ps 0 )",
                "din": "PWL ( 0ps 0mv 20ps 1200mV )"}

        with open('config.txt') as f:
            l_strip = [s.strip() for s in f.readlines()]
            for cfg in l_strip[1:]:
                cfg_lis = cfg.split(',')
                
                name = "V_"+cfg_lis[0]
                freq = int(cfg_lis[1])
                offset = int(cfg_lis[2])
                zhenfu =  int(cfg_lis[3])
                value = str(cfg_lis[4])
                value_ = []
                for i in range(len(value)):
                    value_.append(int(value[i]))
                out_txt = generate_10010(value_, offset, freq, zhenfu)

                config[name] = out_txt
        #print(config)
        '''
        {
            'xin1': 'SIN (0 800mV 5GHz 100ps 0 )', 'xin2': 'SIN (0 800mV 5GHz 150ps 0 )', 'din': 'PWL ( 0ps 0mv 20ps 1200mV )', 
            'V_a': 'PWL(0ps 0mV 1ps -5mV 20ps -5mV  \t21ps 5mV 220ps 5mV \t221ps 5mV 420ps 5mV \t421ps -5mV 620ps -5mV \t621ps -5mV 820ps -5mV \t)', 
            'V_b': 'PWL(0ps 0mV 1ps -5mV 20ps -5mV  \t21ps -5mV 220ps -5mV \t221ps -5mV 420ps -5mV \t421ps 5mV 620ps 5mV \t621ps 5mV 820ps 5mV \t)',
            'V_c': 'PWL(0ps 0mV 1ps -5mV 20ps -5mV  \t21ps -5mV 220ps -5mV \t221ps -5mV 420ps -5mV \t421ps 5mV 620ps 5mV \t621ps 5mV 820ps 5mV \t)'
        }
        '''

        inp = write_driver(inp, jsjs, pin_val_dict, config)
        inp = copy_josim_lib(inp)
        with open("josim_"+jsjs["project_name"]+".inp", "w") as text_file:
            text_file.write(inp)

        jsjs_draw = jsjs.copy()
        draw_nodes(jsjs_draw, "1", "1", "1")

