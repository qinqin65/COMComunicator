import serial
import sys
import socket
import time
import math

COM = 'COM3'
BAUD = 115200
DATABIT = 8
PARITY = 'O'
STOPBIT = 1

IP = '0.0.0.0'
PORT = 12007

INSTRUCT_ISBINFULL = '%EE#RCSR2002**'
INSTRUCT_BINFULLNO = '%EE#RDD0024000240**'
INSTRUCT_BINFULLAMOUNT = '%EE#RDD0060300603**'
INSTRUCT_READBINCNT = '%EE#RDD0200002131**'
INSTRUCT_READMAGNUMBINCNT = '%EE#RDD0047000479**'

class comCon:
	def __init__(self,com,baud,databit,parity,stopbit):
		try:
			self.ser = serial.Serial(COM, BAUD,DATABIT,PARITY,STOPBIT)
		except Exception, e:
			print 'open serial failed'
			self.ser = None
	
	def __del__(self):
		if(self.ser!=None):
			self.ser.close()

def getVal(inst):
	comSer = comCon(COM,BAUD,DATABIT,PARITY,STOPBIT)
	if(comSer.ser==None):
		return '-1'
	print 'write:'+inst
	comSer.ser.write(inst+'\r')
	comSer.ser.flush()
	reply = ''
	while True:
		tmp = comSer.ser.read()
		reply += tmp
		if(tmp=='\r'):
			break
	print 'read:'+reply
	return reply

def getHexInt(hexStr):
	if(hexStr=='A'):return 10
	elif(hexStr=='B'):return 11
	elif(hexStr=='C'):return 12
	elif(hexStr=='D'):return 13
	elif(hexStr=='E'):return 14
	elif(hexStr=='F'):return 15
	else:return int(hexStr)

def hexStrToInt(hexStr):
	value = 0
	l = len(hexStr)
	c = 0
	for i in hexStr:
		value += getHexInt(i)*math.pow(16,l-c-1)
		c+=1
	return int(value)

def main():
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.bind((IP,PORT))
	sock.listen(1)
	
	while True:
		connection, address=sock.accept()
		try:
			buf=connection.recv(1024)
			buf = buf.rstrip('\r\n')
			print 'recv:'+buf
			value = ''
			if(buf=='getIsBinFull'):
				value = getVal(INSTRUCT_ISBINFULL)
				if(value.find('RC1')>0):
					connection.send('true')
				else:
					connection.send('false')
			elif(buf=='getBinFullAmount'):
				value = getVal(INSTRUCT_BINFULLAMOUNT)
				if(value.find('$')>0):
					tmp = value[8:10]+value[6:8]
					while tmp[0] == '0':
						tmp = tmp[1:]
						if(len(tmp)==1):
							break
					connection.send(str(hexStrToInt(tmp)))
				else:
					connection.send('-1')
			elif(buf=='getBinFullNo'):
				value = getVal(INSTRUCT_BINFULLNO)
				if(value.find('$')>0):
					tmp = value[8:10]+value[6:8]
					while tmp[0] == '0':
						tmp = tmp[1:]
						if(len(tmp)==1):
							break;
					connection.send(tmp)
				else:
					connection.send('-1')
			elif(buf=='getBinMagnumCnt'):
				value = getVal(INSTRUCT_READMAGNUMBINCNT)
				if(value=='-1'):
					continue
				value = value[6:]
				valStr = ''
				j = 0
				for i in range(5):
					tmp = value[j:j+8]
					tmp = tmp[6:8] + tmp[4:6] + tmp[2:4] + tmp[0:2]
					valStr += str(hexStrToInt(tmp)) + ','
					j += 8
				connection.send(valStr.rstrip(','))
			elif(buf=='getBinCnt'):
				if(value=='-1'):
					continue
				ins  = INSTRUCT_READBINCNT
				instLis = []
				instLis.append(ins.replace('0200002131', '0200002026'))
				instLis.append(ins.replace('0200002131', '0202702053'))
				instLis.append(ins.replace('0200002131', '0205402080'))
				instLis.append(ins.replace('0200002131', '0208102107'))
				instLis.append(ins.replace('0200002131', '0210802131'))
				
				valStr = ''
				for lis in instLis:
					value = getVal(lis)
					value = value[6:]
					j = 0
					for i in range(len(value)/4):
						tmp = value[j:j+4]
						tmp = tmp[2:4] + tmp[0:2]
						valStr += str(hexStrToInt(tmp)) + ','
						j+=4
				connection.send(valStr.rstrip(','))

		except Exception,e:
			print e
		finally:
			if connection != None:
				connection.close()

if __name__ == '__main__':
    main()