##### creat by wang xinlei  20201029


import xmltodict
import json
import os
import G_Function as VS
from datetime import datetime
from functools import wraps
import time

class Vcats_Json:
	def __init__(self):
		self.v_json={}
		self.test=None
		self.init()
	def init(self):
		self.v_json["UNIT_IN_TEST"]={}
		##maby add featuer
		#self.v_json["UNIT_IN_TEST"]["DECODE_OPTIONS"]={}
		self.v_json["UNIT_IN_TEST"]["PROCESS"]={}
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TESTS"]={}
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TESTS"]["TEST"]=[]
		##maby add featuer
		#self.v_json["UNIT_IN_TEST"]["PROCESS"]["CONFIGURATION"]={}
		#self.v_json["UNIT_IN_TEST"]["PROCESS"]["CONFIGURATION"]["@CMID"]="VCATS"
		#self.v_json["UNIT_IN_TEST"]["PROCESS"]["CONFIGURATION"]["DATA"]=[]
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TRACE_FILES"]={}
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TRACE_FILES"]["TRACE_FILE"]={}
	def init_UNIT_IN_TEST(self):
		self.v_json["UNIT_IN_TEST"]["@VIN"]=VS.GET_RM("VIN","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["@BuildCode"]=VS.GET_RM("BROADCAST","CAR_INFO")
	def init_PROCESS(self):
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Process"]=VS.GET_RM("Process","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@StartTime"]=VS.GET_RM("StartTime","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@StartTimeUTC"]=VS.GET_RM("StartTimeUTC","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@FinishTime"]=VS.GET_RM("FinishTime","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Status"]=VS.GET_RM("Status","CAR_INFO") 	
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Cell"]=VS.GET_RM("Cell","CAR_INFO") 
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Cal"]=VS.GET_RM("StartTime","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@DCRev"]= VS.GET_RM("DCRev","CAR_INFO")
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@SWVer"]=VS.GET_RM("SWVer","CAR_INFO")	
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@OperatorID"]=""
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@RunType"]="Full"
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Retest"]="0"		
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@Latest"]="1"		
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["@SeqComplete"]=VS.GET_RM("SeqComplete","CAR_INFO")
	def append_process_test(self):	
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TESTS"]["TEST"]=self.test	
	def append_process_trace_file(self):
		self.trace_file_title=VS.GET_RM("LOG_NAME","CAR_INFO")
		week_number=datetime.now().isocalendar()[1]
		if int(week_number)>9:week_str=str(week_number)
		else:week_str='0'+str(week_number)
		year_number=datetime.now().isocalendar()[0]
		self.trace_file_path="/VCATSTRACEFILES/"+str(year_number)+"/WK"+week_str+"/"+VS.GET_RM("LOG_NAME","CAR_INFO")+"\\"+VS.GET_RM("LOG_NAME","CAR_INFO")+".log"
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TRACE_FILES"]["TRACE_FILE"]["@FileTitle"]=self.trace_file_title
		self.v_json["UNIT_IN_TEST"]["PROCESS"]["TRACE_FILES"]["TRACE_FILE"]["@FilePath"]=self.trace_file_path



def set_process_test(save_json):
	Tickcount=1
	VS.RM("Status","Pass","CAR_INFO")
	process_tests_list=[]
	process_test={}
	for phase_info in save_json:
		if phase_info=='System': continue
		for key in save_json[phase_info]:
			Tickcount=Tickcount+1
			process_test={}	
			###need  add Phase TestTime
			process_test["@Phase"]=phase_info
			process_test["@Test"]=key
			###MABY update later
			process_test["@InCycleRetestNum"]=1
			process_test["@StratRev"]=""
			process_test["@TestTime"]=save_json[phase_info][key]["TestTime"]
			if "error_att" in save_json[phase_info][key]:
				process_test["@Status"]="Fail"
				VS.RM("Status","Fail","CAR_INFO")
				process_test["FAULT_CODES"]={}
				process_test["FAULT_CODES"]["FAULT_CODE"]=[]
				for error_infos in save_json[phase_info][key]["error_att"]:
					error_info_dic={}
					error_info_dic["@Status"]="Fail"
					error_info_dic["@Faultmode"]="D"
					error_info_dic["@FaultCode"]="VC001"
					error_info_dic["@CMID"]="VCATS" 
					#aa=list(error_infos.keys())[0]
					error_info_dic["@ShortDesc"]=error_infos+' Nok'
					error_info_dic["@Testtime"]=save_json[phase_info][key]["error_att"][error_infos]['save_time']
					error_info_dic["FAULT_ATTRIBUTES"]={}
					error_info_dic["FAULT_ATTRIBUTES"]["FAULT_ATTRIBUTE"]={}
					error_info_dic["FAULT_ATTRIBUTES"]["FAULT_ATTRIBUTE"]["@Att"]=error_infos
					error_info_dic["FAULT_ATTRIBUTES"]["FAULT_ATTRIBUTE"]["@Val"]=save_json[phase_info][key]["error_att"][error_infos][error_infos]                      
					error_info_dic["FAULT_ATTRIBUTES"]["FAULT_ATTRIBUTE"]["@Tickcount"]=str(Tickcount)
					process_test["FAULT_CODES"]["FAULT_CODE"].append(error_info_dic)
					Tickcount=Tickcount+1					
			else:
				process_test["@Status"]="Pass"
			process_test["@Latest"]="1"
			if "save_att" in save_json[phase_info][key]:		   	
				process_test["TEST_ATTRIBUTES"]={}
				process_test["TEST_ATTRIBUTES"]["TEST_ATTRIBUTE"]=[]
				for save_att in save_json[phase_info][key]["save_att"]:
					save_att_dic={}
					save_att_dic["@Att"]=save_att
					save_att_dic["@Val"]=save_json[phase_info][key]["save_att"][save_att][save_att]
					save_att_dic["@Tickcount"]=Tickcount
					Tickcount=Tickcount+1
					process_test["TEST_ATTRIBUTES"]["TEST_ATTRIBUTE"].append(save_att_dic)
			process_tests_list.append(process_test)	
	return process_tests_list

def test_init(process):
	def wraps(func):
		def fun_info(*args, **kwargs):
			try:				
				
				#Process=os.path.basename(__file__)
				#Phase=func.__name__
				VS.VARIABLE={}
				VS.RM_VARIABLE={}
				VS.SV("Process",process)
				VS.init_test_value()
				VS.RM("Process",process,"CAR_INFO")
				
				func(*args, **kwargs)
				SeqComplete="True"
				VS.RM("SeqComplete",SeqComplete,"CAR_INFO")
			except Exception as err:
				SeqComplete="False"
				VS.RE("ERROR",err,"CAR_INFO")
				VS.RM("SeqComplete","Fail","CAR_INFO")
				VS.m_message(str(err))
				return(1)
			try:
				logname=VS.GV('LOG_NAME')
				VS.RM("SeqComplete",SeqComplete,"CAR_INFO")
				FinishTime=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
				VS.RM("FinishTime",FinishTime,"CAR_INFO")
				VS.save_all_result(logname)					
				creat_vcats_xml(VS.RM_VARIABLE)
			except Exception as err:				
				VS.m_message(str(err))
				return(1)
		return fun_info
	return wraps

def XmlToJson(xml_path,json_total_path):
	xml=open(xml_path,'r',encoding='UTF-8')
	xml_str=xml.read()
	xml_json=xmltodict.parse(xml_str)
	xml_json=json.dumps(xml_json,indent=4)
	with open(json_total_path,'w') as f:
		f.write(xml_json)
	#VS.set_file_readonly(json_total_path)

def jsonToXml(json_str):
    try:
        xml_str=""
        xml_str = xmltodict.unparse(json_str, encoding='utf-8',short_empty_elements=True)
    except:
        xml_str = xmltodict.unparse({'request': json_str}, encoding='utf-8')
    finally:
        return xml_str

def jsondic_to_xml(json_dic,xml_path):
	json_result = jsonToXml(json_dic)
	f = open(xml_path, 'w', encoding="UTF-8")
	f.write(json_result)
	f.close()
	


def creat_vcats_xml(save_json):
	test_json=set_process_test(save_json)
	vj=Vcats_Json()
	vj.test=test_json
	vj.init_UNIT_IN_TEST()   
	vj.init_PROCESS()
	vj.append_process_test()
	vj.append_process_trace_file()
	xml_path=VS.Config["proj_path"]+VS.Config["result"]["vcats_path"]
	log_time=datetime.now().strftime("%Y%m%d_%H%M%S")
	file_name=VS.GET_RM("VIN","CAR_INFO")+"_"+log_time+"_"+VS.GET_RM("Cell","CAR_INFO")+".xml"
	xml_path=xml_path+'/'+file_name
	jsondic_to_xml(vj.v_json,xml_path)
	VS.set_file_readonly(xml_path)
	if VS.GV("TEST_MODE")>0:
		logname=VS.GV('LOG_NAME')
		logpath=VS.Config["proj_path"]+VS.Config["DEVICE"]["ftp_log"]["upload_path"]
		log_tt=logpath+'/'+logname+'.log'
		log_finish=logpath+'/'+logname+'_finish'+'.log'
		os.rename(log_tt, log_finish)
		VS.set_file_readonly(log_finish)

if __name__ == '__main__':
	pass


