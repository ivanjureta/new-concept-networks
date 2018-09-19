# Functions to transform strings

# Shorten input string to n characters and add ellipsis '...'.
def shorten_string(string, n):
    if len(string) < n: return string
    else: return string[0:n] + '...'

# Add line breaks to long string.
## In: String x and number of characters to add line breaks at.
## Out: String y with a line break every max_chars of x.
def add_line_breaks(x, max_chars):
    import math
    y = str()
    cc = 0
    for i in x.split(): 
        cc = cc + len(i)
        y = y + ' ' + i
        if cc > max_chars:
            cc = 0
            y = y + '\n'
    return y
