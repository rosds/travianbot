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
USERNAME = 'Sir Bimbo'
PASSWORD = 'tr4v14n'


class Farm:
    """ This class contains the info for one farm """
    def __init__(self, string):
        """ Create am instance of a farm given a string """
        info = string.split()
        self.x = info[0]
        self.y = info[1]
        self.troops = dict([troop.split(':') for troop in info[2:]])
        self.next_attack = datetime.datetime.now()

    def can_attack(self):
        """ Determine if it is possible to attack """
        if datetime.datetime.now() > self.next_attack:
            commands.go(SERVER + 'build.php?tt=2&id=39')
            html = commands.show()
            soup = BeautifulSoup(html)
            for troop, num in self.troops.items():
                link = soup.find('a', {'onclick': re.compile('.*\.' + troop + '\..*')})
                if link and link.text > int(num):
                    continue
                else:
                    print "tropas insuficientes :("
                    return False
            return True
        else:
            print "Las tropas deben estar en camino"
            return False

    def attack(self):
        """ Attack the farm """
        print "Planeando ataque a (" + self.x + "|" + self.y + ")"
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
            h, m, s = t.split(':')
            self.next_attack = datetime.datetime.now() + \
                datetime.timedelta(seconds=int(s), minutes=int(m) + 2, hours=int(h))
            commands.fv('2', 's1', 'ok')
            print "Enviado ataque...",
            commands.submit()
            print "done"

    def __str__(self):
        """ Print the coordinate of the farm """
        return '(%d|%d)' % (self.x, self.y)


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
            farm_list.append(Farm(line))
        self.farms = farm_list
        f.close()

    def attack_farms(self):
        """ Attack all the farms """
        for farm in self.farms:
            farm.attack()

    def start(self):
        """ Starts the bot """
        self.read_farms_file()
        print "A las armaaaaaaas!!!"
        while True:
            print "al ataque!"
            self.attack_farms()
            print "me voy a dormir, regreso en 1 min... zzzz"
            time.sleep(60)


if __name__ == '__main__':
    tb = TravianBot()
    tb.login()
    tb.start()
