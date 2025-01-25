import ujson
import uio
import os
from machine import RTC
import random
import time

# wait for the next second to generate the next sequence
# without the wait the sequence will be generated too fast
# and the sequence will be the same file over and over again
waitinseconds = 1.33

class autosequencer:
    def __init__(self, filedir):
        self.dir = filedir
        self.fnames = []
        self.sequence = []
        self.rtc = RTC()
        d = os.listdir(filedir)
        for e in d:
            filename = self.dir+e
            with uio.open(filename, "r") as f:
                json_data = ujson.load(f)
                f.close()
                end = len(json_data)
                self.fnames.append([json_data[0]['Ref'],json_data[end-1]['Ref'],e])
    
    @property
    def files(self):
        return self.fnames

    # get all possible next files
    # filetuple = [start, end, filename]
    def getpossibilities(self, filetuple):
        possibilities = []
        for f in self.fnames:
            if f[0] == filetuple[1]:
                possibilities.append(f)
            #if f[0]+1 == filetuple[1]:
            #    possibilities.append(f)
            #if f[0]-1 == filetuple[1]:
            #    possibilities.append(f)
        return possibilities
    
    # generate a sequence of files to play based on RTC seconds
    # returns a list of filenames to play in sequence
    def generateSequence(self):
        prev = ""
        self.sequence.clear()
        # rtc.datetime = [year, month, day, weekday, hours, minutes, seconds, subseconds]
        possibilities = self.getpossibilities(self.fnames[self.rtc.datetime()[6] % len(self.fnames)])
        #possibilities = self.getpossibilities(random.choice(self.fnames))
        while True:
            if len(possibilities) > 0:
                p = random.choice(possibilities)
                if p[2] == prev:
                    break
                #print(p)
                if len(p) <= 0:
                    break
                else:
                    self.sequence.append(p[2])
                    prev = p[2]
                    possibilities = self.getpossibilities(p)
            else:
                break
        if len(self.sequence) <= 1:
            time.sleep(1)
            self.generateSequence()
        return self.sequence

def main():
    a = autosequencer("sequences/")
    print(a.generateSequence())

if __name__ == "__main__":
    main()