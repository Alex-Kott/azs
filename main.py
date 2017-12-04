# -*- coding: utf-8 -*-
from time import sleep
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring, parse
import xml.dom.minidom as minidom
import datetime
import re

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
		code = i['gas_station'].strip()
		int_code = re.findall(r'\d+', code)[0]

		if int_code != args.object_code:
			continue

		item = SubElement(menu, 'Item')
		item_name = SubElement(item, 'Item_Name_{}'.format(i['code']))
		item_name.text = good_names.get(int(i['code']), i['name'])
		item_price = SubElement(item, 'Item_Price_{}'.format(i['code']))
		item_price.text = i['retail_price']

		with open(args.output_file, 'w') as f:
			f.write(prettify(menu))

		# orderer ask do not write xml-header (<?xml version="1.0" encoding="utf8"?>)
		lines = open(args.output_file).readlines()
		open(args.output_file, 'w').writelines(lines[1:])

	

	
	



def log(msg):
	now = datetime.datetime.now()
	report = '{} {}\n'.format(now, msg)
	with open('log.txt', 'a') as f:
		f.write(report)

class Args:
	object_code = u''

	def __init__(self):
		self.good_name_file = 'good_confirmation.xlsx' # xlsx-файл с соответствием названия блюда и его id
		self.raw_file = 'raw_data.xml' # xml-файл с информацией о блюдах
		self.output_file = 'output.xml' # файл, куда будет выводиться результат
		self.object_number_file = 'object_code.txt' # файл, содержащий интересующий нас номер объекта

		with open(self.object_number_file, 'r') as f:
			
			try:
				code = f.read().strip()
				int_code = re.findall(r'\d+', code.decode('utf-8'))[0]
				self.object_code = int_code
			except Exception as e:
				print(e)
				msg = "Ошибка. Некорректно указан файл с номером объекта или файл имеет некорректное содержимое"
				print(msg)
				log(msg)
				exit()





if __name__ == "__main__":
	args = Args()

	while True:
		if check_changes():
			try:
				good_names = get_pretty_names(args)
				raw_data = get_raw_data(args)
				generate_file(good_names, raw_data)
				log("Файл создан")
			except:
				log("Ошибка при создании файла")
		exit()
		sleep(60*60)