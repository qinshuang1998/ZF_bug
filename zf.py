# -*- coding: UTF-8 -*-  
import requests
import os
import bs4
import sys
import werobot
import re
import datetime
import MySQLdb
from PIL import Image

robot = werobot.WeRoBot(token='qs717398')
Nyear = datetime.datetime.now().year
Yyear = datetime.datetime.now().year-1
Nmonth = datetime.datetime.now().month

headers = {
			'Referer': '',
			'Host': '42.247.7.170',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Origin': 'http://42.247.7.170',
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            }
		
playload = {
			'__VIEWSTATE': '',
			'__VIEWSTATEGENERATOR': '',
			'txtUserName': '',
			'Textbox1': '',
			'TextBox2': '',
			'txtSecretCode': '',
			'RadioButtonList1': '\xd1\xa7\xc9\xfa',
			'Button1': '',
			'lbLanguage': '',
			'hidPdrs': '',
			'hidsc': '',
			}

data = {
		'UserName':'',
		'Pwd':''
		}

@robot.subscribe
def subscribe(message):
	reply = "感谢您的关注!\n如果你想要使用我，那么完全OJBK，步骤如下:\n1.回复\"登录教务\"，初次使用需要验证绑定，绑定完成后再次输入\"登录教务\"即可\n2.回复你看到的验证码，#号结束，如\"sdfg#\"\n3.回复菜单编号来查询信息\n4.结束后务必输入\"清除会话\"，以防越权操作数据问题\n\n任何问题请联系QQ:1378860132"
	return reply

@robot.filter("登录教务")
def login(message):
	openid = message.source
	res = sqlfind(openid)
	if res != 'null':
		url = "http://42.247.7.170/default2.aspx"
		mediaid = GetCall(url)
		reply = werobot.replies.ImageReply(message=message, media_id=mediaid)
		return reply
	else:
		reply = werobot.replies.ArticlesReply(message=message)
		article = werobot.replies.Article(
					title="点击进行绑定",
					description="检测到当前为首次操作，需要进行认证",
					img="http://zf.qugcloud.cn/timg2.jpg",
					url="https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx1b35b95a76735531&redirect_uri=http://zf.qugcloud.cn&response_type=code&scope=snsapi_base&state=123#wechat_redirect"
					)
		reply.add_article(article)
		return reply
		

@robot.filter(re.compile(".*?#"))
def yz(message):
	global playload
	code = message.content.strip('#')
	url = "http://42.247.7.170/default2.aspx"
	playload['txtSecretCode'] = code
	call.post(url,data=playload,headers=headers)
	try:
		islogin()
	except:
		return "登录失败,可能有以下原因:\n1.验证码是否正确输入\n2.验证码输入超时"
	else:
		return "功能菜单:\n1.查询成绩\n2.查询课表\n回复序号即可查询\ntip:仅可查询本学年!"
	
@robot.filter("1")
def score(message):
	xn = str(Yyear)+'-'+str(Nyear)
	if Nmonth<7:
		xq = '1'
	else:
		xq = '2'
	try:
		info = GetScore(xn,xq)
		onerow = xn+'\t'+'第'+xq+'学期'+'\n'
		for i in range(1,len(info)):
			onerow += info[i][0]+'\t'+info[i][1]+'\n'
		reply = werobot.replies.TextReply(message=message,content=onerow)
	except:
		return "查询失败,可能有以下原因:\n1.验证码是否正确输入\n2.未登录或登录超时"
	else:
		return reply

@robot.filter("2")
def sub(message):
	try:
		info = GetSub()
		table = '<!DOCTYPE html><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=0"><title>课程表</title><style>table,table tr th,table tr td {border:1px solid #000000;}table {text-align:center;border-collapse:collapse;}</style></head><body><table>'
		for element in info.children:
			table += str(element)
		table += '</table></body></html>'
		with open('/www/wwwroot/zf.qugcloud.cn/table.html','w') as f:
			f.write(table)
		reply = werobot.replies.ArticlesReply(message=message)
		article = werobot.replies.Article(
					title="点击查看课程表",
					description="Bug反馈联系QQ:1378860132",
					img="http://zf.qugcloud.cn/timg.jpg",
					url="http://zf.qugcloud.cn/table.html"
					)
		reply.add_article(article)
	except:
		return "查询失败,可能有以下原因:\n1.验证码是否正确输入\n2.未登录或登录超时"
	else:
		return reply

@robot.filter("清除会话")
def score(message):
	call.cookies.clear()
	return "清除成功"	

def sqlfind(openid):
	global data
	db = MySQLdb.connect("localhost","root","moxuanmusic.520","test")
	cursor = db.cursor()
	sql = "SELECT * FROM `weixin` WHERE `openid`='"+openid+"'"
	cursor.execute(sql)
	results = cursor.fetchone()
	if results:
		data['UserName'] = results[2]
		data['Pwd'] = results[3]
		db.close()
		return data
	else:
		db.close()
		return 'null'
		
def GetCall(url):
	global headers
	global playload
	headers['Referer'] = url
	html = call.get(url,headers=headers)
	soup = bs4.BeautifulSoup(html.text,'lxml')
	__VIEWSTATE = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
	__VIEWSTATEGENERATOR = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
	UserName = data['UserName']
	Pwd = data['Pwd']	
	playload['txtUserName'] = UserName
	playload['TextBox2'] = Pwd
	playload['__VIEWSTATE'] = __VIEWSTATE
	playload['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
	pic = call.get('http://42.247.7.170/CheckCode.aspx',stream=True).content
	with open('verify.png','wb') as f:
		f.write(pic)
	image_file = open('verify.png','r')
	back = client.upload_media('image',image_file)
	mediaid = back['media_id']
	return mediaid

def islogin():
	view = call.get("http://42.247.7.170/xs_main.aspx?xh="+data['UserName'],headers=headers)
	soup = bs4.BeautifulSoup(view.text,'lxml')
	name = soup.find('span', attrs={'id': 'xhxm'}).text.strip('同学')

def GetSub():
	view = call.get("http://42.247.7.170/xs_main.aspx?xh="+data['UserName'],headers=headers)
	soup = bs4.BeautifulSoup(view.text,'lxml')
	name = soup.find('span', attrs={'id': 'xhxm'}).text.strip('同学')
	url = "http://42.247.7.170/xskbcx.aspx?xh="+data['UserName']+"&xm="+name+"&gnmkdm=N121603"
	html = call.get(url,headers=headers).text
	soup = bs4.BeautifulSoup(html,'lxml')
	res = soup.find('table',attrs={'id': 'Table1'})
	return res

def GetScore(xn,xq):
	view = call.get("http://42.247.7.170/xs_main.aspx?xh="+data['UserName'],headers=headers)
	soup = bs4.BeautifulSoup(view.text,'lxml')
	name = soup.find('span', attrs={'id': 'xhxm'}).text.strip('同学')
	url = "http://42.247.7.170/xscj_gc.aspx?xh="+data['UserName']+"&xm="+name+"&gnmkdm=N121605"
	score = call.get(url,headers=headers)
	soup = bs4.BeautifulSoup(score.text,'lxml')
	__VIEWSTATE = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
	__VIEWSTATEGENERATOR = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']
	playdata = {
				'__VIEWSTATE': __VIEWSTATE,
				'__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
				'ddlXN': xn,
				'ddlXQ': xq,
				'Button1': '\xb0\xb4\xd1\xa7\xc6\xda\xb2\xe9\xd1\xaf',
				}
	info = []
	html = call.post(url,data=playdata,headers=headers).text
	soup = bs4.BeautifulSoup(html,'lxml')
	res = soup.find('table', attrs={'id': 'Datagrid1'})
	for tr in res.findAll('tr'):
		td = tr.findAll('td')
		temp = [
				td[3].contents[0],		#课程
				td[8].contents[0]		#成绩
				]
		info.append(temp)
	return info
	
if __name__=="__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')
	robot.config['HOST'] = '0.0.0.0'
	robot.config['PORT'] = 8090
	robot.config["APP_ID"] = "wx1b35b95a76735531"
	robot.config["APP_SECRET"] = "d4dcc2b47ad2f232fe23c73ff674dd26"
	client = robot.client
	call = requests.Session()
	robot.run()
	
	
