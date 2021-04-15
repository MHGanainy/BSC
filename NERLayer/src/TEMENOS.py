# Import Statments
import pandas as pd
import numpy as np
import csv
import aws
# Global Variables
# Class Declaration
class TEMENOS:
    #Constructor
    def __init__(self,Path,AccNum):
        self.AccNum = AccNum
        self.Path = Path
        self.RawTextPath = Path + "/RawText.txt"
        self.TableCSVPath = Path + "/table.csv"
        self.initialization()
        
    def initialization(self):
        self.convert_csv_to_pd()
        self.check_columns_fix("ValueDate")
        self.df_correction()
        self.add_extra_col("ExtraRef")
        self.add_extra_col("Amount")
        self.add_extra_col("TT")
        self.add_extra_col("Category")
        self.remove_row([0])
        self.fix_double_row()
        self.define_transfer_type('Debit','CreditClosingBalance')
        self.remove_column("BookDate")
        self.rule_based_category()
        self.csv_gen()
        self.adjust_table_csv()
        self._writeCSV()
        self.save_to_csv()
        aws.uploadS3Object(self.Path,str(self.AccNum)+".csv")
        # print(self.tablePD)
        
    def convert_csv_to_pd(self):
        self.tablePD = pd.read_csv(self.TableCSVPath)
        self.tablePD.columns = self.tablePD.columns.str.replace(' ', '')
    def check_columns_fix(self,col_name):
        if col_name not in self.tablePD.columns:
            for index,row in self.tablePD.iterrows():
                res = [elem.replace(' ', '') for elem in row.tolist()]
                if col_name in res:
                    column_index = index
                    break
            if(column_index>0):
                for i in range(column_index):
                    self.remove_row(i)
                column_index = 0
            self.tablePD.reset_index(drop=True, inplace=True)
            res = [elem.replace(' ', '') for elem in self.tablePD.iloc[0].tolist()]
            self.tablePD = self.tablePD[1:]
            self.tablePD.columns = res
            self.tablePD.reset_index(drop=True, inplace=True)
            
    def df_correction(self):
        self.tablePD = self.tablePD.replace(np.nan, "")
    
    def add_extra_col(self, col_name):
        self.tablePD[col_name] = ""
    
    def remove_row(self,indicies):
        self.tablePD = self.tablePD.drop(indicies)
    
    def fix_double_row(self):
        indicies_to_be_removed = []
        for index, row in self.tablePD.iterrows():
            if row['ValueDate'] == "":
                indicies_to_be_removed.append(index)
                self.tablePD.loc[index-1,"ExtraRef"] = self.tablePD.loc[index-1,"Reference"] + " " + self.tablePD.loc[index-1,"Descript"] + " " +row['Descript']
            elif row['ExtraRef'] == "":
                row["ExtraRef"] =  row["Reference"] + " " + row["Descript"]
        self.remove_row(indicies_to_be_removed)
    
    def define_transfer_type(self,CreditName,DebitName):
        for index, row in self.tablePD.iterrows():
            if row[DebitName] != "":
                self.tablePD.loc[index,"TT"] = "D"
                self.tablePD.loc[index,"Amount"] = row[DebitName]
            else:
                self.tablePD.loc[index,"TT"] = "C"
                self.tablePD.loc[index,"Amount"] = row[CreditName]
        self.tablePD.drop(DebitName,axis='columns', inplace=True)
        self.tablePD.drop(CreditName,axis='columns', inplace=True)

    def remove_column(self, col_name):
        self.tablePD.drop(col_name,axis='columns', inplace=True)
        
    def rule_based_category(self):
        for index, row in self.tablePD.iterrows():
            if "FT" in row["Reference"]:
                if row["TT"] == "C":
                    self.tablePD.loc[index,"Category"] = "C1"
                elif row["TT"] == "D":
                    self.tablePD.loc[index,"Category"] = "C2"
            elif "CHG" in row["Reference"]:
                if row["TT"] == "C":
                    self.tablePD.loc[index,"Category"] = "C3"
                elif row["TT"] == "D":
                    self.tablePD.loc[index,"Category"] = "C4"
            else:
                self.tablePD.loc[index,"Category"] = "C5"
    
    def adjust_table_csv(self):
        self.output_csv = self.tablePD.copy()
        self.output_csv.drop("Descript",axis='columns', inplace=True)
        self.output_csv.drop("Reference",axis='columns', inplace=True)
        self.output_csv["Debit Amount"] = self.output_csv.loc[self.output_csv['TT'] == "C"]["Amount"]
        self.output_csv["Credit Amount"] = self.output_csv.loc[self.output_csv['TT'] == "D"]["Amount"]
        self.output_csv["Transaction Currency"] = "EGP"
        self.output_csv = self.output_csv.replace(np.nan, 0)
        self.output_csv.drop("Amount",axis='columns', inplace=True)
        self.output_csv.drop("TT",axis='columns', inplace=True)
        self.output_csv = self.output_csv[["ValueDate","Category","Debit Amount", "Credit Amount","Transaction Currency","ExtraRef"]]
        self.output_csv.columns = ["Value Date","Transaction Type","Debit Amount", "Credit Amount","Transaction Currency","Description"]
        self.output_csv['Value Date'] = self.output_csv['Value Date'].apply(lambda x: self.date_formatter(x))
        self.csvData.append(self.output_csv.columns)
        for index, row in self.output_csv.iterrows():
            self.csvData.append(row.tolist())
        # return "Adjust"
    def date_formatter(self, sDate):
        Months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        aDate = sDate.split()
        Mon = aDate[1]
        Month = Months.index(Mon) + 1
        return aDate[0] + "/" + str(Month) + "/20" + aDate[2]

    def csv_gen(self):
        csvData = []
        csvRow = []
        csvRow.append("Account Number")
        csvRow.append("Bank Key")
        csvRow.append("Currency")
        csvRow.append("Statement Date")
        csvRow.append("From Date")
        csvRow.append("To Date")
        csvData.append(csvRow)
        csvRow = []
        print(self.AccNum)
        csvRow.append("'"+str(self.AccNum)+"'")
        csvRow.append("")
        csvRow.append("EGP")
        csvRow.append("")
        csvRow.append("")
        csvRow.append("")
        csvData.append(csvRow)
        csvRow = []
        csvRow.append("Begin Balance")
        csvRow.append("End Balance")
        csvRow.append("Total Debit Amount")
        csvRow.append("Total Credit Amount")
        csvData.append(csvRow)
        csvRow = []
        csvRow.append("")
        csvRow.append("")
        csvRow.append("")
        csvRow.append("")
        csvData.append(csvRow)
        csvRow = []
        self.csvData = csvData
    
    def _writeCSV(self):
        csvData = self.csvData
        # fileName = "./template.csv"
        with open(r'{}/{}.csv'.format(self.Path,self.AccNum), 'w' , newline='') as csv_file:
            writer = csv.writer(csv_file)
            for item in csvData:
                writer.writerow(item)
    
    def save_to_csv(self):
        self.tablePD.to_csv(r'{}/modified.csv'.format(self.Path), index = False)
        