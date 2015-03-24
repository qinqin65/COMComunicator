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

INSTRUCT_ISBINFULL = '%01#RCSR1201**'
INSTRUCT_BINFULLAMOUNT = '%01#RDD0051200512**'
INSTRUCT_READBINCNT = '%01#RDD0050200502**'

class comCon:
	def __init__(self,com,baud,databit,parity,stopbit):
		try:
			self.ser = serial.Serial(COM, BAUD,DATABIT,PARITY,STOPBIT)
		except Exception, e:
			print 'open serial failed'
			self.ser = None
	
	def __del__(self):
		self.ser.close()

def getVal(inst):
	comSer = comCon(COM,BAUD,DATABIT,PARITY,STOPBIT)
	if(comSer==None):
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
			elif(buf=='getBinCnt'):
				value = getVal(INSTRUCT_READBINCNT)
				if(value.find('$')>0):
					tmp = value[8:10]+value[6:8]
					while tmp[0] == '0':
						tmp = tmp[1:]
						if(len(tmp)==1):
							break
					connection.send(str(hexStrToInt(tmp)))
				else:
					connection.send('-1')

		except Exception,e:
			print e
		finally:
			if connection != None:
				connection.close()

if __name__ == '__main__':
    main()