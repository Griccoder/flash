# creat by wangxinlei 20201030

import socket
import sys
import binascii
import time
import platform
import struct
import os
from datetime import datetime
import threading
import G_Function as vs
import logging
import logging.handlers
import pylog 
import queue
import PyUDS

# import argparse

# DoIP Header Structure : <protocol version><inverse protocol version><payload type><payloadlength><payload>
# Payload format : <local ecu address> <optional: target ecu addres> <optional message ><ASRBISO><ASRBOEM>

PROTOCOL_VERSION = DOIP_PV = '02'
INVERSE_PROTOCOL_VERSION = DOIP_IPV = 'FD'

# Payload type definitions#
DOIP_GENERIC_NEGATIVE_ACKNOWLEDGE = DOIP_NARP = '0000'
DOIP_VEHICLE_ID_REQUEST = '0001'
DOIP_VEHICLE_ID_REQUEST_W_EID = '0002'
DOIP_VEHICLE_ID_REQUEST_W_VIN = '0003'
DOIP_VEHICLE_ANNOUNCEMENT_ID_RESPONSE = '0004'
# DOIP_ROUTING_ACTIVATION_REQUEST : <0005><sourceaddress><activation type><00000000>
DOIP_ROUTING_ACTIVATION_REQUEST = DOIP_RAR = '0005'
# Activation Type
DEFAULT_ACTIVATION = '00'
WWH_OBD_ACTIVATION = '01'
# 0x02-0xDF ISOSAE Reserved
CENTRAL_SECURITY_ACTIVATION = 'E0'
# 0xE1-0xFF OEM Specific
ACTIVATION_SPACE_RESERVED_BY_ISO = ASRBISO = '00000000'
# the code above is mandatory but has no use at the moment. ISOSAE Reserved
ACTIVATION_SPACE_RESERVED_BY_OEM = ASRBOEM = 'ffffffff'

DOIP_ROUTING_ACTIVATION_RESPONSE = '0006'
DOIP_ALIVE_CHECK_REQUEST = '0007'
DOIP_ALIVE_CHECK_RESPONSE = '0008'
# 0x009-0x4000: Reserved by ISO13400
DOIP_ENTITY_STATUS_REQUEST = '4001'
DOIP_ENTITY_STATUS_RESPONSE = '4002'
DOIP_DIAGNOSTIC_POWER_MODE_INFO_REQUEST = '4003'
DOIP_DIAGNOSTIC_POWER_MODE_INFO_RESPONSE = '4004'
# 0x4005-0x8000 Reserved by ISO13400
DOIP_DIAGNOSTIC_MESSAGE = DOIP_UDS = '8001'
DOIP_DIAGNOSTIC_POSITIVE_ACKNOWLEDGE = '8002'
DOIP_DIAGNOSTIC_NEGATIVE_ACKNOWLEDGE = '8003'
# 0x8004-0xEFFF Reserved by ISO13400
# 0xF000-0xFFFF Reserved for manufacturer-specific use

TIME_OUT_FOR_REMSG=5
TIME_OUT_FOR_UDP_IP=5


payloadTypeDescription = {
    int(DOIP_GENERIC_NEGATIVE_ACKNOWLEDGE): "Generic negative response",
    int(DOIP_VEHICLE_ID_REQUEST): "Vehicle ID request",
    int(DOIP_VEHICLE_ID_REQUEST_W_EID): "Vehicle ID request with EID",
    int(DOIP_VEHICLE_ID_REQUEST_W_VIN): "Vehicle ID request with VIN",
    int(DOIP_VEHICLE_ANNOUNCEMENT_ID_RESPONSE): "Vehicle announcement ID response",
    int(DOIP_ROUTING_ACTIVATION_REQUEST): "Routing activation request",
    int(DOIP_ROUTING_ACTIVATION_RESPONSE): "Routing activation response",
    int(DOIP_ALIVE_CHECK_REQUEST): "Alive check request",
    int(DOIP_ALIVE_CHECK_RESPONSE): "Alive check response",
    int(DOIP_ENTITY_STATUS_REQUEST): "Entity status request",
    int(DOIP_ENTITY_STATUS_RESPONSE): "Entity status response",
    int(DOIP_DIAGNOSTIC_POWER_MODE_INFO_REQUEST): "Diagnostic power mode info request",
    int(DOIP_DIAGNOSTIC_POWER_MODE_INFO_RESPONSE): "Power mode info response",
    int(DOIP_DIAGNOSTIC_MESSAGE): "Diagnostic message",
    int(DOIP_DIAGNOSTIC_POSITIVE_ACKNOWLEDGE): "Diagnostic positive acknowledge",
    int(DOIP_DIAGNOSTIC_NEGATIVE_ACKNOWLEDGE): "Diagnostic negative acknowledge",
}

secreen_log_message=[]

class doip_message():
    def __init__(self,message=None):
        self.init_value()

    def init_value(self):
        self.message=None
        self.length=None
        self.payload=None
        self.payloadType=None
        self.sourceAddress=None
        self.sourceAddress=None
        #self.set_re_msg(message=self.message)

class DoIPMsg:
    def __init__(self, message=None):
        pass
    def UpdateMsg(self, message=None):
        if not message:
            self.messageString = None
            self.protcolVersion = self.inverseProtocolVersion = None
            self.payloadType = self.payloadLength = None
            self.sourceAddress = self.targetAddress = None
            self.payload = ""
            self.isUDS = False
        else:
            self.messageString = message
            self.protcolVersion = message[0:2]
            self.inverseProtocolVersion = message[2:4]
            self.payloadType=message[4:8]
            self.payloadLength = message[8:16]
            self.sourceAddress = message[16:20]
            if self.payloadType == DOIP_ROUTING_ACTIVATION_REQUEST:
                self.targetAddress = message[20:24]
            else:
                self.targetAddress = message[20:24]

            if self.payloadType == DOIP_DIAGNOSTIC_MESSAGE:
                self.isUDS = True
                self.payload = message[24:len(message)]
                if len(self.payload) != 2*int(self.payloadLength,16)-8:
                    aa = message[16+2*int(self.payloadLength,16):len(message)]
                    self.UpdateMsg(message=aa)                    

            elif self.payloadType == DOIP_DIAGNOSTIC_POSITIVE_ACKNOWLEDGE:
                self.isUDS = True
                if len(message)!=16+2*int(self.payloadLength,16):              
                    aa = message[16+2*int(self.payloadLength,16):len(message)]
                    self.UpdateMsg(message=aa)
                else:
                    self.isUDS = True
                    self.payload = message[24:len(message)]
            elif self.payloadType == DOIP_ROUTING_ACTIVATION_REQUEST:
                self.payload = message[24:len(message)]              
            else:
                self.payload = message[24:len(message)]
                self.isUDS = False

    def set_re_msg(self,message=None):
        message_list=[]
        self.length=None
        self.payload=None
        self.payloadType=None
        self.sourceAddress=None
        self.sourceAddress=None
        if message==None or len(message)=='':return 1
        else:
            message_header=message[0:7]
            if message_header=='02FD800':
                messages=message.split('02FD800')
                for mess in messages:
                    re_message=doip_message()
                    if mess!='':
                        messall='800'+mess
                        payloadLength = int(mess[1:9],16)
                        payload=mess[17:]
                        sourceAddress = mess[9:13]
                        targetAddress = mess[13:17]
                        payloadType='800'+message[0:1]
                        re_message.message=messall
                        re_message.length=payloadLength
                        re_message.payload=payload
                        re_message.payloadType=payloadType
                        re_message.sourceAddress=sourceAddress
                        re_message.targetAddress=targetAddress
                        if len(payload)+8!=2*payloadLength:
                            raise Exception("error set re message %s",message)
                        else:message_list.append(re_message)
            return message_list


class DoIP_Client:

    def __init__(self,logname='',tx_address=None,re_connect=False):
        if "Window" in platform.platform(): # Checks if software is running in the Windows OS
            self._localIPAddr = socket.gethostbyname(socket.getfqdn())
        elif "Linux" in platform.platform():
            self._localIPAddr = get_ip('eth0')    
        self._localPort =13400
        self._localECUAddr = '0E80'
        self._targetIPAddr = None
        self._targetPort = None
        self._tx_address = tx_address
        self._isTCPConnected = False
        self._isRoutingActivated = False
        self._activationSwitch = False
        self.re_msg=doip_message()
        self.msg_control=DoIPMsg()
        self.rxqueue = queue.Queue()
        self.exit_requested = False
        self._mode=1
        self.test_check=0
        self._logname=logname
        self._wxll_log = pylog.TNLog(self._logname,self._mode)
        self._KeepRoutingFlag=0
        self._KeepRoutingTask=None
        sys.setrecursionlimit(5000)
        self._re_connect=re_connect
        self.rxthread_task_state=False
        vs.SV("TEST_MODE",self._mode)
        try:
            self._TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, 12, 1)#supposedly, 12 is TCP_QUICKACK option id
            time.sleep(0.1)
            self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)  # immediately send to wire wout delay
            time.sleep(0.1)
            self._TCP_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # allows different sockets to reuse ipaddress
            time.sleep(0.1)
            self._TCP_Socket.settimeout(5.0)
            #self._TCP_Socket.setblocking(1)
            time.sleep(0.5)
            self._TCP_Socket.bind((self._localIPAddr, self._localPort))
            #print( "Socket successfully created: Binded to %s:%d" % (
            #    self._TCP_Socket.getsockname()[0], self._TCP_Socket.getsockname()[1]))

        except socket.error as err:
            self._TCP_Socket = None
            errorstr="Socket creation failed with error: %s" % err
            self.error_set(errorstr)
    def __enter__(self):
        return self

    def Connect(self, car_address=None, port=13400, routingActivation=True, tx_address= None):
        if self._isTCPConnected:
            errorstr="Error :: Already connected to a server. Close the connection before starting a new one\n"
            return self.error_set(errorstr)
        else:
            if not self._TCP_Socket:
                #print( "Warning :: Socket was recently closed but no new socket was created.\nCreating new socket with last available IP address and Port")
                try:
                    self._TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, 12, 1)#supposedly, 12 is TCP_QUICKACK option id
                    self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # immediately send to wire wout delay
                    self._TCP_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self._TCP_Socket.settimeout(5.0)         
                    self._TCP_Socket.bind((self._localIPAddr, self._localPort))
                    print( "Socket successfully created: Binded to %s:%d\n" % (
                        self._TCP_Socket.getsockname()[0], self._TCP_Socket.getsockname()[1]))
                except socket.error as err:
                    #print( "Socket creation failed with error %s" % (err))
                    self._TCP_Socket = None
                    errorstr="Socket creation failed with error %s" % (err)
                    return self.error_set(errorstr)
            if self._TCP_Socket != None:
                try:
                    if car_address != None and self._targetIPAddr==None:
                        self._targetIPAddr=car_address
                    elif self._targetIPAddr!=None:pass
                    else:
                        self.get_car_address()
                    if self._targetIPAddr!=None:
                        self._TCP_Socket.connect((self._targetIPAddr, port))
                        self._isTCPConnected = True
                        print(  "Connection to DoIP established\n")
                    else:raise Exception("error get the car address")
                except socket.error as err:
                    if hasattr(err, 'winerror') and (err.winerror == 10048 )and self.test_check==0:
                        self.test_check=1
                        try:self.close()
                        except Exception as e:pass
                        self.Connect(car_address=self._targetIPAddr)
                    errorstr="Unable to connect to socket at %s:%d. Socket failed with error: %s" % (self._targetIPAddr, port, err)
                    self._targetIPAddr = None
                    self._targetPort = None
                    self._isTCPConnected = False
                    return self.error_set(errorstr)
            else:
                return -1
        
        if routingActivation == False:
            return 0
        elif routingActivation == True and self._isTCPConnected:
            try:
                self.RequestRoutingActivation()
                if self.rxthread_task_state==False:
                    self.rxthread = threading.Thread(target=self.rxthread_task)
                    self.rxthread.start()
                return 1              
            except socket.error as err:
                return self.error_set(err)
        elif routingActivation and not self._isTCPConnected:
            return self.error_set( "Error :: DoIP client is not connected to a server")

    def Re_connect(self, car_address=None, port=13400, routingActivation=True, tx_address= None):
        if not self._TCP_Socket:
            #print( "Warning :: Socket was recently closed but no new socket was created.\nCreating new socket with last available IP address and Port")
            try:
                self._TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, 12, 1)#supposedly, 12 is TCP_QUICKACK option id
                time.sleep(0.1)   
                self._TCP_Socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # immediately send to wire wout delay
                time.sleep(0.1)   
                self._TCP_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                 ##wxll
                time.sleep(0.1)   
                self._TCP_Socket.settimeout(5.0)
                #self._TCP_Socket.setblocking(1)  
                time.sleep(0.5)               
                self._TCP_Socket.bind((self._localIPAddr, self._localPort))
                print( "Socket successfully created: Binded to %s:%d\n" % (
                    self._TCP_Socket.getsockname()[0], self._TCP_Socket.getsockname()[1]))
            except socket.error as err:
                #print( "Socket creation failed with error %s" % (err))
                self._TCP_Socket = None
                errorstr="Socket creation failed with error %s" % (err)
                return self.error_set(errorstr)
        if self._TCP_Socket != None:
            try:
                if car_address != None and self._targetIPAddr==None:
                    self._targetIPAddr=car_address
                elif self._targetIPAddr!=None:pass
                else:
                    self.get_car_address()
                if self._targetIPAddr!=None:
                    self._TCP_Socket.connect((self._targetIPAddr, port))
                    self._isTCPConnected = True
                    print(  "Connection to DoIP established\n")
                else:raise Exception("error get the car address")
            except socket.error as err:
                if hasattr(err, 'winerror') and (err.winerror == 10048 )and self.test_check==0:
                    self.test_check=1
                    try:self.close()
                    except Exception as e:pass
                    self.Connect(car_address=self._targetIPAddr)
                errorstr="Unable to connect to socket at %s:%d. Socket failed with error: %s" % (self._targetIPAddr, port, err)
                self._targetIPAddr = None
                self._targetPort = None
                self._isTCPConnected = False
                return self.error_set(errorstr)
        else:
            return -1
        
        if routingActivation == False:
            return 0
        elif routingActivation == True and self._isTCPConnected:
            try:
                self.RequestRoutingActivation()
                if self.rxthread_task_state==False:
                    self.rxthread = threading.Thread(target=self.rxthread_task)
                    self.rxthread.start()
                return 1              
            except socket.error as err:
                return self.error_set(err)
        elif routingActivation and not self._isTCPConnected:
            return self.error_set( "Error :: DoIP client is not connected to a server")

    def get_car_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO, TIME_OUT_FOR_UDP_IP*1000)
            s.bind(('', 13400))
            vs.start_wait_time("udp_time")
            while True:
                data, address = s.recvfrom(65535)
                mm=data[0:4]
                if(mm==b'\x02\xfd\x00\x04'):
                    self._targetIPAddr=address[0]
                    break
                if(vs.wait_time_out("udp_time",TIME_OUT_FOR_UDP_IP)<1):
                    errorstr=" time out  get the  car address"
                    return self.error_set(errorstr)
            #try:s.close()
            #except Exception as e:pass 
        except Exception as e:
            try:s.close()
            except Exception as e:pass           
            self._targetIPAddr = None
            self._targetPort = None
            self._isTCPConnected = False
            errorstr="Unable to get the car address. Socket failed with error: %s" % (e)
            return self.error_set(errorstr)

    def DisconnectFromDoIPServer(self):
        if self._isTCPConnected:
            try:
                print( "Disconnecting from DoIP server...")
                self._TCP_Socket.shutdown(socket.SHUT_RDWR)
                self._TCP_Socket.close()
                self._TCP_Socket = None
                self._isTCPConnected = 0
            except socket.error as err:
                return self.error_set( "Unable to disconnect from socket at %s:%d. Socket failed with error: %s." % (
                    self._targetIPAddr, self._targetPort, err))
            finally:
                self._targetIPAddr = None
                self._targetPort = None
                self._isTCPConnected = 0
        else:
            return self.error_set( "Error :: DoIP client is not connected to a server")

    def RequestRoutingActivation(self, activationType=DEFAULT_ACTIVATION, localECUAddr=None, tx_address=None):
        if self._isTCPConnected:
            try:
                if not localECUAddr:
                    localECUAddr = self._localECUAddr
                if not tx_address:
                    tx_address=self._tx_address
                DoIPHeader = PROTOCOL_VERSION + INVERSE_PROTOCOL_VERSION + DOIP_ROUTING_ACTIVATION_REQUEST
                payload = localECUAddr + activationType + ASRBISO
                #payload = localECUAddr + activationType
                payloadlength = "%.8X" % int(len(payload) / 2)
                activationString = DoIPHeader + payloadlength+ payload
                if self._activationSwitch ==False:
                   self._TCP_Socket.send(bytes.fromhex(activationString))
                   activationResponse = (binascii.hexlify(self._TCP_Socket.recv(2048))).upper()
                else:
                   activationResponse = b'02fd0006000000090e8010011000000000'
                self.msg_control.UpdateMsg(activationResponse)
                if self.msg_control.payload[0:2] == b'10':
                    self._isRoutingActivated = True 
                    return 0
                else:
                    self._isRoutingActivated = False
                    return self.error_set("Unable to activate routing")

            except socket.error as err:               
                #print( "Unable to activate routing with ECU:%s. Socket failed with error: %s" % (tx_address, err))
                self._isRoutingActivated = 0
                #self._tx_address = None
                return self.error_set("Unable to activate routing with ECU. Socket failed with error: %s" % (err)) 

        else:
            print( "Unable to request routing activation. Currently not connected to a DoIP server")

    def send_uds_message(self, message, localECUAddr=None, tx_address=None,timeout=None):
        global TIME_OUT_FOR_REMSG
        if timeout==None:timeout=TIME_OUT_FOR_REMSG
        if vs.wait_time_out("uds_message_time",timeout)<1:            
            return self.error_set("send UDS message timeout.")
        if not localECUAddr:
            localECUAddr = self._localECUAddr
        if tx_address==None and self._tx_address==None:
            return self.error_set("Not set the target ecu address can not send %s!! " %message)
        elif not tx_address:
            tx_address=self._tx_address
        DoIPHeader = PROTOCOL_VERSION + INVERSE_PROTOCOL_VERSION + DOIP_DIAGNOSTIC_MESSAGE
        if vs.typeof(message)=="str":payload = localECUAddr + tx_address + message  # no ASRBISO
        if vs.typeof(message)=="bytes":message=binascii.hexlify(message).decode().upper();payload = localECUAddr + tx_address + message  # no ASRBISO
        payloadLength = "%.8X" % int(len(payload) / 2)
        UDSString = DoIPHeader + payloadLength + payload
        UDSString=UDSString.upper()
        log_msg=self._localECUAddr+'--->'+tx_address +'\tsend_message:'+UDSString
        #if self._mode==0:self.log_message(log_msg)
        if self._isTCPConnected:
            try:
                self._TCP_Socket.send(bytes.fromhex(UDSString))
                self.log_message(log_msg)
                return 1
            except socket.error as err: 
                if self._re_connect==True:        
                    self.close()
                    time.sleep(2)
                    ret=self.Connect()
                    if ret>=0:
                        return self.send_uds_message(message,tx_address=tx_address,timeout=None)
                return self.error_set("%s error. Socket failed with error: %s" % (log_msg, err))
        else:
            if self._re_connect==True:        
                self.close()
                time.sleep(2)
                ret=self.Connect()
                if ret>=0:
                    return self.send_uds_message(message,tx_address=tx_address,timeout=None)
            return self.error_set("%s error ,Not currently connected to a server" %log_msg)
    
    def send_message(self,message,tx_address=None):
        if not tx_address:
            tx_address=self._tx_address
        self.empty_rxqueue()
        vs.start_wait_time("uds_message_time")        
        ret=self.send_uds_message(message,tx_address=tx_address)
        if ret<0:
            return self.error_set("failed with send tcp message: %s" % message)
        else:return 1


    def send(self,message,tx_address=None,timeout=None):
        if not tx_address:
            tx_address=self._tx_address
        self._KeepRoutingFlag=1
        self.empty_rxqueue()
        vs.start_wait_time("uds_message_time")
        ret=self.send_uds_message(message,tx_address=tx_address,timeout=timeout)
        if ret>=0:
            self.re_finish=False
            ret=self.receive_uds_msg(message,tx_address=tx_address,timeout=timeout)
        self._KeepRoutingFlag=1
        return ret    


    def receive_uds_msg(self, message,rxBufLen=1024,localECUAddr=None, tx_address=None,timeout=None):
        global TIME_OUT_FOR_REMSG
        if self.re_finish==False:self.re_msg.init_value()
        if timeout==None:timeout=TIME_OUT_FOR_REMSG
        if vs.wait_time_out("uds_message_time",timeout)<1:
            self.re_finish=True
            return self.error_set("receive UDS message timeout.")
        if self._isTCPConnected:
            try:
                if timeout==None:timeout=TIME_OUT_FOR_REMSG
                re_message=self.wait_frame(timeout=timeout)
                if vs.typeof(re_message)=="int":return re_message
                if re_message!=None:
                    if len(re_message)==0 or re_message==b'':
                        time.sleep(0.01)
                        return self.receive_uds_msg(message,tx_address=tx_address,timeout=timeout)
                    if not localECUAddr:localECUAddr = self._localECUAddr
                    if not tx_address:tx_address = self._tx_address
                    re_message1=binascii.hexlify(re_message).decode('utf-8').upper();re_message=re_message1                                 
                    re_msg_list=self.msg_control.set_re_msg(re_message)                   
                else:
                    time.sleep(0.01)
                    return self.receive_uds_msg(message,tx_address=tx_address,timeout=timeout,)
                self.re_msg_control(re_msg_list,tx_msg=message,re_message=re_message,tx_address=tx_address)
                if self.re_finish==False:
                    return self.receive_uds_msg(message,tx_address=tx_address,timeout=timeout)
                else:return 1
            except Exception as err:
                return self.error_set( "Unable to receive UDS message. Socket failed with error: %s" % str(err))
        else:
            return self.error_set("receive uds msg error , Not currently connected to a server")

    def re_msg_control(self,msg_list=None,tx_msg=None,re_message=None ,tx_address=None):
        for msg in msg_list:
            log_str=msg.sourceAddress+'--->'+msg.targetAddress+'\trevd_message:'+msg.message
            self.log_message(log_str)
            if msg.payloadType == DOIP_GENERIC_NEGATIVE_ACKNOWLEDGE:
                self.re_finish=True
                raise Exception("DOIP GENERIC NEGATIVE ACKNOWLEDGE") 
            if msg.payloadType == DOIP_DIAGNOSTIC_NEGATIVE_ACKNOWLEDGE:
                self.re_finish=True
                raise Exception("DOIP DIAGNOSTIC NEGATIVE ACKNOWLEDGE.") 


            if tx_address!=msg.sourceAddress:
                continue
            if msg.payloadType == DOIP_DIAGNOSTIC_POSITIVE_ACKNOWLEDGE or (msg.payload[4:6] =='78' and msg.payload[0:2] =='7F'):
                continue
            if vs.typeof(tx_msg)=="str":start_flag_value =int(tx_msg[0:2],16)
            if vs.typeof(tx_msg)=="bytes":start_flag_value=int.from_bytes(tx_msg[0:1], byteorder='little', signed=True)
            if start_flag_value+0x40!=int(msg.payload[0:2],16):
                if msg.payload[0:2]=='7F' and msg.payload[4:6] in PyUDS.ERROR_DIC:
                    error_key=msg.payload[4:6]
                    message_str="uds negative respond message. %s" %PyUDS.ERROR_DIC[error_key]
                    if self.re_finish!=True:
                        self.re_msg=msg
                    self.re_finish=True
                    raise Exception(message_str) 
                    #return self.error_set(message_str)
                else:
                    continue
            else:
                self.re_msg=msg
                self.re_finish=True



    def KeepRoutingActivation(self, activationType='3E80', localECUAddr=None, tx_address=None):
        if self._isTCPConnected:
            self._KeepRoutingFlag=1
            try:
                if not localECUAddr:
                    localECUAddr = self._localECUAddr
                if not tx_address:
                    tx_address = '1FFF'
                DoIPHeader = PROTOCOL_VERSION + INVERSE_PROTOCOL_VERSION + DOIP_DIAGNOSTIC_MESSAGE
                payload = self._localECUAddr + tx_address + activationType
                payloadLength = "%.8X" % int(len(payload) / 2)
                activationString = DoIPHeader +payloadLength+ payload
                while(1):
                    if self._isTCPConnected:
                        if self._KeepRoutingFlag==1:
                            self._TCP_Socket.send(bytes.fromhex(activationString))    
                            payload = localECUAddr+'--->'+tx_address +'\tsend_message:'+ activationString
                            self.log_message(payload)
                            time.sleep(2)       
                        else: time.sleep(0.1)
                    else:break

            #except socket.error as err:
            except Exception as err:
                self._isRoutingActivated = 0
                if self._KeepRoutingFlag!=1:
                    return self.error_set( "Unable to  KEEP activate routing with ECU:%s. Socket failed with error: %s" % (
                        tx_address, err))  
        else:
            return self.error_set( "Unable to request routing activation. Currently not connected to a DoIP server")

    def close(self):
        self.log_message('close connect the doip server')
        if self._isTCPConnected:
            try:
                
                self.exit_requested = True
                self.rxthread_task_state=False
                self._KeepRoutingFlag=-1
                self._isTCPConnected = 0
                if self._KeepRoutingTask!=None:self._KeepRoutingTask.join()
                if self.rxthread!=None:self.rxthread.join()
                try:self._TCP_Socket.shutdown(socket.SHUT_RDWR)
                except Exception as err:pass
                self._TCP_Socket.close()
                self._TCP_Socket = None
            except socket.error as err:
                return self.error_set("error: %s." %err)
            finally:
                #self._wxll_log.close()
                self.exit_requested = True
                self._KeepRoutingFlag=-1
                if self._KeepRoutingTask!=None:self._KeepRoutingTask.join()
                if self.rxthread!=None:self.rxthread.join()
                self._targetIPAddr = None
                self._targetPort = None
                self._isTCPConnected = 0
        else:
            #self._wxll_log.close()
            return self.error_set("close error , Not currently connected to a server") 
   
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        print("...end")

    def error_set(self, message,err_set=-1,set_mode=1):
        if self._mode==0 or set_mode==0:
            #print(message)
            self.log_message(message)
            return err_set
        else:
            self.log_message(message)
            raise Exception(message)        

    def rxthread_task(self):
        self.rxthread_task_state=True
        while not self.exit_requested:
            try:
                data=self._TCP_Socket.recv(2048)
                if data is not None:
                    self.rxqueue.put(data)
            except socket.timeout:
                pass
            except Exception:
                self.exit_requested = True
                self.rxthread_task_state=False
    
    def wait_frame(self, timeout=5):
        if not self._isTCPConnected:
            self.error_set("Currently not connected to a DoIP server")
        else:
            timedout = False
            frame = None
            try:
                frame = self.rxqueue.get(block=True, timeout=timeout)          
            except queue.Empty:
                timedout = True
            #if timedout:
            #    return self.error_set("Did not received ISOTP frame in time (timeout=%s sec)" % timeout)
            return frame

    def empty_rxqueue(self):
        while not self.rxqueue.empty():
            re_message=self.rxqueue.get()
            if len(re_message)>0:
                re_message1=binascii.hexlify(re_message).decode('utf-8').upper();re_message=re_message1  
                if re_message[0:4]=='02FD':                                     
                    self.msg_control.UpdateMsg(re_message)
                    log_str=self.msg_control.sourceAddress+'--->'+self.msg_control.targetAddress+'\trevd_message:'+re_message
                else:
                    log_str='\trevd_message:'+re_message
                self.log_message(log_str)

    def keep_Routing_task(self):
        if self._isTCPConnected:
            self._KeepRoutingTask=threading.Thread(target=self.KeepRoutingActivation)
            self._KeepRoutingTask.setDaemon(True)
            self._KeepRoutingTask.start()
            #t1.join()
        else:
            return self.error_set( "Unable to request routing activation. Currently not connected to a DoIP server")



    def log_message(self,message):
        global secreen_log_message
        self._wxll_log.write(message)
        time_str=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        message=time_str+':  '+message
        message=message.replace('\t','  ')
        if len(message)>150:vs.secreen_log_message.append(message[:150]+'...')
        else:vs.secreen_log_message.append(message)






 
def get_ip(ifname):

    import socket
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15].encode('utf-8')))
    )[20:24])
 




if __name__ == '__main__':
    vs.read_config()

    #message='02FD8002000000051FFF0E8000'
    #message='02FD8003000000051A210E8003'
    #aa=DoIPMsg()
    #aa.UpdateMsg(message)
    logname='111122222'+time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    doip=DoIP_Client(logname=logname)    
    #doip.Connect(car_address='169.254.92.237')
    doip.Connect()
    doip.keep_Routing_task()
    while(1):
        time.sleep(1)
        doip.send('1001',tx_address='1601')
        print("wait....")