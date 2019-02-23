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

################################################################################
# USING
################################################################################

def functionFromPairs(pairs): # [(a, b)] -> a -> b
    """takes in a list of 2 item tuples [(a, b)] and returns a function which will interpolate the values of b given a as an input (where the a's are orderable), it will take the endpoint values as the value if a out of range"""
    pairs = sorted(pairs, key=lambda pair: pair[0]) # sort by a
    if pairs == []: # if invalid list
        raise ValueError("nothing to interpolate from an empty list")
    
    def interpolate(pairs, a):
        try:
            below = max([pair for pair in pairs if pair[0] < a], key=lambda pair: pair[0]) # get the point below a
        except Exception as e:
            below = None
        try:
            above = min([pair for pair in pairs if a <= pair[0]], key=lambda pair: pair[0]) # get the point above a
        except Exception as e:
            above = None
        if below == None and above != None: # under bounds
            return above[1]
        elif below != None and above == None: # over bounds
            return below[1]
        #elif below == None and above == None: # no bounds # cannot happen, checked for before making function
        else:
            return (above[1] - below[1]) / (above[0] - below[0]) * (a - below[0]) + below[1]
    
    return lambda a: interpolate(pairs, a)

def pairsFromColumns(csvdict, colA, colB):
    A = [float(a) for a in csvdict[colA]]
    B = [float(b) for b in csvdict[colB]]
    return list(zip(A, B))