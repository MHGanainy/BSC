# Import Statements
import time
import awsoutputgenerator as aog
# Queue JSON
JSONQueue = []

def monitorQueue():
    while True:
        for jsonD in JSONQueue:
            aog.OutputGenerator(jsonD)
            JSONQueue.remove(jsonD)
        time.sleep(5)