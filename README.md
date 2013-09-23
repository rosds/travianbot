travianbot
==========

A simple python script for the game travian

Now the only feature of travianbot is the constant attack of the farms specified
on the farms.txt file.


requisites
----------

This script uses the twill library and BeautifulSoup library so be sure to have
that ;)


How to
------

The first thing is to ser your username and password on the variables at the
begining on the script. After that be sure to fill up the farms.txt file and
just run the script as:

'''
./travian_bot.py
'''


farms.txt format
---------------

The farm.txt format is very simple. Here is an example:

162 -17 t1:40 t2:30

the first two numbers are the coordinates of the farm and the next set of
strings denote type and number of troops. In this example means to send 40
soldiers of type one and 30 soldiers of type two.
