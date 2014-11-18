"""

"""

import csv
from csv import DictReader, DictWriter
from operator import itemgetter

def read_print(fname):
    file = open(fname)
    rows = DictReader(file)
    for row in rows:
        print(row)
    file.close()
    
def read(fname):
    file = open(fname)
    res = []
    reader = csv.reader(file)
    for row in reader:
        res.append(row)
    file.close()
    return res

def find(fname, field, vtarget, fieldnames=None):
    if(fieldnames is None):
        fieldnames = get_fields(fname)
    
    file = open(fname)
    res = []
    rows = DictReader(file, fieldnames=fieldnames)
    for row in rows:
        row.pop(None, None)
        if row.get(field) == vtarget:
            res.append(row)
    file.close()
    
    return res
    
def find_range(fname, field, vmin, vmax, fieldnames=None, resreverse=False):
    if(fieldnames is None):
        fieldnames = get_fields(fname)
    
    file = open(fname)
    res = []
    rows = DictReader(file, fieldnames=fieldnames)
    for row in rows:
        row.pop(None, None)
        if row.get(field) <= vmax and row.get(field) >= vmin:
            res.append(row)
    file.close()
    
    return sorted(res, key=itemgetter(field), reverse=resreverse)

def get_fields(fname):
    file = open(fname)
    reader = csv.reader(file)
    fields = []
    for row in reader:
        fields = row
        break;
    file.close()
    
    return fields;

def write(fname, rows):
    file = open(fname, "w", newline='')
    writer = csv.writer(file)
    writer.writerows(rows)
    file.close()
    
def write_dict(fname, dicts, fieldnames):
    file = open(fname, "w", newline='')
    writer = DictWriter(file, fieldnames)
    writer.writeheader()
    writer.writerows(dicts);
    file.close()

# Test

def test():
    
    input_filename = "test.csv"
    
    output_filename = "test_output.csv"
    
#     dicts = find(input_filename, "Release Date", "")
#    
#     write_dict(output_filename, dicts, get_fields(input_filename))
    
    rows = [("data1", "data2", "data3", "data4", "data5", "data6", "data7", "data8", "data9", "data10")]
    
    for i in range(0, 10000):
        rows.append([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
    write("scale_output4.csv", rows)
    print("fin")

if __name__ == "__main__":
    test()
