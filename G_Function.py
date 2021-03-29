 #-*-coding:utf-8-*-
import threading
import time
import os
import sys
import json
from datetime import datetime
import re
import shutil
import uuid
import platform
from psutil import net_if_addrs

VARIABLE={}
RM_VARIABLE={}
Config={}
Car_Config={}
R = threading.Lock()
mid_message_list=[]
secreen_log_message=[]
table_value_list=[]
flask_table_dic={}

def get_base_dir():

    ret = os.path.dirname(os.path.realpath(sys.argv[0]))
    SV('base_dir',ret)
    return ret

def PML(pml_str):
    pml=GV("BROADCAST.PML")
    if pml.find(pml_str)<0: 
        return False
    else:
        return True
###not test
def PML_Fun(pml_fun):
    c4 = re.compile(r'(/[&\|\\\*^%$#@\-()!]/g')    
    pml_ = pml_fun.sub('_', c4)
    pml_list=pml_.split("_")
    for pml_str in pml_list:
        if pml_str !=None and pml_str !="":
           pml_fun=pml_fun.replace(pml_str, PML(pml_str))
    return  eval(pml_fun)            

def SV(key,value):
    global VARIABLE
    R.acquire() 
    VARIABLE[key]=value
    R.release()

def GV(key):
    global VARIABLE
    if key in VARIABLE:
        return VARIABLE[key]
    else:
        return None

def start_wait_time(wait_flag):		
	SV("VARIABLE."+wait_flag,time.time())
def wait_time_out(wait_flag,wait_time):	
    time_init = GV("VARIABLE."+wait_flag)
    if time_init!=None:
        #print(time.time()- time_init)
        if(time.time()- time_init> wait_time):return -1
        else:return 1
    else:return 1


def typeof(variate):
    type=None
    if isinstance(variate,int):
        type = "int"
    elif isinstance(variate,str):
        type = "str"
    elif isinstance(variate,float):
        type = "float"
    elif isinstance(variate,list):
        type = "list"
    elif isinstance(variate,tuple):
        type = "tuple"
    elif isinstance(variate,dict):
        type = "dict"
    elif isinstance(variate,set):
        type = "set"
    elif isinstance(variate,bytes):
        type = "bytes"
    return type

def read_config():
    global Config
    global Car_Config
    try:
        get_base_dir()    
        file_path=GV('base_dir')+"/CONFIG/config.json"
        with open(file_path, 'r') as f:
            Config=json.load(f)
        Config["proj_path"]=GV('base_dir')
        file_path=Config["proj_path"]+"/CONFIG/car_config.json"
        with open(file_path, 'r') as f:
            Car_Config=json.load(f)
    except Exception as e:
        message='Error:open config files'+str(e)
        raise Exception(message)

def save_result(file_name):
    global RM_VARIABLE
    global Config
    file_name=Config["proj_path"]+Config['result']['path']+'/'+file_name+'.json'
    jsondata = json.dumps(RM_VARIABLE,indent=4,separators=(',', ': '))
    #jsondata = json.dumps(RM_VARIABLE)
    with open(file_name,'w',encoding='utf-8') as f:
        f.write(jsondata)

def save_all_result(file_name):
    global RM_VARIABLE
    global Config
    file_name=Config["proj_path"]+Config['result']['path']+'/'+file_name+'.json'
    BRSTR=GV("BROADCAST")
    VIN=GV("BROADCAST.VIN")
    logname=GV('LOG_NAME')
    if BRSTR!=None: RM("BROADCAST",BRSTR,"CAR_INFO")
    if VIN!=None: RM("VIN",VIN,"CAR_INFO")
    if logname!=None: RM("LOG_NAME",logname,"CAR_INFO")
    jsondata = json.dumps(RM_VARIABLE,indent=4,separators=(',', ': '))
    #jsondata = json.dumps(RM_VARIABLE)
    with open(file_name,'w',encoding='utf-8') as f:
        f.write(jsondata)


           

def RM(test_key=None,test_vlaue=None,testname=None,phase=None):
    global RM_VARIABLE     
    save_att={}
    #if not testname:testname=self._testname 
    save_att[test_key]=test_vlaue
    save_att["save_time"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if testname=='CAR_INFO':phase='System'
    if phase==None:phase=GV("Process")
    if phase not in RM_VARIABLE:RM_VARIABLE[phase]={}
    if testname not in RM_VARIABLE[phase]:
        RM_VARIABLE[phase][testname]={}
        RM_VARIABLE[phase][testname]["save_att"]={}
        RM_VARIABLE[phase][testname]["save_att"][test_key]=save_att
        if "TestTime" not in RM_VARIABLE[phase][testname]:
            TestTime=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            RM_VARIABLE[phase][testname]["TestTime"]=TestTime
            RM_VARIABLE[phase][testname]["Status"]="Pass"
            RM_VARIABLE[phase][testname]["Phase"]=phase
    else:
        if "save_att" in RM_VARIABLE[phase][testname]:
            RM_VARIABLE[phase][testname]["save_att"][test_key]=save_att
        else:
            RM_VARIABLE[phase][testname]["save_att"]={}
            RM_VARIABLE[phase][testname]["save_att"][test_key]=save_att
    set_tabele_list(test_key,test_vlaue,testname,phase)
    set_flask_table_list(phase,test=testname,status=RM_VARIABLE[phase][testname]["Status"],testtime=RM_VARIABLE[phase][testname]["TestTime"])


def set_flask_table_list(phase,test,status,testtime):
    global flask_table_dic
    process=GV("Process")
    key=process+"_"+str(phase)+'_'+str(test)
    flask_table_dic[key]={"process": process, "phase": phase, "test": test, "status":status, "testime":testtime}



def set_tabele_list(test_key,test_vlaue,testname,phase):
    global table_value_list
    test_time=RM_VARIABLE[phase][testname]["TestTime"]
    status=RM_VARIABLE[phase][testname]["Status"]
    test_dic={"test_key":test_key,"test_vlaue":test_vlaue,"testname":testname,"test_time":test_time,"status":status,"phase":phase}
    table_value_list.append(test_dic)


def RE(test_key=None,test_vlaue=None,testname=None,phase=None):
    global RM_VARIABLE 
    error_att={}
    #if not testname:testname=self._testname
    error_att[test_key]=test_vlaue
    error_att["save_time"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if testname=='CAR_INFO':phase='System'
    if phase==None:phase=GV("Process")
    if phase not in RM_VARIABLE:RM_VARIABLE[phase]={}
    if testname not in RM_VARIABLE[phase]:
        RM_VARIABLE[phase][testname]={}
        RM_VARIABLE[phase][testname]["error_att"]={}
        RM_VARIABLE[phase][testname]["error_att"][test_key]=error_att
        if "TestTime" not in RM_VARIABLE[phase][testname]:
            TestTime=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            RM_VARIABLE[phase][testname]["TestTime"]=TestTime
            RM_VARIABLE[phase][testname]["Status"]="Fail"
            RM_VARIABLE[phase][testname]["Phase"]=phase
    else:
        if "error_att" in RM_VARIABLE[phase][testname]:
            RM_VARIABLE[phase][testname]["error_att"][test_key]=error_att
            RM_VARIABLE[phase][testname]["Status"]="Fail"
        else:
            RM_VARIABLE[phase][testname]["error_att"]={}
            RM_VARIABLE[phase][testname]["error_att"][test_key]=error_att
            RM_VARIABLE[phase][testname]["Status"]="Fail"
    set_tabele_list(test_key,test_vlaue,testname,phase)
    set_flask_table_list(phase,test=testname,status=RM_VARIABLE[phase][testname]["Status"],testtime=RM_VARIABLE[phase][testname]["TestTime"])

def GET_RM(test_key=None,testname=None,phase=None):
    global RM_VARIABLE
    if testname=='CAR_INFO':phase='System'
    if phase==None:phase=GV("Process")
    if RM_VARIABLE[phase][testname]==None:return None
    if test_key in RM_VARIABLE[phase][testname]["save_att"]:
        return RM_VARIABLE[phase][testname]["save_att"][test_key][test_key]
    else:return None 


def RM_DIC(rm_dic=None,testname=None,):
    global RM_VARIABLE       
    for key in rm_dic:
        save_att={}
        save_att[key]=rm_dic[key]
        save_att["save_time"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if testname not in RM_VARIABLE:
            RM_VARIABLE[testname]={}
            RM_VARIABLE[testname]["save_att"]=[]
            RM_VARIABLE[testname]["save_att"].append(save_att)
        else:
            if "save_att" in RM_VARIABLE[testname]:
                RM_VARIABLE[testname]["save_att"].append(save_att)
            else:
                RM_VARIABLE[testname]["save_att"]=[]
                RM_VARIABLE[testname]["save_att"].append(save_att)
 


def read_file_dic(path,file_type):
	file_dic={}
	for dirpath,dirnames,filenames in os.walk(path):
		for filename in filenames:
			aa=os.path.join(dirpath,filename)
			if file_type!="":
				filename=filename.upper()
				file_type=file_type.upper()
				fd_pose =len(filename)-filename.rfind(file_type)
				fd = filename[-fd_pose:]
				if fd.upper() ==file_type:
					fd_pose=fd_pose+1
					fe=filename[:-fd_pose]
					file_dic[fe]=aa
			else:
				filename=filename.upper()
				file_dic[filename]=aa
	return file_dic




def read_broadcast(vin):
    try:
	    path_br=Config["proj_path"]+Config["broadcast"]["path"]
	    path=path_br
	    br_file_dic={}
	    br_file_dic=read_file_dic(path,"txt")
	    swdl_info_dic={}
	    if vin in br_file_dic:
	    	with open(br_file_dic[vin], 'r') as f:
	    		br_data=f.read()
	    		SV("BROADCAST",br_data)
	    		br_data_list=br_data.split("%")
	    		for item in br_data_list:
	    			item_li=item.split(",")
	    			if len(item_li)==1:
	    				save_key="BROADCAST."+item_li[0]
	    				SV(save_key,"")
	    			else:
	    				save_key="BROADCAST."+item_li[0]
	    				save_value=','.join(item_li[1:])
	    				SV(save_key,save_value)
	    				if "$"in item_li[0] and len(item_li)>=2:
	    					#vf_br_dic[item_li[0][1:]]=item_li[2:]
	    					swdl_info_dic[item_li[0][1:]]=item_li[2:]
	    					SV(save_key+".1",item_li[1])
	    					SV(save_key+".-1",item_li[-1])
	    else:
	    	raise Exception("error get vin code:'%s', please check the broadcast files"%vin)
	    SV("SWDL_INFO",swdl_info_dic)
	    pml_str=GV("BROADCAST.PINCODE")
	    if pml_str!=None:	
	    	pml_list=pml_str.split(',')
	    	for value in pml_list:
	    		SV("PINCODE."+str(value)[0:6],str(value)[6:])
	    logname=GV('BROADCAST.VIN')+'_'+time.strftime('%Y%m%d_%H%M%S', time.localtime())
	    SV('LOG_NAME',logname)
    except Exception as e:
        raise Exception("error get broadcastinfo:'%s' ,error:%s" %(vin,e))



def m_message(message):
    global mid_message_list
    mid_message_list.append(message)
    #print(mid_message_list)
    print(message)

def init_test_value():
    global RM_VARIABLE
    global VARIABLE
    global mid_message_list
    global secreen_log_message
    try:
        
        mid_message_list=[]
        secreen_log_message=[]
        table_value_list=[]
        StartTime=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        StartTimeUTC=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        Cell=Config["DEVICE"]["Cell"]
        SWVer=Config["DEVICE"]["SWVer"]
        DCRev=Config["DEVICE"]["DCRev"]
        #RM("Phase",Phase,"CAR_INFO")
        RM("StartTime",StartTime,"CAR_INFO")
        RM("StartTimeUTC",StartTimeUTC,"CAR_INFO")
        RM("Cell",Cell,"CAR_INFO")
        RM("SWVer",SWVer,"CAR_INFO")
        RM("DCRev",DCRev,"CAR_INFO")
        RM("SeqComplete","True","CAR_INFO")
    except Exception as e:
        raise Exception("error init_test_value:'%s'" %e)
def get_dir_file_all(path):
    result = []
    get_dir = os.listdir(path)  
    for i in get_dir:          
        sub_dir = os.path.join(path,i)  
        if os.path.isdir(sub_dir):     
            get_dir_file_all(sub_dir)
        else:
            result.append(sub_dir)
    return result

def get_dir_file_all_dic(path):
    result = {}
    get_dir = os.listdir(path)  
    for i in get_dir:          
        sub_dir = os.path.join(path,i)  
        if os.path.isdir(sub_dir):     
            get_dir_file_all_dic(sub_dir)
        else:
            result[sub_dir]=i
    return result

def get_file_all_dic(path):
    result = {}
    for dirpath,dirnames,filenames in os.walk(path):
        for filename in filenames:
            aa=os.path.join(dirpath,filename)
            result[aa]=filename
    return result


def get_dir_all_file_dic(path):
    result = {}
    for dirpath,dirnames,filenames in os.walk(path):
        for filename in filenames:
            aa=os.path.join(dirpath,filename)
            result[filename]=aa
    return result


def create_dir_all(path_all):
    path_all=path_all.replace('\\','/')
    path_all_pin=path_all.rfind('/')
    path=path_all[0:path_all_pin]

    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception as e:
        create_dir_all(path)
    finally:        
        if not os.path.exists(path):
            os.mkdir(path)






def set_file_readonly(path):
    from stat import S_IREAD, S_IRGRP, S_IROTH
    #os.chmod(path, S_IREAD|S_IRGRP|S_IROTH)
    par_dir =Config["proj_path"]
    os.chdir(par_dir)
    #path=par_dir+path[1:]
    #os.chmod(path, S_IREAD+S_IRGRP+S_IROTH)
    os.chmod(path,S_IREAD|S_IRGRP|S_IROTH)
    #readobly_str="attrib +r "+path
    #os.system(readobly_str)

def set_file_write_able(path):
    from stat import S_IREAD, S_IRGRP, S_IROTH,S_IWRITE
    #os.chmod(path, S_IREAD|S_IRGRP|S_IROTH)
    par_dir = Config["proj_path"]
    os.chdir(par_dir)
    #path=par_dir+path[1:]
    #os.chmod(path, S_IREAD+S_IRGRP+S_IROTH)
    os.chmod(path,S_IWRITE)



def get_dir_file(path):
    result = []
    get_dir = os.listdir(path)  
    for i in get_dir:          
        sub_dir = os.path.join(path,i)  
        if os.path.isdir(sub_dir):     
            #get_all(sub_dir)
            continue
        else:
            result.append(sub_dir)
    return result

def do_file(o_filepath): 
    for parent,dirnames,filenames in os.walk(o_filepath):
        print(("root contain：{0}\n\n").format(parent))
        for dirname in dirnames:
          print(("  has folder：{0}\n\n").format(dirname))
        for filename in filenames:
          print(("  files：{0}\n\n").format(filename))






def get_dir_file_dic(path):
    result = {}
    get_dir = os.listdir(path)  
    for i in get_dir:          
        sub_dir = os.path.join(path,i)  
        if os.path.isdir(sub_dir):     
            #get_all(sub_dir)
            continue
        else:
            result[sub_dir]=i
    return result



def get_file_property(path,mode):
    if mode=="read":
        return os.access(path,os.R_OK)
    if mode=="write":
        return os.access(path,os.W_OK)
    if mode=="exist":
        return os.access(path,os.F_OK)


def linux_cmd(command):
    sudoPassword =Config["DEVICE"]["sudo_password"]
    ret= os.system('echo %s|sudo -S %s' % (sudoPassword, command))
    return ret




def check_connect(ip_address):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((ip_address,80)) 
    except Exception as e:
        time.sleep(5)
        return -1
    s.close()
    return 1 


def move_file(oldname,newname):      
    try:
        path_indx=-get_filename_index(newname)
        newname_path=newname[:-path_indx]
        if not os.path.exists(newname_path):
            os.makedirs(newname_path) 
        shutil.copyfile(oldname,newname)
        mov_str="move'%s' to %s'" %(oldname,newname)
        return mov_str
    except Exception as e:
        return 'Error:'+str(e)

def remove_file(path): 
    if not get_file_property(path,"write"):set_file_write_able(path)
    os.remove(path)
    while os.path.exists(path):
        time.sleep(0.1)

def move_file_dir(oldname,new_dir):      
    try:
        path_indx=get_filename_index(oldname)
        newname=new_dir+oldname[path_indx:]
        if not os.path.exists(new_dir):
            os.makedirs(new_dir) 
        shutil.copyfile(oldname,newname)
        return "move '%s' to '%s'" %(oldname,new_dir)
    except Exception as e:
        return 'Error:'+str(e)


def get_filename_index(path_str):
    aa=path_str.rfind('/')
    bb=path_str.rfind('\\')
    return max(aa,bb)
    
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)

def check_mac_address():
    mac_list=[]
    mac_list=get_mac_address_list()
    if len(mac_list)>0:
        list_mac= ["A7BEAFDB06FD","9F9F97325FED","E8B1FCB9F24E","25D6F26F3D88","C3E37BB2F122","612B24AFC3B4","C0B8838D3DCF" ,"DCA63253DEE5","DCA6322DA0F8","DCA6321A6340","DCA63253DF18","DCA6322DA137",'DCA63253DE33',"DCA63253DE34"]
        for mac in mac_list:  
            if mac in list_mac:
                return 1
        raise Exception(str(mac_list))
    else:
        raise Exception("error get car mac address")

"""
def get_mac_address_list():
    address_list=[]
    if "Linux" in platform.platform():
        address_list=[]
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:]
        mac=mac.upper()
        address_list.append(mac)
        return address_list
    else:
        for k, v in net_if_addrs().items():
            for item in v:
                address = item[1]
                if '-' in address and len(address)==17:
                    address_list.append(address.replace('-','').upper())
        return address_list
"""
def get_mac_address_list():
    address_list=[]
    if "Linux" in platform.platform():
        try:
            for line in os.popen("/sbin/ifconfig"):
                if 'Ether' in line:
                    mac_info_list=line.split(" ")
                    for value in mac_info_list:
                        if ':' in value and len(value)>10:
                            mac=value.replace(":","").upper()
                            address_list.append(mac)
        except Exception as e:
            raise Exception("error open /sbin/ifconfig")
        return address_list
    else:
        for k, v in net_if_addrs().items():
            for item in v:
                address = item[1]
                if '-' in address and len(address)==17:
                    address_list.append(address.replace('-','').upper())
        return address_list




"""
def Window_to_Linux_File(window_path, Linux_path, Linux_ip, username, password):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>Window_to_Linux_File begin')
    
    cmd='C:\STAF\lib\python\SBS\esxtest\pscp.exe -pw {password} {window_path} {username}@{Linux_ip}:{Linux_path}'.format(
              password=password, window_path=window_path, username=username, Linux_ip=Linux_ip, Linux_path=Linux_path)
    os.system(cmd)
      
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<Window_to_Linux_File end')
      
      
def Window_to_Linux_Dir(window_path, Linux_path, Linux_ip, username, password):
  print '>>>>>>>>>>>>>>>>>>>>>>>>>Window_to_Linux_Dir begin'
    
  cmd='C:\STAF\lib\python\SBS\esxtest\pscp.exe -pw {password} -r {window_path} {username}@{Linux_ip}:{Linux_path}'.format(
              password=password, window_path=window_path, username=username,Linux_ip=Linux_ip, Linux_path=Linux_path)
  os.system(cmd )
    
  print '<<<<<<<<<<<<<<<<<<<<<<<<<<Window_to_Linux_Dir end'
    
    
def Linux_to_Window_File(Linux_path, window_path, Linux_ip, username, password):
  print '>>>>>>>>>>>>>>>>>>>>>>>>>Linux_to_Window_File begin'
    
  cmd='C:\STAF\lib\python\SBS\esxtest\pscp.exe -pw {password} {username}@{Linux_ip}:{Linux_path} {window_path}'.format(
              password=password, username=username,Linux_ip=Linux_ip, Linux_path=Linux_path, window_path=window_path)
  os.system(cmd )
    
  print '<<<<<<<<<<<<<<<<<<<<<<<<<<Linux_to_Window_File end'  
     
    
def Linux_to_Window_Dir(Linux_path, window_path, Linux_ip, username, password):
  print '>>>>>>>>>>>>>>>>>>>>>>>>>Linux_to_Window_Dir begin'
    
  cmd='C:\STAF\lib\python\SBS\esxtest\pscp.exe -pw {password} -r {username}@{Linux_ip}:{Linux_path} {window_path}'.format(
              password=password, username=username,Linux_ip=Linux_ip, Linux_path=Linux_path, window_path=window_path)
  os.system(cmd)
    
  print '<<<<<<<<<<<<<<<<<<<<<<<<<<Linux_to_Window_Dir end'


"""

if __name__ == '__main__':
    check_mac_address()
