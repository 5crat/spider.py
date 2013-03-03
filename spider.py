#------coding:utf-8------

import re
import os
import sys
import time
import urllib2
import sqlite3
import logging
from urlparse import urljoin
from Queue import Queue
from bs4 import BeautifulSoup
from threading import Thread
from datetime import datetime
from optparse import OptionParser
from locale import getdefaultlocale
from threadPool import ThreadPool

logger = logging.getLogger()

#页面爬行类
class Crawler(object):
	def __init__(self,url,depth,threadNum,dbfile,key):
		#要获取url的队列
		self.urlQueue = Queue()
		#读取的html队列
		self.htmlQueue = Queue()
		#已经访问的url
		self.readUrls = []
		#未访问的链接
		self.links = []
		#线程数
		self.threadNum = threadNum
		#数据库文件名
		self.dbfile = dbfile
		#创建存储数据库对象
		self.dataBase = SaveDataBase(self.dbfile) 
		#指点线程数目的线程池
		self.threadPool = ThreadPool(self.threadNum)
		#初始化url队列
		self.urlQueue.put(url)
		#关键字,使用console的默认编码来解码
		self.key = key.decode(getdefaultlocale()[1]) 
		#爬行深度
		self.depth = depth
		#当前爬行深度
		self.currentDepth = 1
		#当前程序运行状态
		self.state = False
		
	#获取当前页面的URL
	def work(self,url):
		try:
			html = urllib2.urlopen(url).read()
		except UnicodeError,e:
			self.urlQueue.put(url.encode('raw_unicode_escape'))
			logger.warninng(e)
			return None
		except Exception,e:
			logger.warninng(e)
			return None
		soup = BeautifulSoup(html)	
		allUrl = soup.find_all('a',href=re.compile('^http|^/'))
		if url.endswith('/'):
			url = url[:-1]
		for i in allUrl:
			if i['href'].startswith('/'):
				i['href'] = url + i['href']
			#如果该链接不在已经读取的URL列表中，把它加入该列表和队列
			if i['href'] not in self.readUrls:
				self.readUrls.append(i['href'])
				self.links.append(i['href'])
			#	print i['href'] #显示获取的链接
		if html:
			self.htmlfilter(url,html)
				
	#匹配关键字
	def htmlfilter(self,url,html):
		try:
			if self.key:
				soup = BeautifulSoup(html)
				re_string = key.split()
				#查找关键字
				if soup.findAll('meta',content = re.compile(re_string)):
					self.htmlQueue.put((url,key,html))
			else:
				self.htmlQueue.put((url,'',html))
		except Exception,e:
			logger.warninng
	def start(self):
		self.state = True
		print '\n[-] Start Crawling.........\n'
		self.threadPool.startThreads()
		#判断当前深度，确定是否继续
		while self.currentDepth <= self.depth:
			while not self.urlQueue.empty():
				url = self.urlQueue.get()
				self.threadPool.addJob(self.work,url)	#向线程池中添加工作任务
				self.readUrls.append(url)	#添加已访问的url
				self.dataBase.save(self.htmlQueue)	#保存到数据库
				self.threadPool.workJoin()
			#把获取当前深度未访问的链接放入url队列	
			for i in self.links:
				self.urlQueue.put(i)
			currentTime = int(time.time())	#当前时间
			self.currentDepth += 1
		#结束任务
		self.stop()

	def stop(self):
		self.state = False
		self.threadPool.stopThreads()
		self.dataBase.stop()

#存储数据库类
class SaveDataBase(object):
	def __init__(self,dbfile):
		#移除现有的同名数据库
		if os.path.isfile(dbfile):
			os.remove(dbfile)
		#数据库创建链接
		self.conn = sqlite3.connect(dbfile)
		#设置支持中文存储
		self.conn.text_factory = str
		self.cmd = self.conn.cursor()
		self.cmd.execute('''
			create table if not exists data(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				url text,
				key text,
				html text
				)
		''')
		self.conn.commit()

	#保存页面代码
	def save(self,htmlQueue):
		while not htmlQueue.empty():
			(url,key,html) = htmlQueue.get()
			try:
				self.cmd.execute("insert into data (url,key,html) values (?,?,?)",(url,key,html))
				self.conn.commit()
			except Exception,e:
				logger.warninng(e)
				
	#关闭数据库连接
	def stop(self):
		self.conn.close()

class printInfo(Thread):
	def __init__(self,Crawler):
		Thread.__init__(self)
		self.startTime = datetime.now()
		self.daemon = True
		self.Crawler = Crawler
		self.start()
	def run(self):
		while True:
			if self.Crawler.state == True:
				time.sleep(10)
				print '[+] CurrentDepth : %d, Totally visited %d Links.\n'%(self.Crawler.currentDepth,len(self.Crawler.readUrls))
				logger.info('CurrentDepth : %d, Totally visited %d Links.\n'%(self.Crawler.currentDepth,len(self.Crawler.readUrls)))
	def printEnd(self):
		self.endTime = datetime.now()
		print 'Crawl Depth: %d, Totally visited %d Links.\n'%(self.Crawler.currentDepth - 1,len(self.Crawler.readUrls)) 
		print 'Start at: %s' % self.startTime
		print 'End at  : %s' % self.endTime
		print 'Spend time: %s\n' % (self.endTime - self.startTime) + 'Finish!'

#日志配置函数
def logConfig(logFile,logLevel):
	#移除现有的同名日志文件
	if os.path.isfile(logFile):
		os.remove(logFile)
	#数字越大记录越详细
	LEVELS = {
		1:logging.CRITICAL,
		2:logging.ERROR,
		3:logging.WARNING,
		4:logging.INFO,
		5:logging.DEBUG
	}
	level = LEVELS[logLevel]
	logging.basicConfig(filename = logFile,level = level)
	formatter = logging.Formatter('%(actime)s %(levelname)s %(message)s')

#程序自检模块
def testself(dbfile):

	print 'Starting TestSelf ......\n'
	#测试网络，以获取百度源码为目标
	url = "http://www.baidu.com"
	netState = True		#网络状态
	pageSource = urllib2.urlopen(url).read()
	if pageSource == None:	#获取不到源码，网络状态设为False
		print 'Please check your network.'
		netState = False
	#测试数据库
	try:
		conn = sqlite3.connect(dbfile)
		cur = conn.cursor()
		cur.execute('''
			create table if not exists data (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			url text,
			key text,
			html text
			)
		''')
	except Exception,e:
		conn = None
	# 判断数据库和网络状态
	if conn == None:
		print 'DataBase Error!'
	elif netState:
		print 'The Crawler runs normally!'

if __name__ == '__main__':
	helpInfo = '%prog -u url -d depth'
	#命令行参数解析
	optParser = OptionParser(usage = helpInfo)
	optParser.add_option("-u",dest="url",type="string",help="Specify the begin url.")
	optParser.add_option("-d",dest="depth",type="int",help="Specify the crawling depth.")
	optParser.add_option("-f",dest="logFile",default="spider.log",type="string",help="The log file path, Default: spider.log.")
	optParser.add_option("-l",dest="logLevel",default="3",type="int",help="The level(1-5) of logging details. Larger number record more details. Default: 3")
	optParser.add_option("--thread",dest="thread",default="10",type="int",help="The amount of threads. Default: 10.")
	optParser.add_option("--dbfile",dest="dbfile",default="data.sql",type="string",help="The SQLite file path. Default:data.sql")
	optParser.add_option("--key",metavar="key",default="",type="string",help="The keyword for crawling. Default: None.")
	optParser.add_option("--testself",action="store_false",dest="testself",help="TestSelf")
	(options,args) = optParser.parse_args()
	#当参数中有testself时，执行自检
	if options.testself:
		testself(options.dbfile)
		#exit()
	#当不输入参数时，提示帮助信息
	if len(sys.argv) < 5:
		print optParser.print_help()
	else:
		logConfig(options.logFile,options.logLevel)	#日志配置
		spider = Crawler(options.url,options.depth,options.thread,options.dbfile,options.key)	
		info = printInfo(spider)
		spider.start()
		info.printEnd()
