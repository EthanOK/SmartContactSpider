# -*- coding: utf8 -*-
# SmartContactSpider.py
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
import config

etherscan_url = config.etherscan_url

listNumber = config.listNumber


def printtime():
    print(time.strftime("%Y-%m-%d %H:%M:%S:", time.localtime()), end=" ")
    return 0


def getsccodecore(datajson):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }

    failedTimes = 50
    while True:
        if failedTimes <= 0:
            printtime()
            print("final failed times exceed 50!")
            break

        failedTimes -= 1
        try:

            printtime()
            print("fecth:" + datajson.get("codeURL"))
            response = requests.get(datajson.get("codeURL"), headers=headers, timeout=5)
            break

        except requests.exceptions.ConnectionError:
            printtime()
            print("ConnectionError! please wait 3 second!")
            time.sleep(3)

        except requests.exceptions.ChunkedEncodingError:
            printtime()
            print("ChunkedEncodingError! please wait 3 second!")
            time.sleep(3)

        except:
            printtime()
            print("Unfortunitely Error! please wait 3 second!")
            time.sleep(3)

    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    # js-sourcecopyarea editor ace_editor ace-dawn
    targetPRE = soup.find_all("pre", "js-sourcecopyarea editor")
    filepath = getPathCodeDirectory()
    os.makedirs(filepath, exist_ok=True)

    filename = datajson.get("address")
    if os.path.exists(filepath + filename + ".sol"):
        printtime()
        print(filename + ".sol already exists!")
        return 0

    fo = open(filepath + filename + ".sol", "w+", encoding="utf-8")
    for eachpre in targetPRE:
        try:
            json.loads(eachpre.text)
            print("Skipping Settings JSON")
            continue
        except json.JSONDecodeError:
            fo.write(eachpre.text)

    fo.close()
    printtime()
    print(filename + ".sol created!")

    return 0


def getsccode():
    jsonfilepath = getUrlJsonFilePath()
    try:
        with open(jsonfilepath, "r") as file:
            datas = json.load(file)

    except:
        printtime()
        print("read json file error!")

    for data in datas:
        getsccodecore(data)

    file.close()
    return 0


def getSCAddress(eachurl):
    json_array = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }

    failedTimes = 50

    while True:

        if failedTimes <= 0:
            printtime()
            print("final failed times exceed 50!")
            break

        failedTimes -= 1
        try:
            print("fecth:" + eachurl)
            response = requests.get(url=eachurl, headers=headers, timeout=5)
            break

        except requests.exceptions.ConnectionError:
            printtime()
            print("connectionError! waiting 3 second!")
            time.sleep(3)

        except requests.exceptions.ChunkedEncodingError:
            printtime()
            print("ChunkedEncodingError! waiting 3 second!")
            time.sleep(3)

        except:
            printtime()
            print("error! waiting 3 second!")
            time.sleep(3)

    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # targetDiv = soup.find_all('div', 'table-responsive')

    try:
        targetTBody = soup.find_all("tbody", "align-middle text-nowrap")[0]

    except:
        printtime()
        print("get targetTBody failed!")
        return [], 1

    for targetTR in targetTBody:
        if targetTR.name == "tr":
            data = targetTR.find_all("td")
            # /address/0xceea87307db481e5ffbd412784e17e02e3851ace#code
            herf = targetTR.td.find("a", "me-1").attrs["href"]
            match = re.search(r"0x[a-fA-F0-9]{40}", herf)
            if match:
                Address = match.group(0)
            Name = data[1].getText()
            Compiler = data[2].getText()
            Version = data[3].getText()
            Balance = data[4].getText()
            VerifiedTime = data[7].getText()
            if "Solidity".lower() in Compiler.lower():
                item = {
                    "contractnName": Name,
                    "address": Address,
                    "codeURL": etherscan_url + herf,
                    "version": Version,
                    "verified": VerifiedTime,
                }
                json_array.append(item)

    return json_array, 0


def getUrlList():
    if listNumber == config.ListNumber.FiveHundred:
        return getUrlList500()
    if listNumber == config.ListNumber.TenThousand:
        return getUrlList10000()


# 仅显示最后500经已验证的合约源码
def getUrlList500():

    urlList = []

    for i in range(5):
        page = i + 1
        urlList.append(
            etherscan_url + "/contractsVerified/" + str(page) + "?filter=solc&ps=100"
        )

    return urlList


# 仅显示最后10,000经已验证的合约源码 (OpenSource)
def getUrlList10000():

    urlList = []

    for i in range(100):
        page = i + 1
        urlList.append(
            etherscan_url
            + "/contractsVerified/"
            + str(page)
            + "?filter=opensourcelicense&ps=100"
        )

    return urlList


def getUrlJsonFilePath():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    address_directory_path = os.path.join(current_directory, "temp_address")
    os.makedirs(address_directory_path, exist_ok=True)
    relative_file_path = "address_500.json"
    if listNumber == config.ListNumber.TenThousand:
        relative_file_path = "address_10000.json"
    address_file_path = os.path.join(address_directory_path, relative_file_path)
    return address_file_path


def getPathCodeDirectory():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    relative_file_path = "temp_code/code500/"
    if listNumber == config.ListNumber.TenThousand:
        relative_file_path = "temp_code/code10000/"
    code_directory_path = os.path.join(current_directory, relative_file_path)
    return code_directory_path


def updatescurl():
    urlList = getUrlList()

    filepath = getUrlJsonFilePath()

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            printtime()
            print("Remove", filepath)
    except IOError:

        printtime()
        print("IOError!")

        return 1

    all_json_data = []
    for eachurl in urlList:
        time = 0
        while True:
            json_array, result = getSCAddress(eachurl)
            if result == 0:
                all_json_data.extend(json_array)
                break
            time += 1
            if time == 10:
                break

            pass

    json_data = json.dumps(all_json_data, indent=2)
    with open(filepath, "w") as fo:
        fo.write(json_data)

    return 0


def main():
    #  get the smart contract code url list
    updatescurl()

    # get the smart contract code
    getsccode()


main()
