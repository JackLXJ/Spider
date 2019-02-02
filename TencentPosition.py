import requests
from bs4 import BeautifulSoup
from lxml import etree
from pyquery import PyQuery as pq
import itertools
import pandas as pd

class TencentPosition():

	"""
	功能： 定义初始变量
	参数：
		start： 起始数据
	"""
	def __init__(self, start):
		self.url = "https://hr.tencent.com/position.php?&start={}#a".format(start)
		self.headers = {
			"Host": "hr.tencent.com",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
		}
		self.file_path = "./TencentPosition.csv"

	"""
	功能： 请求目标页面
	参数：
		url： 目标链接
		headers： 请求头
	返回：
		html，页面源码
	"""
	def get_page(self, url, headers): 
		res = requests.get(url, headers=headers)
		try:
			if res.status_code == 200:
				return res.text
			else:
				return self.get_page(url, headers=headers)
		except RequestException as e:
			return self.get_page(url, headers=headers)
	
	"""
	功能： Beautiful Soup解析页面
	参数：
		html： 请求页面源码
	"""
	def soup_analysis(self, html):
		soup = BeautifulSoup(html, "lxml")
		tr_list = soup.find("table", class_="tablelist").find_all("tr")
		for tr in tr_list[1:-1]:
			position_info = [td_data for td_data in tr.stripped_strings]
			self.settle_data(position_info=position_info)

	"""
	功能： xpath解析页面
	参数：
		html： 请求页面源码
	"""
	def xpath_analysis(self, html):
		result = etree.HTML(html)
		tr_list = result.xpath("//table[@class='tablelist']//tr")
		for tr in tr_list[1:-1]:
			position_info = tr.xpath("./td//text()")
			self.settle_data(position_info=position_info)
	
	"""
	功能： pyquery解析页面
	参数：
		html： 请求页面源码
	"""
	def pyquery_analysis(self, html):
		result = pq(html)
		tr_list = result.find(".tablelist").find("tr")
		for tr in itertools.islice(tr_list.items(), 1, 11):
			position_info = [td.text() for td in tr.find("td").items()]
			self.settle_data(position_info=position_info)

	"""
	功能： 职位数据整合
	参数：
		position_info： 字段数据列表
	"""
	def settle_data(self, position_info):
		position_data = {
				"职位名称": position_info[0].replace("\xa0", " "),	# replace替换\xa0字符防止转码error
				"职位类别": position_info[1],
				"招聘人数": position_info[2],
				"工作地点": position_info[3],
				"发布时间": position_info[-1],
			}
		print(position_data)
		self.save_data(self.file_path, position_data)

	"""
	功能： 数据保存
	参数：
		file_path： 文件保存路径
		position_data： 职位数据
	"""
	def save_data(self, file_path, position_data):
		df = pd.DataFrame([position_data])
		try:
			df.to_csv(file_path, header=False, index=False, mode="a+", encoding="gbk")	# 数据转码并换行存储
		except:
			pass
"""
主函数
"""
if __name__ == "__main__":
	for page, index in enumerate(range(287)):
		print("正在爬取第{}页的职位数据:".format(page+1))
		tp = TencentPosition(start=(index*10))
		tp_html = tp.get_page(url=tp.url, headers=tp.headers)
		tp.pyquery_analysis(html=tp_html)
		print("\n")


