# -*- coding: utf-8 -*-
# import logging
# _logger = logging.getLogger(__name__)

KHONG = "không"
MOT = "một"
HAI = "hai"
BA = "ba"
BON = "bốn"
NAM = "năm"
SAU = "sáu"
BAY = "bảy"
TAM = "tám"
CHIN = "chín"
MUOI = "mươi"
MUOI_2 = "mười"
TRAM = "trăm"
TRAM_LINH = "trăm linh"
TRAM_MUOI = "trăm mười"
MUOI_NAM   = "mươi năm"
MUOI_LAM   = "mươi lăm"
MUOI_NAM_2 = "mười năm"
MUOI_LAM_2 = "mười lăm"
NGHIN = "nghìn"
TRIEU = "triệu"
TY = "tỷ"
DONG = "đồng"
SPACE = " "

def numberToString(number):
    sR = ""
    if number == 0:
        sR = KHONG
    elif number == 1:
        sR = MOT
    elif number == 2:
        sR = HAI
    elif number == 3:
        sR = BA
    elif number == 4:
        sR = BON
    elif number == 5:
        sR = NAM
    elif number == 6:
        sR = SAU
    elif number == 7:
        sR = BAY
    elif number == 8:
        sR = TAM
    elif number == 9:
        sR = CHIN
    else:
        sR = ""

    return sR

def TransferUnit(Number):
    sNumber = ""
    Number = str(Number)
    # try:
    length = 0
    if Number:
        length = len(Number)
    
    if length==1:
        iNu = int("" + str(Number[0]))
        sNumber += numberToString(iNu)
    elif length==2:
        iChuc = int("" + str(Number[0]))
        iDV = int("" + str(Number[1]))
        if iChuc==1:
            if iDV > 0:
                sNumber += MUOI_2 + SPACE + numberToString(iDV)
            else:
                sNumber += MUOI_2
        else:
            if iDV > 0:
                sNumber += numberToString(iChuc) + SPACE + MUOI + SPACE + numberToString(iDV)
            else:
                sNumber += numberToString(iChuc) + SPACE + MUOI
    else:
        iTram = int("" + str(Number[0]))
        iChuc = int("" + str(Number[1]))
        iDV = int("" + str(Number[2]))

        if iChuc==0:
            if iDV >0:
                sNumber += numberToString(iTram) + SPACE + TRAM_LINH + SPACE + numberToString(iDV)
            else:
                sNumber += numberToString(iTram) + SPACE + TRAM
        elif iChuc==1:
            if iDV > 0:
                sNumber += numberToString(iTram) + SPACE + TRAM_MUOI + SPACE + numberToString(iDV)
            else:
                sNumber += numberToString(iTram) + SPACE + TRAM_MUOI
        else:
            if iDV > 0:
                sNumber += numberToString(iTram) + SPACE + TRAM + SPACE + numberToString(iChuc) + SPACE + MUOI + SPACE + numberToString(iDV) 
            else:
                sNumber += numberToString(iTram) + SPACE + TRAM + SPACE + numberToString(iChuc) + SPACE + MUOI
    # except: 
    #     _logger.error('TransferUnit error')
    
    return sNumber

# Transfer money number to money string
def translate(sNumber):
    sR = ""
    sR1 = ""
    sR2 = ""
    sR3 = ""
    sR4 = ""

    # try:
    # Skip decimal point part
    sNumber = int(sNumber)
    sNumber = str(sNumber)
    seq=0
    k = 1
    i = len(sNumber)
    # for(int i = sNumber.length() ; i >= 0 ; i--)
    while i >= 0:
        if seq == 3:
            subStr = str(sNumber[i: i + seq])
            
            if k==1:
                sR = TransferUnit(subStr) + SPACE + DONG
            elif k==2:
                sR1 = TransferUnit(subStr) + SPACE + NGHIN + SPACE
            elif k==3:
                sR2 = TransferUnit(subStr) + SPACE + TRIEU + SPACE
            else:
                sR3 = TransferUnit(subStr) + SPACE + TY + SPACE;
                
                # Reset
                k = 1;
                sR = sR3 + sR2 + sR1 + sR
                sR3 = ""
                sR2 = ""
                sR1 = ""
            
            seq = 0
            k += 1
        seq += 1
        i -= 1
    
    if seq > 1:
        subStr = str(sNumber[0: seq - 1])
        if k==1:
            sR = TransferUnit(subStr) + SPACE + DONG
        elif k==2:
            sR1 = TransferUnit(subStr) + SPACE + NGHIN + SPACE
        elif k==3:
            sR2 = TransferUnit(subStr) + SPACE + TRIEU + SPACE
        else:
            sR3 = TransferUnit(subStr) + SPACE + TY + SPACE
    
    # seq
    sR4 = sR3 + sR2 + sR1 + sR
    
    # except: 
    #     _logger.error('translate(sNumber) error')
    
    sR4 = filter(sR4)
    
    return sR4

    
def filter(pNumber):
    # Filter 1
    lvFilterMillion = [ \
        KHONG + SPACE + TRAM + SPACE + TRIEU + SPACE + KHONG + SPACE + TRAM + SPACE + NGHIN + SPACE + KHONG + SPACE + TRAM + SPACE + DONG, \
        KHONG + SPACE + TRAM + SPACE + NGHIN + SPACE + KHONG + SPACE + TRAM + SPACE + DONG, \
        KHONG + SPACE + TRAM + SPACE + DONG
    ]
    
    index = 0
    
    # for( int i=0; i<lvFilterMillion.length; i++ )
    i = 0
    while i < len(lvFilterMillion):
        index = indexOf(pNumber, lvFilterMillion[i])
        if index != -1:
            pNumber = pNumber[0: index]
            pNumber += DONG
            break
        i += 1
    
    # Filter 2
    lvFilterBil = [ \
        KHONG + SPACE + TRAM + SPACE + TRIEU + SPACE + KHONG + SPACE + TRAM + SPACE + NGHIN + SPACE + KHONG + SPACE + TRAM + SPACE + TY + SPACE + DONG, \
        KHONG + SPACE + TRAM + SPACE + NGHIN + SPACE + KHONG + SPACE + TRAM + SPACE + TY + SPACE + DONG \
    ]
    index = 0
    
    # for( int i=0; i<lvFilterBil.length; i++ )
    i = 0
    while i < len(lvFilterBil):
        index = indexOf(pNumber, lvFilterBil[i])
        if index != -1:
            pNumber = pNumber[0: index]
            pNumber +=  TY + SPACE + DONG
            break
        i += 1
    
    # Filter 3
    lvFilterBil1 = [
        KHONG + SPACE + TRAM + SPACE + TRIEU + SPACE + KHONG + SPACE + TRAM + SPACE + NGHIN + SPACE + KHONG + SPACE + TRAM + SPACE
    ]
    index = 0
    
    # for( int i=0; i<lvFilterBil1.length; i++ )
    i = 0
    while i < len(lvFilterBil1):
        index = indexOf(pNumber, lvFilterBil1[i])
        if index != -1:
            pNumber = pNumber.replace(lvFilterBil1[i], "")
        i += 1
    
    # change nam to lam
    lvFilter4 = [ \
        MUOI_NAM, \
        MUOI_NAM_2 \
    ]
    
    index = 0
    
    # for( int i=0; i<lvFilter4.length; i++ )
    i = 0
    while i < len(lvFilter4):
        index = indexOf(pNumber, lvFilter4[i])
        if index != -1:
            if i == 0:
                pNumber = pNumber.replace(lvFilter4[i], MUOI_LAM)
            else:
                pNumber = pNumber.replace(lvFilter4[i], MUOI_LAM_2)
        i += 1
    
    # Upper first letter
    pNumber = pNumber.capitalize()
    
    return pNumber

def indexOf(pNumber, pStr):
    index = -1
    try:
        index = pNumber.index( pStr )
    except:
        index = -1
    return index