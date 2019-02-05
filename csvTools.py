import csv

################################################################################
# READING
################################################################################

def CSVToMatrix(filename):
    """reads a csv file and returns a list of lists where each list item is a row in the csv"""
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        
        csvmatrix = []
        for row in reader:
            csvmatrix.append(row)
        
        return csvmatrix

def CSVToDict(filename):
    """reads a csv file and returns a dictionary where the column names (the first row of the csv) are the keys, and the column values are a list corresponding to that key"""
    m = CSVToMatrix(filename)
    keys = m[0]
    mt = list(map(list, zip(*m[1:])))
    return dict(zip(m[0], mt))

################################################################################
# WRITING
################################################################################

def matrixToCSV(filename, matrix):
    """writes a csv file given a list of lists corresponding to rows of the file"""
    with open(filename, "w") as newfile:
        writer = csv.writer(newfile)
        writer.writerows(matrix)

def dictToCSV(filename, dict):
    """writes a csv file given a dictionary where the keys are column headers and the values are lists which are the column values"""
    vs = list(dict.keys())
    mt = list(dict.values())
    m = [vs] + list(map(list, zip(*mt)))
    matrixToCSV(filename, m)