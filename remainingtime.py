import requests
import time


Url = "https://svc.metrotransit.org"

#
def getresponse(Path):
	myURL = Url + Path
	try:
		result = requests.get(myURL, params = {'format': 'json'})
		if (result.ok):
			return result.json()
		else:
			raise IOError
	except:
		raise IOError

def suppressMultipleSpaces(x):
	while x.find("  ") >= 0:
		x = x.replace("  "," ")
	return x

def extractMatches(allItems, matchField, substring):
	#import pdb
	#pdb.Pdb(stdout=sys.__stdout__).set_trace()
	if (substring.upper()=="#ANY"): return allItems  # special code #ANY returns whole  list
	startMatch = False
	if (substring[0:1] == "#"):
		startMatch = True
		substring = substring[1:]
	matchingItems = [ ]
	for thisItem in allItems:
		if startMatch:
			if suppressMultipleSpaces(thisItem[matchField].upper()).find(suppressMultipleSpaces(substring.upper()+" ")) == 0:
				matchingItems.append(thisItem)
		else:
			if suppressMultipleSpaces(thisItem[matchField].upper()).find(suppressMultipleSpaces(substring.upper())) != -1:
				matchingItems.append(thisItem)
	return matchingItems

def getRouteMatches(busRoute):
	return extractMatches(getresponse("/NexTrip/Routes"),"Description", busRoute)

def getDirectionMatches(busRouteNum, busDirection):
	return extractMatches(getresponse("/NexTrip/Directions/" + busRouteNum), "Text", busDirection)

def getStopMatches(busRouteNum, busDirectionNum, busStop):
	return extractMatches(getresponse("/NexTrip/Stops/" + busRouteNum + "/" + busDirectionNum), "Text", busStop)

def getTimepointDepartures(busRouteNum, busDirectionNum, busStopCode):
	return getresponse("/NexTrip/" + busRouteNum + "/" + busDirectionNum + "/" + busStopCode)

def minutesTillBus(busTimepoint, nowTime = None):
	t = busTimepoint["DepartureTime"]
	if nowTime is None: nowTime = time.time()
	secondsFromNow = float(t[6:-2].split('-')[0])/1000.0 - nowTime
	return secondsFromNow / 60.0

def formatTimepoint(busTimepoint, nowTime = None):
	minutesFromNow = round(minutesTillBus(busTimepoint, nowTime))
	if (minutesFromNow==1):
		return "1 Minute"
	else:
		return "{:.0f} Minutes".format(minutesFromNow)

def getNextBusRecord(busTimepointList):
	for thisTimepoint in busTimepointList:
		if minutesTillBus(thisTimepoint) > 0:
			return [ thisTimepoint ]
	return [ ]

def commaList(inputList, fieldToUse):
	outstr = ""
	for thisItem in inputList:
		if outstr != "": outstr += ", "
		outstr += thisItem[fieldToUse]
	return outstr

def nextBus(busRoute, busStop, direction, returnDepartureText = False):
	try:
		#import pdb
		#pdb.Pdb(stdout=sys.__stdout__).set_trace()
		noBusReturnValue = ""

		matchingRoutes = getRouteMatches(busRoute)
		if (len(matchingRoutes) == 0): return "No match on route"
		#if (len(matchingRoutes) > 1): return "Multiple matches on route"
		BusNum = matchingRoutes[0]["Route"]

		matchingDirections = getDirectionMatches(BusNum, direction)
		if (len(matchingDirections) == 0): return "No match on direction"
		#if (len(matchingDirections) > 1): return "Multiple matches on direction "
		DirectionNum = matchingDirections[0]["Value"]

		matchingStops = getStopMatches(BusNum, DirectionNum, busStop)
		if (len(matchingStops) == 0): return "No match on stop"
		#if (len(matchingStops) > 1): return "Multiple matches on stop "
		StopCode = matchingStops[0]["Value"]

		departures = getTimepointDepartures(BusNum, DirectionNum, StopCode)
		nextDepartureRecordList = getNextBusRecord(departures)
		if (len(nextDepartureRecordList) == 0):
			print ("No departure for given route") 
			return noBusReturnValue
		if returnDepartureText:
			return nextDepartureRecordList[0]["DepartureText"]
		else:
			return formatTimepoint(nextDepartureRecordList[0])
	except IOError:
		return "NETWORK ERROR"
	except:
		return "UNKNOWN ERROR"


if __name__ == "__main__":
	import sys
	"""
	Example Command-Line: nextbus.py "bus-route" "bus-stop-name" "direction"
	#any gives complete list of route, direction or Stops
	"""

	if len(sys.argv) != 4:
		print("PARAMETER ERROR: " + helpText)
		exit(1)
	else:
		print(nextBus(sys.argv[1],sys.argv[2],sys.argv[3]))
		exit(0)
