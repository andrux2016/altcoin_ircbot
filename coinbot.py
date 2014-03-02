# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 16:07:07 2014

@author: f1ndm3h

TO DO SHIT:

- Add game support ?

- ADD  !tiproulette 

- Ghost itself when running the bot!

"""

import socket
import string
import time
import re
import json
import urllib2
from xml.dom import minidom
import random
import jsonrpclib
import thread
import operator
from threading import Timer, Lock

# create a mutex-lock
lockbuffer = Lock()
readbuffer = ""

BILLION=1000000000
MILLION=1000000

HOST="irc.freenode.net"
PORT=6667
NICK="ZeitAssistBot"
IDENT="ZeitAssistBot"
REALNAME="ZeitAssistBot"
readbuffer=""
BOTCHANNEL="#zeitcoin"
PASS="cnapbot@123"

# keep updating this dictionary of prices
currPrices = {'coinex' : -1, 'cryptorush' : -1, 'cryptsy' : -1}

block_reward = [250000, 1000000]

DONATEADDR="MZZCShGh3iBA1o29nxfufiQHhG3wjexGhG"

giftlist = [ "gives 2 symmetric boobs to ",
             "gives a hug to ",
             "gives a lucky ZeitCoin to ",
             "gives 0.00000000 BTC to ",
             "throws some crypto poops to ",
             "throws an orphan ZeitBlock at ",
             "offers a lucky ZeitCoin to ",]

poollist = ["- https://zeit.yourmine.org/",
            "- http://www.megapools.org/",
            "- http://zeit.hashstrike.com/",
            "- http://zeit.morecoins.org/",
            "- https://minercrew.org/zeit/",
            "- http://zeit.dedicatedpool.com",
            "- http://zeit.coins4everyone.com",
            "- http://zeit.hashfever.com",
            "- http://zeit.hashrate.eu",
            "- http://www.xhash.net",
            "- http://zeit.okaypool.com/ ",
            "- http://115.28.133.246/zeit ",
            "- http://liwu.com:88/zeit/",
            "- http://zeit.crewdoginvesting.com",
            "- https://zeit.mineoncloud.com",
            "- http://zeitcoin.kaysid.com/",
            "- http://zeit.pool.mn/",
            "- http://zeit.mha.sh/",
            "- http://zeit.hashfaster.com",
            "- https://zeit.hash.so/",
            "- https://zeit.imine.at",]
            
faucetlist = ["- http://earncryptocoins.com/zeitcoin",
              ]
            
nodelist = ["54.213.62.154",
"54.213.81.163",
"54.213.195.38",
"54.213.243.144",
"54.213.174.35",
"198.101.12.57",
"192.3.178.234",
"162.220.26.146",]

"""
    NA VALO FLOOD PROTECTION.. px an ekanes !pools min ksana kanei meta apo 10 sec! 
"""

"""
    The answer is in the form ACC :
    
     0 - account or user does not exist
     1 - account exists but user is not logged in
     2 - user is not logged in but recognized (see ACCESS)
     3 - user is logged in
"""
def checkIfIdented(s, who):
    s.send("PRIVMSG NICKSERV" + " :ACC " + who + "\r\n")
    

    try:    
        lockbuffer.acquire()
        #global readbuffer 
        #readbuffer = readbuffer + s.recv(1024)
        global readbuffer
        tmp = string.split(readbuffer, "\n")
        
        lockbuffer.release()        
        
        
        for line in tmp:
            line = string.rstrip(line)
            line = string.split(line)
            for ind, elem in enumerate(line):
                print "psaxno..."
                if elem in ("ACC"):
                    print line[ind+1]
                    if line[ind+1] == "3":
                        return True
                    else:
                        return False
    except:
        print "Something went wrong when fetching users list @ " + BOTCHANNEL

def priceUpdater():
    
    currPrices['coinex'] = displayPrice('ZEIT', 1, 'coinex')
    currPrices['cryptorush'] = fetchPrice('cryptorush')
    # update prices in 2 mins again
    Timer(120, priceUpdater, ()).start()
        
    # print "mpika stin price updater!"
    # print currPrices

def randomTIP(where, s):

    # throw a random tip every so
    timeInt = random.randint(300, 700)
    
    try:
        userlist = fetchUserList(s)
        target = random.choice(userlist)
        if target[0] in ('@', '+'):
            target = target[1:]
            
        rcoins = random.randint(50, 100)
        s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION would love to randomly tip someone..\x01\r\n")
        time.sleep(0.5)
        s.send("PRIVMSG " + where + " :!tip " + target + " " + str(rcoins) + " well\r\n")

        Timer(timeInt, randomTIP, (where, s)).start()
    except:
        print "Something went wrong while trying to random tip someone !!"
        Timer(timeInt, randomTIP, (where, s)).start()

def fetchUserList(s):
    
    rd = ""    
    
    try:
        
        s.send("NAMES " + BOTCHANNEL + "\r\n")
        
        rd = rd + s.recv(1024)
        print rd
        tmp = string.split(rd, "\n")
        
        rd = tmp.pop()
        print rd            
        
        for line in tmp:
            line = string.rstrip(line)
            line = string.split(line)
#                print "-----****----"
#                print line
#                print "-----****----"                
            if line[1].find("353") != -1:
                # every following item is a user !
                print line[6:]
                return line[6:]
                
    except:
        print "Something went wrong when fetching users list @ " + BOTCHANNEL

def tellPM(s, where, who, msg):
    s.send("PRIVMSG " + where + " :" + who + ": " + msg + "\r\n")
    
def displayPools(s, where, who):
    
    if not poollist:
        s.send("PRIVMSG " + who + " :Sorry but there are no available pools yet :(:\r\n")
    
    else:    

        # check if user pmed the bot or not
        if who != where:
            # then avoid spamming the main channel and 
            # send them in a pm the available pool
            # s.send("PRIVMSG " + where + " :" + who + ": I have sent you a PM with the available pools :)\r\n")
            msg = "I have sent you a PM with the available pools :)"
            try:
                thread.start_new_thread(tellPM, (s, where, who, msg))
                where = who
            except:
                return

        s.send("PRIVMSG " + who + " :Currently I am aware about these pools:\r\n")
        for pool in poollist:
            # sleep a bit to avoid flooding
            time.sleep(0.5)
            s.send("PRIVMSG " + who + " :" + pool + "\r\n")
    
        # TO DO: Fetch pools list from XML


def displayCoinInfo():

    try:
        rpcserver = jsonrpclib.Server("http://Zeit:Zeitgeist@127.0.0.1:44843")
        data = rpcserver.getmininginfo()
        out = ""

        # get this
        blocknum = data['blocks']
        out += "Last Block: #" + str(blocknum) + " -"
        diff = str(data['difficulty'])
        out += " Current difficulty: " + diff[:5] + " -"

        nrate = float(data['networkhashps'])
        # if 1ghs or more
        if len(str(nrate)) >= 10:
            unit = " GH/s"
            nrate = str(nrate / BILLION)
            # print "edo: " + nrate
        else:
            unit = " MH/s"
            nrate = str(nrate / MILLION)

        # print nrate
        
        out += " Network's HashRate: " + nrate[:5] + unit
        # print out
        return out, data['difficulty'], nrate[:5]

    except:
        out = "Something went wrong. Please try again later and report to cnap"
        return out
        
    
def displaySpecs(s, where, who): 
    
    output = """ZeitCoin's Specifications:\n
    - SCRYPT PoW algorithm\n
    - 30 seconds block target\n
    - 250000 - 1000000 coins per block initially\n
    - Payout will be halved every week for the first 6 weeks\n
    - After 6 weeks, the payout will be fixed at 1 coin per block\n
    - Difficulty retargets every block (Avoids the need for KGW)\n
    - Interest on Proof of Stake:\n
        - Year 1: 25%\n
        - Year 2: 20%\n
        - Year 3: 15%\n
        - Year 4 and ongoing years: 5%\n
        - Total coins 99 billion\n
    - 4 confirmations per transaction means fast 2 mins confirmations\n
    - 50 confirmations per ZEIT blocks\n
    """
    
    # check if user pmed the bot or not
    if who != where:    
        # then avoid spamming the main channel and 
        # send them in a pm the available pool
        # s.send("PRIVMSG " + where + " :" + who + ": I have sent you a PM with ZeitCoin's specifications:)\r\n")
        msg = "I have sent you a PM with ZeitCoin's specifications:)"
        try:
            thread.start_new_thread(tellPM, (s, where, who, msg))
            where = who
        except:
            return
            

    for line in output.split("\n")[:-2]:
        # sleep a bit to avoid flooding
        time.sleep(0.5)
        s.send("PRIVMSG " + where + " :" + line + "\r\n")                

    
def displayPrice(coin, mid, market='cryptsy'):
    
    if market == 'cryptsy':
        try:
            url = "http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=" + mid
            json_data = json.load(urllib2.urlopen(url))
        
            data = json_data['return']['markets'][coin] # ['lasttradeprice']
            # print "this is data: " + data
            info = data['primarycode'] + "/" + data['secondarycode'] + ": "
            info += "Last " + coin + " price: " + data['lasttradeprice']
            info += " (@ " + data['lasttradetime'] + " )"
        
            return info
        except:
            return -1
    if market == 'coinex':
        
        try:

            url = "https://coinex.pw/api/v2/trade_pairs"
            # change the user agent to Mozilla to avoid a possible 403 forbidden error
            agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : agent }
            req = urllib2.Request(url, None, headers)
            
            json_data = json.load(urllib2.urlopen(req))
            data = json_data['trade_pairs']
            newdata = sorted(data, key=operator.itemgetter('id'))
            #data = json_data['trades'] 
            # print data
            #time.sleep(5)   
            # normally ZEITs id is 89
            # something is fucked up and counts i-1
            price = newdata[88]['last_price']
            # print "Price is: " + str(price)
            return "%.8f" % (price * ( 10 ** -8 ))
            
            # print data2['last_price']

            # print data
                    
            # return info
        except:
            return -1


        

def fetchPrice(market='cryptorush'):

    try:
        if market == 'cryptorush':
            url = "https://cryptorush.in/index.php?p=trading&m=ZEIT&b=BTC"
            # change the user agent to Mozilla to avoid a possible 403 forbidden error
            agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : agent }
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)
            html = response.read()
            
            # do the appropriate stuff here
            # in order to grab the price of your interest
            pos1 = html.find("ZEIT / BTC")
            new_html = html[pos1:]
            pos2 = new_html.find("</b>")
            
            x = re.search("\d[.]\d{8,10}", html[pos1:pos1+pos2])
    
            if x:
                return x.group(0)
            else:
                return -1
                
        elif market == 'coinex':
            url = "https://coinex.pw/trade/zeit_btc"
            
            url = "https://coinex.pw/api/v2/currencies"
            
            # change the user agent to Mozilla to avoid a possible 403 forbidden error
            agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : agent }
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)
            html = response.read()
            
            print html
            
            # do the appropriate stuff here
            # in order to grab the price of your interest
            pos1 = html.find("metamorph-172-start")
            new_html = html[pos1:]
            pos2 = new_html.find("metamorph-172-end")
            
            print html[pos1:pos1+pos2]
            # print "Ftaneis edo kale?"
            x = re.search("\d[.]\d{8,10}", html[pos1:pos1+pos2])
            
            print x.group(0)
            
            if x:
                return x.group(0)
            else:
                return -1            
        
    except:
        return -1


def botCommands(s, cmd, xmldoc, who, where, args):

    coinlist = xmldoc.getElementsByTagName('coin')
    print args
    cmd = cmd.lower()
    
    # this means if bot received a PM
    if where == NICK:
        # then pm that guy back
        where = who
    
    #if cmd == "!logo":
    #    s.send("PRIVMSG " + where + " :Logo coming soon..\r\n")
    
    if cmd in ("!safety", "!warning"):
        msg = "Please make sure to register your nickname and always identify yourself.\
 Here's a guide: http://www.wikihow.com/Register-a-User-Name-on-Freenode . \
 We need you to do this in order to reassure that your zeitcoins balance is safe from scams."
 
        s.send("PRIVMSG " + where + " :" + msg + "\r\n")
        
    elif cmd == "!debug":
        print checkIfIdented(s, "cnap")
        
    elif cmd == "!faq-pos":
        msg = "PoS [Proof of Stake] starts after you have held an amount of coins for 20+ days.\
 For 1st year your coins will be increased by 25% (it will be shown as an incoming transaction) \
 every time that a specific amount of coins is held in your wallet for 20+ days.\
 After that every years stake gets decreased by 5% but still ZeitCoins POS is the highest interest at the moment."
         
        s.send("PRIVMSG " + where + " :" + msg + "\r\n")
        
    elif cmd == "!credits":
        s.send("PRIVMSG " + where + " :This bot was coded by cnap. You can always buy him a beer: " + DONATEADDR + " [ZEIT]\r\n")

    elif cmd == "!roll":
        s.send("PRIVMSG " + where + " :You rolled: " + str(random.randint(1, 100)) + "\r\n")

    elif cmd == "!fly":
        s.send("PRIVMSG " + where + " :Gimme some hash and I'll teach you how to FLY\r\n")
    
    elif cmd in ("!hashrate", "!hash", "!khash"):
        
        if not args:
            s.send("PRIVMSG " + where + " :" + who + ": You didn't tell me your mining speed :( [Usage: !khash 100]\r\n")
            
        if cmd == "!khash":    
            ukhash = int(args[0]) * 1000
        else:
            ukhash = int(args[0])
        # block_reward / diff 
        out, diff, nrate = displayCoinInfo()
        
        lowlim = str(block_reward[0] / ((diff*(pow(2, 32) / ukhash) / 3600 / 24)))
        upperlim = str(block_reward[1] / ((diff*(pow(2, 32) / ukhash) / 3600 / 24)))
        
        s.send("PRIVMSG " + where + " :" + who + ": You will mine approximately from " + lowlim + " to " + upperlim + " ZEITs per day!\r\n")
    #elif cmd == "!slaproulette":
        
    #    userlist = fetchUserList(s)
        # print userlist
    #    target = random.choice(userlist)
        
    #    s.send("PRIVMSG " + where + " :" + NICK + " will now pick a random guy to slap.. Hmmm who shall it be?\r\n")
    #    time.sleep(2)
    #    s.send("PRIVMSG " + where + " :Target found!\r\n")
    #    s.send("PRIVMSG " + where + " :\x01ACTION slaps " + target + " around a bit with a large trout\x01\r\n")

    elif cmd == "!tiproulette":
        
        userlist = fetchUserList(s)
        target = random.choice(userlist)
        
        s.send("PRIVMSG " + where + " :" + NICK + " will randomly pick a winner!\r\n")

        for i in range(1,4):
            s.send("PRIVMSG " + where + " :" + str(4-i) + "\r\n")
            time.sleep(1)
            
        s.send("PRIVMSG " + where + " :Aaaand.. " + target + " is the winner!\r\n")
    
    
    elif cmd in ("!specs", "!specifications"):
        displaySpecs(s, where, who)

    elif cmd == "!gift":
        
        n = random.randint(0, len(giftlist)-1)
        s.send("PRIVMSG " + where + " :\x01ACTION " + giftlist[n] + who + "\x01\r\n")
    # add http://explorer.lemoncoin.org:2075/chain/LemonCoin to links or !explorer ???
    elif cmd in ("!conf", "!configuration"):
        s.send("PRIVMSG " + where + " :Basic conf file: http://pastebin.com/0Hh0wPYE\r\n")

    #elif cmd in ("!giveaway", "!giveaways"):
    #    s.send("PRIVMSG " + where + " :To enter the 50k ZeitCoins giveaway simply like https://www.facebook.com/Zeitcoin and follow https://twitter.com/Zeitcoin :) Then please kindly pm Zeitcoin to let him know add you in the giveaway list! \r\n")

    elif cmd in ("!site", "!website"):
        s.send("PRIVMSG " + where + " :Official webpage: http://www.zeit-coin.com/\r\n")
        s.send("PRIVMSG " + where + " :Official online wallet page: https://www.zeit-wallet.com\r\n")

    elif cmd == "!faucet" or cmd == "!faucets":
        
        if not faucetlist:
            s.send("PRIVMSG " + where + " :Sorry there are no faucets yet :(\r\n")    
        for f in faucetlist:
            # s.send("PRIVMSG " + where + " :- http://earncryptocoins.com/lmc\r\n")
            s.send("PRIVMSG " + where + " :" + f + "\r\n")
    #elif cmd == "!donate":
    #    s.send("PRIVMSG " + where + " :Consider Donating some LMC @ LMTHvdesdCPhSgToQLAEyC1tK85TQUWUBE for promotion purposes! (address @ official thread)\r\n")

    elif cmd == "!downloads" or cmd == "!download":
        # https://github.com/macrocoin/macrocoin
        # s.send("PRIVMSG " + where + " :https://mega.co.nz/#!J5YynKiB!dfHiidARiRkcaS9o869T8EKFcb5zuUi4gnKLMdCox_k\r\n")
        # return
        s.send("PRIVMSG " + where + " :Source code: https://github.com/zeitcoin/zeitcoin\r\n")
        s.send("PRIVMSG " + where + " :Windows Wallet: http://zeit-coin.com/Zeitcoin-qt.rar\r\n")
        s.send("PRIVMSG " + where + " :MAC Wallet: http://zeit-coin.com/ZeitcoinMACQT.dmg\r\n")
        

    #elif cmd == "!games" or cmd == "!game":
    #    s.send("PRIVMSG " + where + " :BombSweeper: http://bombsweeper.com/\r\n")

    elif cmd == "!exchange" or cmd == "!trade":
        s.send("PRIVMSG " + where + " :Currently you may buy/sell ZEIT at: \r\n")
        s.send("PRIVMSG " + where + " :https://cryptorush.in/index.php?p=trading&m=ZEIT&b=BTC | https://coinex.pw/trade/zeit_btc | https://www.bittrex.com/Market/Index?MarketName=BTC-ZEIT\r\n")
        return
        #s.send("PRIVMSG " + where + " :- https://pmtocoins.com: \r\n")
        #s.send("PRIVMSG " + where + " :- https://www.newaltex.com/exchange: \r\n")
        # s.send("PRIVMSG " + where + " :\r\n")
    elif cmd in ("!info", "!diff", "!hashrate"):
        # get the ouput string from displayCoinInfo
        s.send("PRIVMSG " + where + " :" + displayCoinInfo()[0] + "\r\n")

    elif cmd in ("!pools", "!pool"):
        displayPools(s, where, who)

    elif cmd in ("!nodes", "!node"):
        _str = ""
        for i in nodelist:
            _str += i + ", "
        # display all except the last ","
        s.send("PRIVMSG " + where + " :" + _str[:-2] + "\r\n")    

    elif cmd in ("!price", "!market", "!value"):
        #s.send("PRIVMSG " + where + " :No prices available yet :(\r\n")        
        #return
        #pr1 = fetchPrice('coinex')
        s.send("PRIVMSG " + where + " :Prices are updated every ~2 minutes:\r\n")        
        
        if currPrices['coinex'] != -1:
            s.send("PRIVMSG " + where + " :ZEIT/BTC last price at https://coinex.pw/: " + str(currPrices['coinex']) + "\r\n")
            found = 1
        else:
            pr1 = displayPrice('ZEIT', 1, 'coinex')
            if pr1 != -1:
                s.send("PRIVMSG " + where + " :ZEIT/BTC last price at https://coinex.pw/: " + str(pr1) + "\r\n")
                # update the cache
                currPrices['coinex'] = pr1
                found = 1
                
        if currPrices['cryptorush'] != -1:
            s.send("PRIVMSG " + where + " :ZEIT/BTC last price at https://cryptorush.in: " + str(currPrices['cryptorush']) + "\r\n")
            found = 1
        else:
            pr2 = fetchPrice('cryptorush')
            if pr2 != -1:
                s.send("PRIVMSG " + where + " :ZEIT/BTC last price at https://cryptorush.in: " + str(pr2) + "\r\n")
                # update the cache
                currPrices['cryptorush'] = pr2
                found = 1
                
        if found == 0:
            s.send("PRIVMSG " + where + " :I was unable to find ZEIT current price :(. Try again later please.\r\n")

    elif cmd == "!help":
        # !game(s),
        # msg = "!info, !price, !exchange, !pool(s), !nodes, !conf, !download(s), !faucet(s), !site, !roll, !fly, !credits"
        msg = "!info, !exchange, !pool(s), !nodes, !conf, !download(s), !faucet(s), !site, !roll, !tiproulette, !slaproulette, !fly, !credits"
        s.send("PRIVMSG " + where + " :Available commands: " + msg + "\r\n")

# [':cnap!~quassel@178.128.39.37.dsl.dyn.forthnet.gr', 'JOIN', '#zeitcoin']

def ifJoinedChannel(s, who, where):

    msg = "Welcome to the official #zeitcoin channel.\
 Please make sure to register your nickname and always identify yourself.\
 Here's a guide: http://www.wikihow.com/Register-a-User-Name-on-Freenode .\
 We need you to do this in order to reassure that your zeitcoins balance\
 is safe from scams. (oh and yeah check our our tips CryptoRobot!)\
 Lastly, if you need any assistance feel free to pm any channel operator."
   
    s.send("PRIVMSG " + who + " :" + msg + "\r\n")

    return
    
    
def checkIfSlapped(line):
    
    # check if someone slapped the bot and slap them back
    b1 = 0
    b2 = 0
    
    for item in line:
        # item = "slaps"
        if "slap" in item:
            b1 = 1
        # if someone slaps the bot 
        if NICK in item and b1 == 1:
            b2 = 1
            
    if b2: return True
    else: return False

def findWho(strn):

    # print "Tha vro name sto: " + strn
    p = re.compile(':(.*)!')
    result = p.match(strn)
    
    if result:
        return result.group(1)

def checkForOwner(who, s):
    # 2% probability to hug
    # or check if I enter channel then -> hug
    random.seed()
    if (random.randint(1, 1000) <= 5) and (who == "cnap" or who == "cnap_"):
        s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION hugs " + who + "\x01\r\n")    

def randItem(who, s):
    n = random.randint(1, 1000)
    if who == NICK:
        who = "itself"
    #if (n <= 5):
    #    s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION throws an orphan ZeitBlock at " + who + "\x01\r\n") 
    #elif (n > 5 and n < 10):
    #    s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION offers a lucky ZeitCoin to " + who + "\x01\r\n")
    if n <= 12:
        s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION " + random.choice(giftlist) + who + "\x01\r\n")


def main():
    
    # readbuffer = ""
    s = socket.socket( )
    s.connect((HOST, PORT))
    
    # fetch and cache the current prices !
    priceUpdater()
    
    time.sleep(1)

    s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
    s.send("NICK %s\r\n" % NICK)
    s.send("PRIVMSG NICKSERV :IDENTIFY %s\r\n" %(PASS))

    # get my voice !
    s.send("PRIVMSG CHANSERV :VOICE " + BOTCHANNEL + " " + NICK + "\r\n")
    # chanserv voice #lemoncoin LemonBot
    # read the coins database
    xmldoc = minidom.parse('coins.xml')    
    
    time.sleep(1) # maybe check when connected sring and then join channel ?
    # s.send("MODE " + NICK + " +B\r\n")
    s.send("JOIN " + BOTCHANNEL + "\r\n") #Join a channel    
    # time.sleep(15)
    # Timer(10, checkIfIdented, (s, "cnap")).start()
    
    # begin random tipping !
    Timer(100, randomTIP, (BOTCHANNEL, s)).start()
    
    while 1:
        
        lockbuffer.acquire()
        global readbuffer 
        readbuffer = readbuffer + s.recv(1024)
        lockbuffer.release()
        
        temp = string.split(readbuffer, "\n")
        # throw away the last element which is the ''
        readbuffer = temp.pop()
        
        for line in temp:
            line = string.rstrip(line)
            line = string.split(line)
            print "*************** MAIN NEW LINE ***************"
            print line
            print "*************** MAIN NEW LINE ***************"
            
            if line[0].find("PING") != -1: # if the server pings us then we've got to respond!
                s.send("PONG :Pong\r\n")
                continue

            try:
                who = findWho(line[0]) # find who said that
                where = line[2] # find if this was a pm or channel msg
            except:
                print "Ooops not enough list args!"
            # check if owner talked and hug with with 10% probability
            checkForOwner(findWho(line[0]), s)
            
            cmd = ""

            # if someone just joined call the proper function
            # so that bot can send him a pm (safety issues)
            if line[1].find("JOIN") != -1:
                # bot doesnt have to pm itself!                
                if who != NICK and where == BOTCHANNEL:
                    ifJoinedChannel(s, who, where)
            
            if line[1].find("PRIVMSG") != -1:
                who = findWho(line[0]) # find who said that
                where = line[2] # find if this was a pm or channel msg
                             
                randItem(who, s)
                cnt = 0
                for iter in line:
                    cnt = cnt + 1
                    matchCmd = re.match( ':!', iter )
                    if matchCmd:
                        cmd += iter.replace(":", "") + " "
                        try:
                            #thread.start_new_thread(botCommands, (s, cmd.replace(" ", ""), xmldoc, who, where))
                            botCommands(s, cmd.replace(" ", ""), xmldoc, who, where, line[cnt:])
                            # print cmd
                        except:
                            print "Something bad happened while trying to spawn botCommands thread!"
                    else:
                        continue

                if checkIfSlapped(line) and (line[3].find("!slaproulette") == -1):
                    slappedBy = findWho(line[0]) # find who slapped me
                    s.send("PRIVMSG " + BOTCHANNEL + " :\x01ACTION slaps " + slappedBy + " back around a bit with a large trout\x01\r\n")

if __name__ == "__main__":
    main()
