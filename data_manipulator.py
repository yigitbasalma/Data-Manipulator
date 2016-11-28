#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import argparse
import time
try:
	import pyunpack
	from subprocess import Popen, PIPE
except ImportError as err:
	print "No module named %s" % err
	sys.exit(5)


def unpack(_file, path):
	paths = []
	ext = _file.split(".")
	e = ext[-1] if ext[-1] != "gz" and ext[-2] != "tar" else "tar.gz"
	try:
		pyunpack.Archive(_file).extractall(path)
		for _dir, _dirs, _files in os.walk(path):
			if len(_dirs) == 0 and len(_files) > 0:
				for i in _files:
					paths.append(os.path.join(_dir, i))
		os.unlink(_file)
		file_name = _file.split("/")[-1]
		return (False, paths, e, file_name)
	except:
		return (True, None, None, file_name)
def pack(_file, ext, compress_path, fname, tmp_dir):
	files = " ".join(_file)
	if ext == "zip":
		cmd = "zip -j -rm {0} {1}".format(os.path.join(compress_path, fname), files)
	elif ext == "tar":
		cmd = "tar --remove-files -cf {0} {1}".format(os.path.join(compress_path, fname), files)
	elif ext == "tar.gz":
		cmd = "tar --remove-files -czf {0} {1}".format(os.path.join(compress_path, fname), files)
	elif ext == "gz":
		cmd = "gzip < {1} > {0} && rm -rf {1}".format(os.path.join(compress_path, fname), files)
	else:
		cmd = None
	if cmd is not None:
		Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
		while True:
			if len(os.listdir(tmp_dir)) == 0:
				break
			else:
				time.sleep(0.1)
		return True
	else:
		return False

def is_compressed(file_name, multiple=False, compressed=False, tmp_path=None):
	compressed_types = ["zip","tar","tar.gz", "gz"]
	if not compressed and not multiple:
		ext = file_name.split(".")
		if ext[-1] in compressed_types:
			return True
		else:
			return False
	if not compressed and multiple:
		for i in file_name:
			ext = i.split(".")
			if ext[-1] in compressed_types:
				return True
		return False
	if not multiple and compressed or multiple and compressed:
		err, paths, ext, fname = unpack(file_name, tmp_path)
		if err:
			return (None, None, fname)
		else:
			return (paths, ext, fname)

def file_manipulator(file_name, reg, mask, multiple=False):
	counts = []
	if not multiple:
		with open(file_name, "r+w") as target:
			t = target.read()
			print "*" * 30
			for k,v in reg.iteritems():
				try:
					#print "{0}: {1} (File => {2})".format(k,len(v.findall(t)), file_name)
					t = v.subn(mask * 16, t)
					print "{0}: {1} (File => {2})".format(k,t[1], file_name)
				except:
					#print "{0}: {1} (File => {2})".format(k,len(v.findall(t)), file_name)
					print "{0}: {1} (File => {2})".format(k,t[1], file_name)
			print "*" * 30
			target.seek(0)
			target.write(t)
			target.truncate()
		return (0, "Done")
	elif multiple:
		for files in file_name:
			with open(files, "r+w") as target:
				t = target.read()
				print "*" * 30
				for k,v in reg.iteritems():
					try:
						print "{0}: {1} (File => {2})".format(k,len(v.findall(t)), files)
						t = v.sub(mask * 16, t)
					except:
						print "{0}: {1} (File => {2})".format(k,len(v.findall(t)), files)
				print "*" * 30
				print "\n"
				target.seek(0)
				target.write(t)
				target.truncate()
		return (0, "Done")

def dir_manipulator(path):
	files = []
	for _dir, _dirs, _files in os.walk(path):
		if len(_dirs) == 0 and len(_files) > 0:
			for i in _files:
				files.append(os.path.join(_dir, i))
	return files

def main():
	parser = argparse.ArgumentParser(description="Manupulate sensitive data (eg: Credit Card Number etc.)", fromfile_prefix_chars="@")
	parser.add_argument("--single-file", dest="single_file", action="store", help="Single file for manipulate.")
	parser.add_argument("--multi-file", dest="multi_file", action="store", nargs="*", help="Multi file for manipulate.")
	parser.add_argument("--from-dir", dest="dir_path", action="store", help="Manipulate for all files in directory.'Must be @ prefix'")
	parser.add_argument("-z", dest="compression", action="store",\
		 choices=["zip","tar","tar.gz"], help="File compression status and type.")
	parser.add_argument("--tmp-path", dest="tmp_path", action="store", help="Files open on the path.This option must be set if -z option is set")
	parser.add_argument("--compress-path", dest="compress_path", action="store",\
		 help="Files zip and put on the path.This option must be set if -z option is set")
	parser.add_argument("--type", default="card_number" , dest="types", action="store",\
		 choices=["card_number", "cv2", "expire_date", "all"], help="Data type.")
	parser.add_argument("-c", default="*" , dest="character", action="store",\
		 choices=["*", "-", "_", "secret", "null"], help="Manipulte character.")

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()

	if args.compression and not args.tmp_path and not args.compress_path:
		parser.print_help()
		print "--tmp-path and --compress-path parameter is missing."
		sys.exit(2)
	if not args.compression and args.tmp_path and args.compress_path:
		parser.print_help()
		print "--tmp-path and --compress-path option can only be with -z option."
		sys.exit(3)

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
		if not args.compression and is_compressed(args.single_file):
			print "This file is compressed.Please use -z and --tmp-path option."
			sys.exit(4)
		if not os.path.exists(args.single_file):
			print "%s is not exists." % args.single_file
			sys.exit(7)
		if not os.path.isfile(args.single_file):
                        print "%s is not a regular file." % args.single_file
                        sys.exit(6)
		if args.compression:
			f_paths, ext, fname = is_compressed(args.single_file, compressed=True, tmp_path=args.tmp_path)
			if ext is not None:
				for i in f_paths:
					exit_code, msg = file_manipulator(i, regexps[args.types], args.character)
				pack(f_paths, ext, args.compress_path, fname, args.tmp_path)
			sys.exit(exit_code)

		exit_code, msg = file_manipulator(args.single_file, regexps[args.types], args.character)
		sys.exit(exit_code)
	elif args.multi_file:
		if not args.compression and is_compressed(args.multi_file, multiple=True):
			print "This files are compressed.Please use -z and --tmp-path option."
			sys.exit(4)
		for i in args.multi_file:
			if not os.path.exists(i):
                                print "%s is not exists." % i
                                sys.exit(7)
			elif not os.path.isfile(i):
				print "%s is not a regular file." % i
				sys.exit(6)
		if args.compression:
			for i in args.multi_file:
				f_paths, ext, fname = is_compressed(i, compressed=True, tmp_path=args.tmp_path, multiple=True)
				if ext is not None:
					exit_code, msg = file_manipulator(f_paths, regexps[args.types], args.character, multiple=True)
					pack(f_paths, ext, args.compress_path, fname, args.tmp_path)
				time.sleep(0.1)
			sys.exit(exit_code)
		
		exit_code, msg = file_manipulator(args.multi_file, regexps[args.types], args.character, multiple=True)
		sys.exit(exit_code)
	elif args.dir_path:
		if not os.path.exists(args.dir_path):
                        print "%s is not exists." % args.dir_path
                        sys.exit(7)
		if not os.path.isdir(args.dir_path):
			print "%s is not a regular directory." % args.dir_path
			sys.exit(8)
		files = dir_manipulator(args.dir_path)
		if not args.compression and is_compressed(files, multiple=True):
			print "This files are compressed.Please use -z and --tmp-path option."
			sys.exit(4)
		if args.compression:
                        for i in files:
				f_paths, ext, fname = is_compressed(i, compressed=True, tmp_path=args.tmp_path, multiple=True)
				if ext is not None:
					exit_code, msg = file_manipulator(f_paths, regexps[args.types], args.character, multiple=True)
					pack(f_paths, ext, args.compress_path, fname, args.tmp_path)
				time.sleep(0.1)
			sys.exit(exit_code)

		for i in files:
			exit_code, msg = file_manipulator(i, regexps[args.types], args.character, multiple=True)
			sys.exit(exit_code)

if __name__ == "__main__":
	main()
