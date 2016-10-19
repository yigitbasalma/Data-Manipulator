#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import argparse

def file_manipulator(file_name, reg, mask, multiple=False):
	counts = []
	if not multiple:
		with open(file_name, "r+w") as target:
			t = target.read()
			for k,v in reg.iteritems():
				try:
					counts.append("{0}: {1}".format(k,len(v.findall(t))))
					t = v.sub(mask, t)
				except:
					counts.append("{0}: {1}".format(k, 0))
			target.seek(0)
			target.write(t)
			target.truncate()
		return (True, "İşlem tamamlandı.İstatislikler; {0} key bulundu ve değiştirildi.Aranan dosya {1}".format(", ".join(counts),\
			 file_name), 0)
	else:
		for files in file_name:
			with open(files, "r+w") as target:
				t = target.read()
				for k,v in reg.iteritems():
					try:
						counts.append("{0}: {1}".format(k,len(v.findall(t))))
						t = v.sub(mask, t)
					except:
						counts.append("{0}: {1}".format(k, 0))
				target.seek(0)
				target.write(t)
				target.truncate()
		return (True, "İşlem tamamlandı.İstatislikler; {0} key bulundu ve değiştirildi.Aranan dosyalar; {1}".format(", ".join(counts),\
			 ", ".join(file_name)), 0)


def main():
	parser = argparse.ArgumentParser(description="Manupulate sensitive data (eg: Credit Card Number etc.)", fromfile_prefix_chars="@")
	parser.add_argument("--single-file", dest="single_file", action="store", help="Single file for manipulate.")
	parser.add_argument("--multi-file", dest="multi_file", action="store", nargs="*", help="Multi file for manipulate.")
	parser.add_argument("--path", dest="dir_path", action="store", help="Manipulate for all files in directory.'Must be @ prefix'")
	parser.add_argument("-z", dest="compression", action="store",\
		 choices=["zip","rar","tar","tar.gz","bz"], help="File compression status and type.")
	parser.add_argument("--type", default="card_number" , dest="types", action="store",\
		 choices=["card_number", "cv2", "expire_date", "all"], help="Data type.")
	parser.add_argument("-c", default="*" , dest="character", action="store",\
		 choices=["*", "-", "_", "secret", "null"], help="Manipulte character.")

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(1)
	
	args = parser.parse_args()

	reg_card_number = re.compile("(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})")
	reg_expire_date = re.compile("(0[1-9]|1[0-2])\/?([0-9]{4}|[0-9]{2})")
	reg_cv2 = re.compile("[0-9]{3,4}")
	all_ = {
		"Credit Card Number": reg_card_number,
		"Credit Card Expire Date": reg_expire_date,
		"Credit Card CV2": reg_cv2
	}
	card_number_ = {
		"Credit Card Number": reg_card_number
	}
	expire_date_ = {
		"Credit Card Expire Date": reg_expire_date
	}
	cv2_ = {
		"Credit Card CV2": reg_cv2
	}
	regexps = {
		"all": all_, 
		"card_number": card_number_, 
		"expire_date": expire_date_, 
		"cv2": cv2_
	}

	if args.single_file:
		err, exit_code, msg = file_manipulator(args.single_file, regexps[args.types], args.character)
		print msg
		sys.exit(exit_code)
	elif args.multi_file:
		err, exit_code, msg = file_manipulator(args.multi_file, regexps[args.types], args.character, multiple=True)
		print msg
		sys.exit(exit_code)

if __name__ == "__main__":
	main()
