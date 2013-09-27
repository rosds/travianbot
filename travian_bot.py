#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    2013-09-22
    travianbot v0.1
    Alfonso Ros
"""

import os
import re
import time
import datetime

from twill import commands, set_output
from BeautifulSoup import BeautifulSoup

from collections import defaultdict


SERVER = 'http://ts4.travian.net/'
USERNAME = ''
PASSWORD = ''


class Farm:
    """ This class contains the info for one farm """
    def __init__(self, string):
        """ Create am instance of a farm given a string """
        info = string.split()
        self.x = info[0]
        self.y = info[1]
        self.troops = dict([troop.split(':') for troop in info[2:]])
        self.next_attack = datetime.datetime.now()

    def get_id(self):
        """ return the coordinates of the farm as a id string """
        return self.x + "|" + self.y

    def attacking(self):
        """ Returns true if the farm is being attacked """
        if datetime.datetime.now() > self.next_attack:
            return False
        else:
            return True

    def can_attack(self):
        """ Determine if it is possible to attack """
        if not self.attacking():
            commands.go(SERVER + 'build.php?tt=2&id=39')
            html = commands.show()
            soup = BeautifulSoup(html)
            for troop, num in self.troops.items():
                link = soup.find('a', {'onclick': re.compile('.*\.' + troop + '\..*')})
                if not link or int(link.text) < int(num):
                    print "Not enought troops to attack"
                    return False
            return True
        else:
            print "This farm is being attacked"
            return False

    def attack(self):
        """ Attack the farm """
        print "Attack (" + self.x + "|" + self.y + "): ",
        if self.can_attack():
            commands.go(SERVER + 'build.php?tt=2&id=39')
            commands.fv('2', 'x', self.x)
            commands.fv('2', 'y', self.y)
            commands.fv('2', 'c', '4')
            for troop, num in self.troops.items():
                commands.fv('2', troop, num)
            commands.submit()
            commands.reload()
            html = commands.show()
            soup = BeautifulSoup(html)
            t = soup.find('div', {'class': 'in'}).text
            t = re.search('[0-9][0-9]?:[0-9]{2}:[0-9]{2}', t).group(0)
            h, m, s = [2 * int(e) for e in t.split(':')]
            wait = datetime.timedelta(seconds=s, minutes=m, hours=h)
            self.next_attack = datetime.datetime.now() + wait
            commands.fv('2', 's1', 'ok')
            commands.submit()
            print "done"

    def __repr__(self):
        """ Print the coordinate of the farm """
        return '(' + self.get_id() + ')'


class TravianBot:
    """ This class contains the travian session information """
    def __init__(self):
        self.username = USERNAME
        self.password = PASSWORD
        self.resourses = defaultdict(int)
        self.fields = defaultdict(list)
        self.farms = []

        # suppress twill output
        f = open(os.devnull, "w")
        set_output(f)

    def login(self):
        """ Init session in travian """
        commands.go(SERVER + 'login.php')
        commands.fv('2', 'name', self.username)
        commands.fv('2', 'password', self.password)
        commands.submit()

    def logout(self):
        """ Exit session """
        commands.go(SERVER + 'logout.php')

    def get_resourses(self):
        """ Parse resourses """
        commands.go(SERVER + 'dorf1.php')
        html = commands.show()
        soup = BeautifulSoup(html)
        self.resourses['wood'] = int(soup.find('span', {'id': 'l1'}).text)
        self.resourses['clay'] = int(soup.find('span', {'id': 'l2'}).text)
        self.resourses['iron'] = int(soup.find('span', {'id': 'l3'}).text)
        self.resourses['cereal'] = int(soup.find('span', {'id': 'l4'}).text)

    def get_fields(self):
        """ Get lvl of production fields """
        commands.go(SERVER + 'dorf1.php')
        html = commands.show()
        soup = BeautifulSoup(html)
        self.fields['wood'] = [int(f.text) for f in soup.findAll('div', {'class': re.compile('.*gid1.*')})]
        self.fields['clay'] = [int(f.text) for f in soup.findAll('div', {'class': re.compile('.*gid2.*')})]
        self.fields['iron'] = [int(f.text) for f in soup.findAll('div', {'class': re.compile('.*gid3.*')})]
        self.fields['cereal'] = [int(f.text) for f in soup.findAll('div', {'class': re.compile('.*gid4.*')})]

    def get_building_cost(self, id):
        """ Read the cost for expanding building """
        commands.go(SERVER + 'build.php?id=' + str(id))
        html = commands.show()
        soup = BeautifulSoup(html)
        cost = {}
        cost['wood'] = int(soup.find('span', {'class': re.compile('.*r1.*')}).text)
        cost['clay'] = int(soup.find('span', {'class': re.compile('.*r2.*')}).text)
        cost['iron'] = int(soup.find('span', {'class': re.compile('.*r3.*')}).text)
        cost['cerial'] = int(soup.find('span', {'class': re.compile('.*r4.*')}).text)
        cost['space'] = int(soup.find('span', {'class': re.compile('.*r5.*')}).text)
        return cost

    def read_farms_file(self):
        """ Read farms.txt for information about the farms """
        f = open("farms.txt")
        farm_list = []
        for line in f.readlines():
            if line[0] == '#':
                continue
            farm_list.append(self.update_farm(Farm(line)))
        self.farms = farm_list
        f.close()

    def update_farm(self, farm):
        """ Update the farm list """
        for f in self.farms:
            if farm.get_id() == f.get_id():
                farm.next_attack = f.next_attack
                return farm
        return farm

    def attack_farms(self):
        """ Attack all the farms """
        for farm in self.farms:
            farm.attack()

    def start(self):
        """ Starts the bot """
        print "Travianbot v0.1"
        while True:
            self.read_farms_file()
            self.attack_farms()
            print "waiting 5 min"
            time.sleep(300)
            self.login()


if __name__ == '__main__':
    tb = TravianBot()
    tb.login()
    tb.start()
