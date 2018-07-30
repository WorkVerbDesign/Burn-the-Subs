#!/usr/bin/python3
#
# Copyright (c) 2018 by twitch.tv/cuexxiii
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE. 

import re

class GParseQuick:
    """
    Quick and dirty GCode parser and generator
    Parses one line of GCode
    """

    def __init__(self, gcode=None):
        self.order = list()
        self.param = {}

        if gcode is not None:
            self.parse(gcode)

    def __str__(self):
        self.unparse()

    def parse(self, gcode):
        """
        Takes a GCode string and parses it into the object
        """
        self.order = list()
        self.param = {}

        for m in re.findall(r"([A-Z])([0-9.-]+)", gcode):
            try:
                if m[0] == "G":
                    self.param[m[0]] = m[1]
                else:
                    self.param[m[0]] = float(m[1])
                self.order.append(m[0])
            except:
                pass # ignore errors

    def unparse(self):
        """
        Returns the contents of this object as GCode string
        """
        return " ".join(map(lambda p: p+str(self.param[p]), self.order))

    def get(self, p):
        """
        Get one value from the GCode
        The G type is a string, all others are floats
        """
        if p in self.order:
            return self.param[p]
        else:
            raise ValueError("%s not in GCode" % p)

    def set(self, p, v):
        """
        Set one value in this GCode instruction to a specific value
        """
        if p in self.order:
            self.param[p] = v
        else:
            raise ValueError("%s not in GCode" % p)

if __name__ == "__main__":
    a = GParseQuick("G01 X0.324 Y-12.234")
    a.set("X", a.get("X") * 2)
    print(a.unparse())

    # this throws an error
    a.set("Z", 20)