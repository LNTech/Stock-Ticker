#!/usr/bin/env python
import requests, json, sched, time
from os import name, system
# CLI Colors
from colorama import init, Fore, Style


# Each company from the loaded .txt file will have its own object, which has the variables name, currentPrice, lastPrice and closePrice
class Stock(object):
    def __init__(self, name, currentPrice, lastPrice, closePrice):
        self.name           = name
        self.currentPrice   = currentPrice
        self.lastPrice      = lastPrice
        self.closePrice     = closePrice


    # Sends a request off to yahoo finance with the objects name in order to get the price values
    def setPrices(self):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self.name}"
        r = json.loads(requests.get(url, headers=headers).text)['chart']['result'][0]['meta']

        self.lastPrice      = self.currentPrice # This doesn't work exactly how I want it to right now, but before setting currentPrice to the new value, we set lastPrice to the old value.
        self.currentPrice   = round(r['regularMarketPrice'], 2)
        self.closePrice     = round(r['previousClose'], 2)


    # Just for debugging purposes, needed to make sure the setPrices function worked at intended.
    def getPrice(self):
        print(self.currentPrice)


    # Function to print all information about the stock, needs tidying up in the future.
    def outputInfo(self):
        if self.currentPrice == self.lastPrice:
            return f"{self.name} \tCurrent Price: {self.currentPrice}             \tLast Price: {self.lastPrice}\tClose Price: {self.closePrice}"
        elif self.currentPrice > self.lastPrice:
            return f"{self.name} \tCurrent Price: {self.currentPrice} {Fore.GREEN}({round(self.currentPrice - self.lastPrice, 2)} change){Style.RESET_ALL} \tLast Price: {self.lastPrice} \tClose Price: {self.closePrice}"
        elif self.currentPrice < self.lastPrice:
            return f"{self.name} \tCurrent Price: {self.currentPrice} {Fore.RED}({round(self.currentPrice - self.lastPrice, 2)} loss){Style.RESET_ALL} \tLast Price: {self.lastPrice} \tClose Price: {self.closePrice}"


# Run this function before doing anything else as it iterates over the stock list and adds the values to the stockDict, as well as initializes the objects.
def initializeStocks():
    for stock in stockList:
        stockDict[stock] = Stock(stock, 0, 0, 0) # initialize stock with default values (0)
        stockDict[stock].setPrices()


# A clear function which clears the stdout
def clear():
    if name == 'nt': system('cls')
    else: system('clear')


# Starts an infinite loop, which iterates over the stock dictionary and runs the setPrices function, then outputs the information of all stocks.
def startTicker():
    while True:
        result = ""
        for stock in stockDict:
            stockDict[stock].setPrices()
            result += f"{stockDict[stock].outputInfo()}\n"
        clear()
        print(result)
        checkClosed()


# Very similar to getMarketHours function except it checks to make sure the market is open or closed.
def checkClosed():
    try:
        r = json.loads(requests.get("https://finance.yahoo.com/_finance_doubledown/api/resource/finance.market-time", headers=headers).text)
        if "U.S. markets close" in r['message']:
            print(r['message'])
        else: # Most likely means the market is closed... so end the script.
            print("Market is currently closed... Exiting script.")
            exit()
    except json.decoder.JSONDecodeError:
        checkClosed() # Try again, if request fails and no json is returned


# Gets market hours, differs from the checkClosed function as it does not exit the script if markets are closed.
def getMarketHours():
    try:
        r = json.loads(requests.get("https://finance.yahoo.com/_finance_doubledown/api/resource/finance.market-time", headers=headers).text)
        if "U.S. markets close" not in r['message']: # Check to see if market is already opened...
            print(r['message'])
            duration = r['duration'][0]
            timeLeft = (int(duration['hrs']) * 60) + int(duration['mins']) * 60 # Convert hours + minutes to seconds
        else:
            timeLeft = 0
        return timeLeft
    except json.decoder.JSONDecodeError:
        getMarketHours() # Try again


# Input stock symbols from txt file
def inputStocks():
    with open('stocks.txt') as f: stocks = [line.rstrip() for line in f]
    return stocks


# Main function that holds all of the function calls
def main():
    initializeStocks() # Create stock objects
    clear()
    scheduler = sched.scheduler(time.time, time.sleep)
    timeLeft = getMarketHours()
    # timeLeft = 0 # Debugging, bypass market hours
    if timeLeft > 0:
        # If the value of timeLeft is greater than 0 seconds, then it shall schedule to run the startTicker function after x amount of seconds
        event = scheduler.enter(timeLeft, 1, startTicker)
        scheduler.run()
    else: # Otherwise just start it straight away
        startTicker()


# Global stuff
init() # Colorama needs this
stockList = inputStocks() # Read .txt file
stockDict = {} # define stockDict for clarity
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'} # Headers to make our request function properly


if __name__ == "__main__":
    main()
