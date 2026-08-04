# my.py: Transforms HTML from imgur into an array format for dbild.js
#
# Usage: python3 my.py <imgur_html_file> 
# 
# Use `nano imgur` then Alt+T to delete the files contents. Paste the HTML from imgur and save, then run this script.
# In imgur, it's easiest to press Rearange and inspect click after the last image, then copy the innerHTML of that div. (Copying the entire page HTML can include other imgur images like the pfp)
# The script checks the files on disk to find missing days. It looks in /home/gob/Pictures/dbild/<year>/Stabilized for files named yyyy-mm-dd.jpg.
# It then appends the imgur codes to dbild.js at the line /* INSERT HERE */.
#
# 2026-08-04
#
# TODO: Handle files named yyyy-mm-dd<something>.jpg, like 2026-08-05 (2).jpg. Currently this should give an error of mismatch between nr missing days and nr of images.

from os import walk
import sys

months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

# Read imgur HTML from the first command line arg as file
if len(sys.argv) < 2:
    print("Error: no imgur HTML file provided")
    print("Usage: python3 my.py <imgur_html_file>")
    exit()
with open(sys.argv[1], "r") as f:
    rawimgurhtml = f.read()

# Let user input month (1-12) and year (yyyy)
mon = input("Month: ")
year = input("Year: ")

# Parse the HTML to extract the imgur codes
imgurhtml = str(rawimgurhtml).split("i.imgur.com/") # Index will 0 contain garbage, so loop from 1 to 31
imgurhtml = [x[:7] for x in imgurhtml] # imgur codes are 7 characters long
print("Nr of days from imgur: {}".format(len(imgurhtml)-1))
print("Imgur codes: {}".format(imgurhtml[1:]))

pathtoimagedir = "/home/gob/Pictures/dbild/{}/Stabilized".format(year)
#input("Path to stabilized images: ")

# Read the directory of images to find missing days. Files should be named yyyy-mm-dd.jpg
missingdays = []
rawfiles = []
for (dirpath, dirnames, filenames) in walk(pathtoimagedir):
    rawfiles.extend(filenames)
    break
monthfiles = [x for x in rawfiles if x.startswith("{}-{}-".format(year, mon.zfill(2)))]
daynrs = [x[8:10] for x in monthfiles]
daynrs.sort()

for i in range(1, 32):
    if str(i).zfill(2) not in daynrs:
        missingdays.append(str(i))
print("Missing days: {}".format(missingdays))
print()

# Check if the number of missing days matches the number of images
if len(missingdays) != 32-len(imgurhtml):
    print("Error: number of missing days does not match number of images")
    exit()

# Pad both arrays to length 32
sortedhtml = [None]*32
for i in range(1, 32-len(imgurhtml)):
    imgurhtml.append(None)

# Open dbild.js and append at /* INSERT HERE */
lines = []
with open("./dbild.js", "r") as f:
    # Find the line with /* INSERT HERE */
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "/* INSERT HERE */" in line:
            insert_index = i

with open("./dbild.js", "w") as f:
    # Write the lines before the insert point
    for i in range(insert_index):
        f.write(lines[i])
    # Write the imgur codes to the file
    j = 0
    for i in range(1, 32):
        if str(i) not in missingdays and imgurhtml[i-j] is not None:
            sortedhtml[i] = imgurhtml[i-j]
            print('["'+str(i)+' '+months[int(mon)-1]+' '+year+'", "'+sortedhtml[i]+'"],')
            f.write('    ["'+str(i)+' '+months[int(mon)-1]+' '+year+'", "'+sortedhtml[i]+'"],\n')
        else:
            j += 1
    # Write the lines after the insert point
    f.write("\n")
    for i in range(insert_index, len(lines)):
        f.write(lines[i])
