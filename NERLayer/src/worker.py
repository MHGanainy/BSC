import TEMENOS as t
import CIB as c
import os, time
import aws
# Global Variales
PARSEDDOCSPATH = "./parsedDocs"

# Global Methods
def get_subdirectories(a_dir):
    return [(a_dir+"/"+name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def get_subfiles(a_dir):
    return [name
             for root, dirs, files in os.walk(a_dir)
             for name in files]
    
def getAccountNum(RawTextPath):
    with open(RawTextPath) as f:
        lines = f.readlines()
        return lines[0]

# Main Function
if __name__ == "__main__":
    aws.clear_bucket()
    while True:
        for path in get_subdirectories(PARSEDDOCSPATH):
            if "modified.csv" not in get_subfiles(path):
                AccNum = int(getAccountNum(path+"/RawText.txt"))
                if AccNum==1000118510010201:
                    t.TEMENOS(path,AccNum)
                    print("Modified CSV Created for Path "+path)
                elif AccNum==100011856807:
                    c.CIB(path,AccNum)
                    print("Modified CSV Created for Path "+path)
        time.sleep(5)