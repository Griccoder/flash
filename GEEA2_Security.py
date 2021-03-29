

def Security_Access(Fix_Byte,Seed):

	# 字符串转Byte
	def String_2_hex(Fix_Byte):
		count=2
		sum_char=''

		Fix_byte_array=[]

		for char_st in Fix_Byte:
			sum_char=sum_char+char_st
			count=count-1
			if count==0:
				# print(sum_char)
				Fix_byte_array.append(sum_char)
				sum_char=''
				count=2
		return Fix_byte_array

	Seed_byte=String_2_hex(Seed)
	Fix_byte_list=String_2_hex(Fix_Byte)

	# get values of Random Seed in HEX
	# s1 = input("please enter the value of random seed S1 in Hex")
	s1 = "{0:08b}".format(int(Seed_byte[0],16)).zfill(8)
	# s2 = input("please enter the value of random seed S2 in Hex")
	s2 = "{0:08b}".format(int(Seed_byte[1],16)).zfill(8)
	# s3 = input("please enter the value of random seed S3 in Hex")
	s3 = "{0:08b}".format(int(Seed_byte[2],16)).zfill(8)

	#Convert fixed hex into bytes of octet format
	#s1 = "{0:08b}".format(0x1A).zfill(8)
	#s2 = "{0:08b}".format(0xF9).zfill(8)
	#s3 = "{0:08b}".format(0x64).zfill(8)
	f1 = "{0:08b}".format(int(Fix_byte_list[0],16)).zfill(8)
	f2 = "{0:08b}".format(int(Fix_byte_list[1],16)).zfill(8)
	f3 = "{0:08b}".format(int(Fix_byte_list[2],16)).zfill(8)
	f4 = "{0:08b}".format(int(Fix_byte_list[3],16)).zfill(8)
	f5 = "{0:08b}".format(int(Fix_byte_list[4],16)).zfill(8)
	Initial = "{0:08b}".format(0xC541A9).zfill(24)
	#Challenge Bits should be added from MSB to LSB
	challenge_bits = f5+f4+f3+f2+f1+s3+s2+s1

	# print(challenge_bits)
	#print (challenge_bits)
	#print (Initial)
	A =Initial
	for y in range(0,64):
			#Calculate Initial[LSB] XOR Challenge Bits[LSB]
			A_temp = int(A[23],2)^int(challenge_bits[63-y],2)
			#RIGHT SHIFT BY ONE POSITION
			temp = int(A,2)>>1
			#COMPENSATE FOR MISSING ZEROES IN LIST
			temp = list("{0:8b}".format(temp).zfill(23))
			#APPEND THE CALCULATED MSB
			temp.insert(0,str(A_temp))
			A = ''.join(temp)
			#XOR WITH MSB ONLY SELECTED BITS
			C24 = str(A[0])
			C23 = str(A[1])
			C22 = str(A[2])
			C21 = str(int((A[3]),2)^int(A[0],2))
			C20 = str(A[4])
			C19 = str(A[5])
			C18 = str(A[6])
			C17 = str(A[7])
			C16 = str(int(A[8],2)^int(A[0],2))
			C15 = str(A[9])
			C14 = str(A[10])
			C13 = str(int(A[11],2)^int(A[0],2))
			C12 = str(A[12])
			C11 = str(A[13])
			C10 = str(A[14])
			C9  = str(A[15])
			C8  = str(A[16])
			C7  = str(A[17])
			C6  = str(int(A[18],2)^int(A[0],2))
			C5  = str(A[19])
			C4  = str(int(A[20],2)^int(A[0],2))
			C3  = str(A[21])
			C2  = str(A[22])
			C1  = str(A[23])
			A = C24+C23+C22+C21+C20+C19+C18+C17+C16+C15+C14+C13+C12+C11+C10+C9+C8+C7+C6+C5+C4+C3+C2+C1
	#RESPONSE BYTE CALCULATION
	responsebyte01 =C12+C11+C10+C9+C8+C7+C6+C5
	responsebyte02 =C16+C15+C14+C13+C24+C23+C22+C21
	responsebyte03 =C4+C3+C2+C1+C20+C19+C18+C17
	result=hex(int(responsebyte01,2))+hex(int(responsebyte02,2))+hex(int(responsebyte03,2))
	re_list=result.split('0x')
	hex_str=''
	for value in re_list[1:]:
		if len(value)<2:value='0'+value
		hex_str=hex_str+value
	hex_str=hex_str.upper()
	#result=result.upper().replace('0X','')
	#print(result)
	# input("Press enter to exit :)")
	return hex_str

"""
# Fix_Byte='4443553031'
#Fix_Byte='5341533031'
Fix_Byte='FFFFFFFFFF'
# Fix_Byte=input('输入安全访问常数：')
#Seed='A9B474  '
Seed='5A4BC5'
# Seed=input('种子：')

AA=Security_Access(Fix_Byte,Seed)
print(AA)
"""
