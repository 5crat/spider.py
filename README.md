关于该爬虫(爬虫有坑。。直接使用小心中招)

程序运行示例：
Spider.py -u url -d depth
　　　
　　　Url,depth 为必需参数，其他为可选参数，日志文件默认当前目录，名字：spider.log，日志等级默       认为3。数据库为：data.sql，也是当前目录。

      关键字是匹配源码中标签<meta>的content属性的值

　　　自检模块只是检查网络连接，和数据库连接。

winXP sp3 和 ubuntu12.10测试均能正常运行
　　　
目前自知的缺点：
　　　对于命令参数，没有仔细检查分析，如：spider -u s -d 2程序一样会运行


主要参考：
　　　Python爬虫      
　　　http://bbs.chinaunix.net/thread-3689276-1-1.html
　　　对Python线程池进行详细说明
　　　http://developer.51cto.com/art/201002/185290.htm
　　　BeautifulSoup学习笔记	
　　　http://pqcc.iteye.com/blog/627481
　　　python之sqlite3使用详解
      http://anony3721.blog.163.com/blog/static/5119742010716104442536/
　　　Python模块学习
　　　http://www.cnblogs.com/captain_jack/archive/2011/01/11/1933366.html
　　　
　　　
　　　
　　　
