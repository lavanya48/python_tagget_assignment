import sys, os , errno, json

if __name__ == "__main__":

	if len(sys.argv) != 2:
	    print "Enter mountpoint properly"
	    sys.exit(1)

	try:
	    os.chdir(sys.argv[1])
	except OSError as e:

	    if e.errno == errno.ENOENT:
	        print "Directory " + sys.argv[1] + " doesn't exist!"
	        sys.exit(1)

	    if e.errno == errno.EACCES:
	        print "Cannot access " + sys.argv[1] + " directory!"
	        sys.exit(1)

	    if e.errno == errno.ENOTDIR:
	        print sys.argv[1] + " is not a directory!"
	        sys.exit(1)

	files = {}
	for file in os.listdir(sys.argv[1]):
	    file = os.path.join(sys.argv[1], file)
	    if os.path.isfile(file):
	        files[file] = os.lstat(file).st_size

	# Print the list in a JSON format
	print json.dumps({"files" : files}, indent=1)
