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
	return reparsed.toprettyxml(indent="\t")


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
	for item in root.findall('Цена_x0020_Прайса_x0020_Розничная'):
		good = {}
		good['price_date'] = item.find('Цена_x0020_Прайса_x0020_Розничная_x0020_Дата').text
		good['retail_price'] = item.find('Цена_x0020_Прайса_x0020_Розничная').text
		good['name'] = item.find('Номенклатура_x0020_Наименование').text
		good['gas_station'] = item.find('Объект_x0020_Управления_x0020_Родитель_x0020_ASPB').text
		good['code'] = item.find('Номенклатура_x0020_Эталон_x0020_Код').text
		raw_data.append(good)
	return raw_data

def generate_file(good_names, raw_data):
	menu = Element('menu')
	for i in raw_data:
		item = SubElement(menu, 'Item')
		code = int(i['code'])
		item_name = SubElement(item, 'Item_Name')
		item_name.text = good_names.get(code, i['name'])
		item_price = SubElement(item, 'Item_Price')
		item_price.text = i['retail_price']

	with open('output.xml', 'w') as f:
		f.write(prettify(menu))



def log(result):
	now = datetime.datetime.now()
	with open('log.txt', 'a') as f:
		if result:
			report = "{} Файл создан\n".format(now)
		else:
			report = "{} Ошибка при создании файла\n".format(now)

		f.write(report)




if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Title to pretty name converter")
	parser.add_argument('--good-name-file', '-f1', help = 'File containing name and good id', required=True)
	parser.add_argument('--raw-file', '-f2', help = 'Raw file with full information', required=True)
	args = parser.parse_args()
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