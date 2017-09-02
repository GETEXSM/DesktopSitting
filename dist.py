#Libraries
import RPi.GPIO as GPIO
import time
import sqlite3
 
#user settings
#MaxreTry = max times the program tries to get the right value, Per run script.
MaxreTry = 5 
#dbname = the place of the Database for all the measurements
dbname="/home/pi/GTdistance.db"

#MainTableName = The name of the Table where we store everything
#might get a Device-id to get this table to be cross-rpi-enabled
MainTableName="DistanceData"

#Debugging = 1 if you wanna print all debugg during run
#Debugging = 0 Silent run
Debugg = 1
 
 #Function for measurare the distance
def distance():
	#GPIO Mode (BOARD / BCM)
	GPIO.setmode(GPIO.BCM)
	 
	#set GPIO Pins
	GPIO_TRIGGER = 23
	GPIO_ECHO = 24
	 
	#set GPIO direction (IN / OUT)
	GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
	GPIO.setup(GPIO_ECHO, GPIO.IN)
	# set Trigger to HIGH
	GPIO.output(GPIO_TRIGGER, True)
 
	# set Trigger after 0.01ms to LOW
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)
 
	StartTime = time.time()
	StopTime = time.time()
 
	# save StartTime
	while GPIO.input(GPIO_ECHO) == 0:
		StartTime = time.time()
 
	# save time of arrival
	while GPIO.input(GPIO_ECHO) == 1:
		StopTime = time.time()
 
	# time difference between start and arrival
	TimeElapsed = StopTime - StartTime
	# multiply with the sonic speed (34300 cm/s)
	# and divide by 2, because there and back
	distance = (TimeElapsed * 34300) / 2
 
	GPIO.cleanup()
	return distance
	
#Function to check so the database file actually is there, if not, create it.
def Database_Status():
	if Debugg: print "Searching for: "
	if Debugg: print "Database file: " + dbname
	if Debugg: print "Table: " + MainTableName
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (MainTableName, ))
	exists = bool(curs.fetchone())
	if exists:
		if Debugg: print "Found both!"
		# there is a table named "tableName"	
		return 1
	else:
		if Debugg: print "Did not Found, Instead Creating."
		try:
			curs.execute("CREATE TABLE " + MainTableName + " (timestamp DATETIME PRIMARY KEY, distanceincm INTEGER);")
			if Debugg: print "Success on creating."
			return 1
		except:
			if Debugg: print "Failed to create."
			return 0
	#commit the changes
	conn.commit()
	conn.close()

def Save_distance(Input_Dist ):
	if Debugg: print ("Distance sent to Save_distance function = %s cm" % Input_Dist)	
	tempsql = "INSERT INTO " + MainTableName + " (timestamp, distanceincm) VALUES (datetime('now')," + str(Input_Dist) + ");"
	if Debugg: print "Using SQL: execute(" + tempsql + ")"
	
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute(tempsql)
	if Debugg: print "Success on storing values"
	conn.commit()
	conn.close()
	
if __name__ == '__main__':
	errortries = 0
	try:
		dist = distance()
		while dist > 400 or dist < 2:
			if Debugg: print "Measure error, trying again"
			if Debugg: print ("reading: %.0f cm" % dist)
			dist = distance()
			errortries += 1
	
			if errortries == 5: 
				if Debugg: print ("Stopped trying after %s tries" % MaxreTry)
				break

		if errortries < 5:
			if Database_Status():
				if Debugg: print ("Measured Distance = %.0f cm" % dist)	
				Save_distance(round(dist,1))
				
		
# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Measurement stopped by User")

