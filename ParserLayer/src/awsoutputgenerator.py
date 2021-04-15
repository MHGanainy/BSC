import os, csv, sys, shutil, math
import awsparser as ap

documentCount = 0

class OutputGenerator:
    #Constructor
    def __init__(self, response):
        self.response = response
        self.document = ap.Document(response)
        self._createDic()
        self._csvData = self._outputTable()
        self._rawText = self._outputText()
        self._getAccountNumber()
        self._writeCSV(self._csvData)
        self._writeRawText(self._rawText)
        print("Successfully Created")
        
    
    def _createDic(self):
        global documentCount
        documentCount += 1
        path = os.path.join("./parsedDocs", str(documentCount))
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
        os.mkdir(path)
        self._path = "./parsedDocs/" + str(documentCount)
    
    def _writeCSV(self, csvData):
        fileName = self._path + "/table.csv"
        with open(fileName, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for item in csvData:
                writer.writerow(item)
    
    def _writeRawText(self, RawText):
        fileName = self._path + "/RawText.txt"
        with open(fileName, 'w') as text_file:
            text_file.write(self._getAccountNumber()+"\n")
            text_file.write(RawText)
    
    def _outputText(self):
        if self.document._pages[0]:
            return self.document._pages[0].getTextInReadingOrder()
    
    def _outputTable(self):
        if self.document._pages[0]:
            if self.document._pages[0]._tables[0]:
                csvData = []
                csvRow = []
                for row in self.document._pages[0]._tables[0].rows:
                    csvRow = []
                    for cell in row.cells:
                        csvRow.append(cell.text)
                    csvData.append(csvRow)
                return csvData
    
    def _getAccountNumber(self):
        wordswithAcc = self.document._pages[0].getTextWithAccount()
        wordswithOnlyNum = self.document._pages[0].getTextWithOnlyNum()
        
        minDist = math.inf
        minONIndex = -1
        
        for wordAcc in wordswithAcc:
            for idxON,wordON in enumerate(wordswithOnlyNum):
                dist = self.getDistanceBetweenBoundingBoxes(wordAcc,wordON)
                if dist < minDist:
                    minDist = dist
                    minONIndex = idxON
        return wordswithOnlyNum[minONIndex]._text
                    
                
    
    def getDistanceBetweenBoundingBoxes(self,b1,b2):
        bb1 = b1._geometry._boundingBox
        bb2 = b2._geometry._boundingBox
        
        bb1x = bb1._left
        bb1y = bb1._top
        
        bb2x = bb2._left
        bb2y = bb2._top
        
        squarexdiff = (bb2x-bb1x)**2
        squareydiff = (bb2y-bb1y)**2
        
        return math.sqrt(squarexdiff+squareydiff)