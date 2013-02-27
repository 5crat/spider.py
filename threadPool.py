#--------coding:utf-8---------

from Queue import Queue,Empty
from threading import Thread  

 
#工作线程类
class Worker(Thread):
  def __init__(self,threadPool,**kargs):
		Thread.__init__(self)
		self.threadPool = threadPool
		self.setDaemon(True)
		self.state = None	#线程工作状态
		self.start()

	def run(self):
		while True:
			if self.state == 'STOP':
				break
			try:
				func,args,kargs = self.threadPool.workQueue.get()
			except Empty:
				continue
			try:
				res = func(*args,**kargs)
				self.threadPool.resultQueue.put(res)
				self.threadPool.workDone()
			except:
				break
	#结束线程
	def stop(self):
		self.state = 'STOP'
			
#线程池类
class ThreadPool(object):
	def __init__(self,threadNum):
		#工作队列
		self.workQueue = Queue()
		#结果队列
		self.resultQueue = Queue()
		#线程池
		self.threadPool = []
		#线程数目
		self.threadNum = threadNum

	#启动线程
	def startThreads(self):
		for i in range(self.threadNum):
			self.threadPool.append(Worker(self))

	#等待线程结束
	def workJoin(self,*args,**kargs):
		self.workQueue.join()

	#添加工作任务
	def addJob(self,func,*args,**kargs):
		self.workQueue.put((func,args,kargs))

	#工作任务完成
	def workDone(self,*args):
		self.workQueue.task_done()

	#获得结果
	def getResult(self,*args,**kargs):
		return self.resultQueue.get(*args,**kargs)

	#结束线程
	def stopThreads(self):
		for thread in self.threadPool:
			#thread.join()
			thread.stop()
		del self.threadPool[:]
