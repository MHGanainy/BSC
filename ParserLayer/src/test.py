import awsoutputgenerator as og 
import json

def readFile(fileName):
    with open(fileName, 'r') as document:
        return document.read()

if __name__ == "__main__":
    filePath = "test3.json"
    response = json.loads(readFile(filePath))

    Doc = og.OutputGenerator(response)
    # print(Doc)