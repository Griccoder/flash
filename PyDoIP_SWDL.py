# -*- coding:utf-8 -*-
#__ creat by wangxinlei 20201030
import sys
import time
import json
import G_Function as vs
import os
import binascii
import PyDoIP
import logging
import logging.handlers
import socket 
import threading
from GEEA2_Security import Security_Access
from vcats_server_file import test_init

br_vbf_info_dic={}

def VBF_Read(file_path):
	aa=b""
	vbf_inf_dic={}
	with open(file_path, 'rb') as f:
		#aa_data=f.read()
		aa_data_list=f.readlines()
		aa_data=b''.join(aa_data_list)
	if len(aa_data)>4000:
		aa=aa_data[0:4000]
	else:
		aa=aa_data

	if aa.find(b'sw_signature')>0:
		start_pose=aa.find(b'sw_signature')
	elif aa.find(b'sw_signature_dev')>0:
		start_pose=aa.find(b'sw_signature_dev') 
	elif aa.find(b'erase')>0:
		start_pose=aa.find(b'erase')
	elif aa.find(b'file_checksum')>0:
		start_pose=aa.find(b'file_checksum')
	elif aa.find(b'ecu_address')>0:
		start_pose=aa.find(b'ecu_address')
	else:start_pose=0

	if aa.find(b';\r\n}',start_pose)>0:
		aa0=aa.find(b';\r\n}',start_pose)
		end_pose=aa0+4
		aa1=aa[0:aa0+3]
	elif aa.find(b';\n}',start_pose)>0:
		aa0=aa.find(b';\n}',start_pose)
		end_pose=aa0+3
		aa1=aa[0:aa0+2]
	elif aa.find(b'\n}',start_pose)>0:
		aa0=aa.find(b'\n}',start_pose)
		end_pose=aa0+2
		aa1=aa[0:aa0+1]
	elif aa.find(b'\r}',start_pose)>0:
		aa0=aa.find(b'\r}',start_pose)
		end_pose=aa0+2
		aa1=aa[0:aa0+1]
	elif aa.find(b'}',start_pose)>0:
		aa0=aa.find(b'}',start_pose)
		end_pose=aa0+1
		aa1=aa[0:aa0]		
	else:
		error="error format %s" %file_path
		raise Exception(error)		
	vbf_hex_data=aa_data[end_pose:len(aa_data)]
	vbf_infor=aa1.split(b'\n')
	for value in vbf_infor:
		value=value.strip(b'\t').strip(b'\r').strip(b';').strip(b" ")
		if b'=' in value and b'//' not in value[0:4]:
			if b";" not in value:
				vbf_infor_0=value.split(b"=")
				if len(vbf_infor_0)==2:
					vbf_inf_dic[vbf_infor_0[0].strip()]=vbf_infor_0[1].strip(b" ").lstrip(b'"').rstrip(b'"')				
				else:
					error_str="error format %s " %file_path
					vs.m_message(error_str)
					
			else:
				aa2=value.find(b";")
				value=value[0:aa2]
				vbf_infor_0=value.split(b"=")
				if len(vbf_infor_0)==2:
					vbf_inf_dic[vbf_infor_0[0].strip()]=vbf_infor_0[1].strip()				
				else:
					error_str="error format %s " %file_path
					vs.m_message(error_str)
	if b'erase' in vbf_inf_dic:
		pose0=aa1.find(b'erase')
		pose0=aa1.find(b'{',pose0)
		pose1=aa1.find(b';',pose0)
		vbf_inf_dic[b'erase']=aa1[pose0:pose1].replace(b'\n',b'').replace(b'\t',b'').replace(b' ',b'').replace(b'=',b'').replace(b'\r',b'').replace(b';',b'').strip(b'"')

	if b'sw_signature' in vbf_inf_dic:
		pose0=aa1.find(b'sw_signature')
		pose0=aa1.find(b'=',pose0)+1
		pose1=aa1.find(b';',pose0)
		vbf_inf_dic[b'sw_signature']=aa1[pose0:pose1].replace(b'\n',b'').replace(b'\t',b'').replace(b' ',b'').replace(b'=',b'').replace(b'\r',b'').replace(b';',b'').strip(b'"')

	if b'sw_signature_dev' in vbf_inf_dic:
		pose0=aa1.find(b'sw_signature_dev')
		pose0=aa1.find(b'=',pose0)+1
		pose1=aa1.find(b';',pose0)
		vbf_inf_dic[b'sw_signature_dev']=aa1[pose0+1:pose1].replace(b'\n',b'').replace(b'\t',b'').replace(b' ',b'').replace(b'=',b'').replace(b'\r',b'').replace(b';',b'').strip(b'"')

	vbf_inf_dic[b"hex_data"]=vbf_Read_hex_data_block(vbf_inf_dic,vbf_hex_data,file_path)
	return vbf_inf_dic
	
def vbf_Read_hex_data_block(vbf_inf_dic,vbf_hex_data,file_path):
	vbf_data_block={}
	#aa0=vbf_inf_dic[b"verification_block_start"][2:].decode()
	#aa0=bytes.fromhex(aa0)
	check_finish=False
	#aa0_pose=vbf_hex_data.find(aa0)
	#print(vbf_hex_data)
	aa0_pose=0
	while check_finish==False and aa0_pose>=0:
		#if aa0 in vbf_hex_data:
		try:
			data_block={}
			data_block[b"address"]=vbf_hex_data[aa0_pose:aa0_pose+4]
			data_block[b"length"]=vbf_hex_data[aa0_pose+4:aa0_pose+8]
			aa0_length_int=int.from_bytes(data_block[b"length"], byteorder='big', signed=False)
			data_block[b"data"]=vbf_hex_data[aa0_pose+8:aa0_pose+8+aa0_length_int]
			data_block[b"crc"]=vbf_hex_data[aa0_pose+8+aa0_length_int:aa0_pose+10+aa0_length_int]
			vbf_data_block[data_block[b"address"]]=data_block
			#print(len(vbf_hex_data))
			if aa0_pose+10+aa0_length_int>=len(vbf_hex_data):
				check_finish=True
				break
			else:
				aa0_pose=aa0_pose+10+aa0_length_int
		except:
			error_str="error format %s " %file_path
			vs.m_message(error_str)
			break
		"""
		else:
			print('no get %s in %s' %(aa0,vbf_inf_dic[b'sw_part_number']))
			time.sleep(2)
			break
		"""
	return vbf_data_block

def read_vbf_info():
	try:
		read_br_vbf_path()
	except Exception as err:
		err='error read_br_vbf_path'+str(err)
		raise Exception(err) 
	try:
		read_vbf_list()
	except Exception as err:
		err='error read_vbf_list'+str(err)
		raise Exception(err) 		




def read_br_vbf_path():
	global swdl_vf_path
	global swdl_vf_path_dic
	vf_path=vs.Config["proj_path"]+vs.Config["image"]["path"]
	vf_type=vs.Config["image"]["type"]
	vf_order=vs.Config["image"]["order"].split(',')
	vf_br_dic=vs.GV("SWDL_INFO")
	swdl_vf_path_dic={}
	if str(vf_type)=="1":		 
		br_file_dic=vs.read_file_dic(vf_path,"VBF")	
		for ecu in vf_order:
			if ecu in vf_br_dic:
				swdl_vf_list=vf_br_dic[ecu]
				if len(swdl_vf_list)<=2:continue
				swdl_vf_path_dic[ecu]=[]
				for vf in swdl_vf_list:
					vf=vf.upper()
					if vf in br_file_dic:
						swdl_vf_path_dic[ecu].append(br_file_dic[vf])
					else:
						error_str="error get soft download file %s "%vf
						vs.m_message(error_str)
				del vf_br_dic[ecu]
		
		for ecu in vf_br_dic:
			swdl_vf_list=vf_br_dic[ecu]
			if len(swdl_vf_list)<2:continue
			swdl_vf_path_dic[ecu]=[]
			for vf in swdl_vf_list:
				vf=vf.upper()
				if vf in br_file_dic:
					swdl_vf_path_dic[ecu].append(br_file_dic[vf])
				else:
					error_str="error get soft download file %s "%vf
					vs.m_message(error_str)
	if str(vf_type)=="2":
		br_file_dic=vs.read_file_dic(vf_path,"")
		for ecu in vf_order:
			if ecu in vf_br_dic:
				swdl_vf_list=vf_br_dic[ecu]
				if len(swdl_vf_list)<2:continue
				swdl_vf_path_dic[ecu]=[]
				for vf in swdl_vf_list:
					vf=vf.upper()
					vaaf=vf+".VBF"
					vbbf=vf[:-3]+'.'+vf[-3:]
					if vaaf in br_file_dic:
						swdl_vf_path_dic[ecu].append(br_file_dic[vaaf])					
					elif vbbf in br_file_dic:
						swdl_vf_path_dic[ecu].append(br_file_dic[vbbf])	
					else:
						error_str="error get soft download file %s "%vf
						vs.m_message(error_str)					
				del vf_br_dic[ecu]
		for ecu in vf_br_dic:
			swdl_vf_list=vf_br_dic[ecu]
			if len(swdl_vf_list)<2:continue
			swdl_vf_path_dic[ecu]=[]
			for vf in swdl_vf_list:
				vf=vf.upper()
				vaaf=vf+".VBF"
				vbbf=vf[:-3]+'.'+vf[-3:]
				if vaaf in br_file_dic:
					swdl_vf_path_dic[ecu].append(br_file_dic[vaaf])					
				elif vbbf in br_file_dic:
					swdl_vf_path_dic[ecu].append(br_file_dic[vbbf])	
				else:
					error_str="error get soft download file %s "%vf
					vs.m_message(error_str)
	vs.SV('swdl_vf_path_dic',swdl_vf_path_dic)
		#print(swdl_vf_path)

def read_vbf_list():
	global br_vbf_info_dic
	swdl_vf_path_dic=vs.GV('swdl_vf_path_dic')
	for ecu in swdl_vf_path_dic:
		for path in swdl_vf_path_dic[ecu]:	
			vbf_info_dic=VBF_Read(path)
			#vbf_key=vbf_info_dic[b'sw_part_number']+vbf_info_dic[b'sw_version']
			br_vbf_info_dic[path]=vbf_info_dic

def set_erase_ad(erase_datastr):
	re_erase_data_dic={}
	erase_data_list=eval(erase_datastr.replace(b"{", b"[").replace(b"}", b"]"))
	for key in erase_data_list:
		re_erase_data_dic[str(key)]={"start_address":int(key[0]).to_bytes(4, byteorder='big', signed=False),"end_address":int(key[1]).to_bytes(4, byteorder='big', signed=False)}
	return re_erase_data_dic

def active_mode(doip):  	
	vs.m_message("set car into active mode")
	try:
		ret=doip.send(b"\x10\x03",tx_address='1A01')
		ret=doip.send(b"\x27\x03",tx_address='1A01')
		Seed=doip.re_msg.payload[-6:]
		key = Security_Access('43454D3033',Seed)
		message='2704'+key
		ret=doip.send(message,tx_address='1A01')
		if ret>0:ret=doip.send(b"\x2F\xDD\x0A",tx_address='1A01')
		if ret>0 and doip.re_msg.payload[-2:]!="0B":
			ret=doip.send(b"\x2F\xDD\x0A",tx_address='1A01')
			ret=doip.send(b"\x22\xDD\x0A",tx_address='1A01')
			if ret<0 or doip.re_msg.payload[-2:]!="0B":
				doip.error_set("error active CEM")
		vs.RM("Active CEM","OK",testname="Active CEM")	
	except Exception as err:
		doip.log_message("error active CEM %s" %str(err))
		vs.RE("Active CEM","NOK",testname="Active CEM")
		vs.RE("Active CEM MESSAGE",str(err),testname="Active CEM")
	time.sleep(5)
	try:
		vs.m_message("Send 1FFF MESSAGE")
		vs.m_message("Wait 15s")
		try:
			ret=doip.send(b"\x31\x01\x02\x06",tx_address='1FFF')
		except Exception as err:
			pass
		try:
			ret=doip.send(b"\x10\x02",tx_address='1FFF')
		except Exception as err:
			pass

	except Exception as err:
		doip.log_message("error send IFFF message %s" %err)
		vs.RE("SEND 1FFF MESSAGE","NOK",testname="inActive CEM")	


def in_active_mode(doip):
	vs.m_message("set car into inactive mode")
	#doip=PyDoIP.DoIP_Client(logname)
	#doip.Connect()
	#vs.SV("car_address",doip._targetIPAddr)
	#doip.keep_Routing_task()
	try:
		ret=doip.send(b"\x10\x03",tx_address='1A01')
		ret=doip.send(b"\x27\x03",tx_address='1A01')
		Seed=doip.re_msg.payload[-6:]
		key = Security_Access('43454D3033',Seed)
		message='2704'+key
		ret=doip.send(message,tx_address='1A01')
		if ret>0:ret=doip.send(b"\x2F\xDD\x0A",tx_address='1A01')
		if ret>0 and doip.re_msg.payload[-2:]!="01":
			ret=doip.send(b"\x2F\xDD\x0A\x03\x01",tx_address='1A01')
			ret=doip.send(b"\x22\xDD\x0A",tx_address='1A01')
			if ret<0 or doip.re_msg.payload[-2:]!="01":
				doip.error_set("error active CEM")
				vs.RM("Active CEM","NOK",testname="Active CEM")
			else:
				vs.RM("Active CEM","OK",testname="Active CEM")	
	except Exception as err:
		doip.log_message("error active CEM %s" %err)
		vs.RE("inActive CEM","NOK",testname="inActive CEM")
		vs.RE("inActive CEM error",str(err),testname="inActive CEM")
	time.sleep(5)
	try:
		vs.m_message("Send 1FFF MESSAGE")
		vs.m_message("Wait 15s")
		try:
			ret=doip.send(b"\x31\x01\x02\x06",tx_address='1FFF')
		except Exception as err:
			pass
		try:
			ret=doip.send(b"\x10\x02",tx_address='1FFF')
		except Exception as err:
			pass

	except Exception as err:
		doip.log_message("error send IFFF message %s" %err)
		vs.RE("SEND 1FFF MESSAGE","NOK",testname="inActive CEM")	

		
    	
def get_ecu_security_access(doip,ecu):
	try:			
		level_1_2=vs.Car_Config['ecu_info'][ecu]['level_1_2']
	except Exception as err:
		vs.m_message("error get the ecu name %s in json's car_config file "%ecu)
		vs.RE("get json info ecu level_1_2 config",'NOK',testname=ecu+"_SWDL")
		return -1
	try:
		ret=doip.send(b"\x27\x01")
		myResponse=doip.re_msg.payload
	except Exception as err:
		vs.m_message("error %s get in to security access "%ecu)
		vs.RE("swdl security access",'NOK',testname=ecu+"_SWDL")
		return -1				
	if len(myResponse)>0:
		Seed=doip.re_msg.payload[-6:]
		key = Security_Access(str(level_1_2),Seed)
		try:
			ret=doip.send('2702'+key)
			return 1
		except Exception as err:
			try:
				if vs.GV("PINCODE."+ecu[0:3]+"000"):
					level_1_2=vs.GV("PINCODE."+ecu[0:3]+"000")
					ret=doip.send(b"\x27\x01")
					Seed=doip.re_msg.payload[-6:]
					key = Security_Access(str(level_1_2),Seed)
					ret=doip.send('2702'+key)
					return 1	
				else:
					ret=doip.send(b"\x10\x02")
					ret=doip.send(b"\x27\x01")
					Seed=doip.re_msg.payload[-6:]
					key = Security_Access(str(level_1_2),Seed)
					ret=doip.send('2702'+key)
					return 1
			except Exception as err:			
				vs.m_message("error %s get in to security access "%ecu)
				vs.RE("swdl security access",'NOK',testname=ecu+"_SWDL")
				return -1
	else:
		return -1


@test_init("SWDL")
def LL(vin):	
	vs.read_broadcast(vin)	
	read_vbf_info()
	sbl_name_list=vs.Config['image']['sbl_type'].split(',')
	logname=vs.GV('LOG_NAME')
	swdl_vf_path_dic=vs.GV('swdl_vf_path_dic')
	try:
		doip1=PyDoIP.DoIP_Client(logname)
		doip1._mode=0
		doip1.Connect()
	except Exception as err:
		vs.m_message(str(err))
		vs.RE("connect_car",str(err),testname="connect_car")
		try:doip1.close()
		except Exception as err:pass		
		return 1
	
	if vs.PML("AA31") or vs.PML("AAC7") or vs.PML("AAB9"):
		in_active_mode(doip1)
	else:
		active_mode(doip1)
	doip1.close()

	time.sleep(10)
	
	doip=PyDoIP.DoIP_Client(logname)
	doip._mode=0
		#doip.Connect(car_address='169.254.19.1')
	doip.Connect()
	#doip.Re_connect()
	
	try:
		doip.keep_Routing_task()
	except Exception as err:
		vs.m_message(str(err))
		vs.RE("keep_Routing_task",str(err),testname="keep_Routing_task")
		try:doip.close()
		except Exception as err:pass		
		return 1		

	for ecu in swdl_vf_path_dic:
		vs.m_message('Flashing  soft in  %s '%(ecu))
		try:	    		
			doip._tx_address=vs.Car_Config['ecu_info'][ecu]['address'][2:]
			try:
				ret=doip.send(b"\x10\x02")
				ret=doip.send(b"\x22\xF1\x86")
			except Exception as err:
				vs.m_message(str(err))
		except Exception as err:
			message="error get %s address info in json info" %ecu
			vs.m_message(message)
			vs.RE("",str(message),testname=ecu+"_SWDL")
			continue
		if get_ecu_security_access(doip,ecu)<0:
			continue		
		for path in swdl_vf_path_dic[ecu]:		
			try:
				set_str='OK'
				vbf_info_dic=br_vbf_info_dic[path]
				ecuaddress=vbf_info_dic[b'ecu_address'].decode().upper()
				vbf_name=(vbf_info_dic[b'sw_part_number']+vbf_info_dic[b'sw_version']).decode().upper()
				vbf_type=vbf_info_dic[b'sw_part_type'].decode().upper()
				data_format=binascii.unhexlify(vbf_info_dic[b'data_format_identifier'][2:])	
				vs.m_message('Flashing  vbf:  %s ,type: %s ,to : %s '%(vbf_name,vbf_type,ecu))
				doip.log_message('Flashing  vbf:  %s ,type: %s ,to : %s '%(vbf_name,vbf_type,ecu))		
										
				#if vbf_type in sbl_name_list:
				#	doip.send(b'\x22\xf1\x86')
				if b'erase' in vbf_info_dic:
					erase_datastr=vbf_info_dic[b'erase']
					erase_data_dic=set_erase_ad(erase_datastr)
					for address in erase_data_dic:
						sendstr=b'\x31\x01\xff\x00'+erase_data_dic[address]['start_address']+erase_data_dic[address]['end_address']
						try:
							doip.send(sendstr,timeout=120)
							if doip.re_msg.payload[0:8]==71010212:
								ret=doip.receive_uds_msg(message=sendstr,timeout=120)
						except Exception as err:
							if doip.re_msg.payload[0:6]!='7101FF':
								raise Exception('error erase momory') 
				flag=1;star_pose=0;end_pose=0
				for key in vbf_info_dic[b'hex_data']:
					hex_length=vbf_info_dic[b'hex_data'][key][b'length']
					hex_data=vbf_info_dic[b'hex_data'][key][b'data']
					hex_address=key
					sendstr=b'\x34'+data_format+b'\x44'+hex_address+hex_length
					ret=doip.send(sendstr)
					if ret>0:
						myResponse=doip.re_msg.payload
						sendlength=int.from_bytes(bytes.fromhex(myResponse[-4:]), byteorder='big', signed=False)
					else:continue
					while(star_pose<=len(hex_data)):				
						b_flag=flag.to_bytes(1, byteorder='little', signed=False)
						if end_pose>0:star_pose=end_pose
						else:star_pose=end_pose				
						end_pose=star_pose+sendlength-2						
						if star_pose>len(hex_data):
							ret=doip.send(b'\x37')
							#print("end_sending",key)
							flag=1;star_pose=0;end_pose=0
							break
						else:
							send_data=hex_data[star_pose:end_pose]
							aa=b'\x36'+b_flag+send_data
							re_ret=doip.send(b'\x36'+b_flag+send_data)
							if re_ret<0:break
							flag=flag+1
							if(flag>255):flag=0
					if re_ret<0:re_ret=0;continue
					if key==list(vbf_info_dic[b'hex_data'])[-1]:
						if (b'sw_signature' in vbf_info_dic or b'sw_signature_dev' in vbf_info_dic):
							if b'sw_signature' in vbf_info_dic:send_str=vbf_info_dic[b'sw_signature']
							else:send_str=vbf_info_dic[b'sw_signature_dev']				
							send_str=b'\x31\x01\x02\x12'+binascii.unhexlify(send_str[2:])
							try:ret=doip.send(send_str,timeout=10)
							except Exception as err:ret=doip.send(send_str,timeout=10)
						if vbf_type in sbl_name_list:
							call_address=binascii.unhexlify(vbf_info_dic[b'call'][2:])
							send_str=b'\x31\x01\x03\x01'+call_address
							doip.send(send_str)
						else:
							lastvf=vs.GV('BROADCAST.$'+ecu+'.-1')
							#if vbf_name==lastvf and key==list(vbf_info_dic[b'hex_data'])[-1]:
							if path.find(lastvf)>0 and key==list(vbf_info_dic[b'hex_data'])[-1]:
								#send_str=b'\x31\x01\x02\x05'+hex_address
								send_str=b'\x31\x01\x02\x05'
								ret=doip.send(send_str)				
								myResponse=doip.re_msg.payload
								if myResponse[-8:]=='00000000':
									doip.log_message("download %s vbf files ok" %ecu)
									set_str='OK'
									#print("download %s vbf files ok" %ecu)
								else:
									doip.log_message("download %s vbf files Nok" %ecu)
									set_str='NOK'
									#print("download %s vbf files Nok" %ecu)

				time.sleep(0.05)	
				vs.RM(vbf_name,set_str,testname=ecu+"_SWDL")
			except Exception as err:
				errorstr="%s"%err
				vs.RM(vbf_name,"NOK",testname=ecu+"_SWDL")
				vs.RE(vbf_name,str(errorstr),testname=ecu+"_SWDL")
				if doip._mode==0:continue
				else:break
	try:
		ret=doip.send_message(b"\x11\x01",tx_address='1FFF')	
	except Exception as err:
		vs.RE("RESET_ECU",str(err),testname="RESET_ECU")			
	finally:
		doip.close()


if __name__ == '__main__':
	pass