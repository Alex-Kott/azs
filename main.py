# -*- coding: utf-8 -*-
from time import sleep
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring, parse
import xml.dom.minidom as minidom
import datetime

import xlrd

def check_changes():
	return True


def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t", encoding="utf8")


def get_pretty_names(args):
	rb = xlrd.open_workbook(args.good_name_file)
	sheet = rb.sheet_by_index(0)
	goods = []
	for rownum in range(1, sheet.nrows):
		row = sheet.row_values(rownum)
		goods.append((int(row[1]), row[0]))

	return dict(goods)


def get_raw_data(args):
	tree = parse(args.raw_file)
	root = tree.getroot()
	raw_data = []
	for item in root.findall(u'Цена_x0020_Прайса_x0020_Розничная'):
		good = {}
		good['price_date'] = item.find(u'Цена_x0020_Прайса_x0020_Розничная_x0020_Дата').text
		good['retail_price'] = item.find(u'Цена_x0020_Прайса_x0020_Розничная').text
		good['name'] = item.find(u'Номенклатура_x0020_Наименование').text
		good['gas_station'] = item.find(u'Объект_x0020_Управления_x0020_Родитель_x0020_ASPB').text
		good['code'] = item.find(u'Номенклатура_x0020_Эталон_x0020_Код').text
		raw_data.append(good)
	return raw_data

def generate_file(good_names, raw_data):
	menu = Element('menu')
	for i in raw_data:
		item = SubElement(menu, 'Item')
		code = int(i['code'])
		item_name = SubElement(item, 'Item_Name_{}'.format(i['code']))
		item_name.text = good_names.get(code, i['name'])
		item_price = SubElement(item, 'Item_Price_{}'.format(i['code']))
		item_price.text = i['retail_price']

	with open(args.output_file, 'w') as f:
		f.write(prettify(menu))



def log(result):
	now = datetime.datetime.now()
	with open('log.txt', 'a') as f:
		if result:
			report = "{} Файл создан\n".format(now)
		else:
			report = "{} Ошибка при создании файла\n".format(now)

		f.write(report)

class Args:
	def __init__(self):
		self.good_name_file = 'good_confirmation.xlsx' # xlsx-файл с соответствием названия блюда и его id
		self.raw_file = 'raw_data.xml' # xml-файл с информацией о блюдах
		self.output_file = 'output.xml' # файл, куда будет выводиться результат


if __name__ == "__main__":
	args = Args()

	# with open(args.output_file, 'w') as f:
	# 	f.write(u'cdsc')
	# 	print(type(u'scsd'))
	# exit()
	
	while True:
		if check_changes():
			try:
				good_names = get_pretty_names(args)
				raw_data = get_raw_data(args)
				generate_file(good_names, raw_data)
				log(True)
			except:
				log(False)
		exit()
		sleep(60*60)