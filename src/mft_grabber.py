# encoding: utf-8
#!/usr/bin/python
__author__ = 'PyBeaner'

import os
import ctypes
import struct
import binascii
from StringIO import StringIO

#constant size values
LONG_LONG_SIZE = ctypes.sizeof(ctypes.c_longlong)
BYTE_SIZE = ctypes.sizeof(ctypes.c_byte)
WORD_SIZE = 2

# decode ATRHeader from
# analyzeMFT.py routines
# Copyright (c) 2010 David Kovar.
def decodeATRHeader(s):
    d = {}
    d['type'] = struct.unpack("<L",s[:4])[0]
    if d['type'] == 0xffffffff:
        return d
    d['len'] = struct.unpack("<L",s[4:8])[0]
    d['res'] = struct.unpack("B",s[8])[0]
    if d['res']:
        d['run_off'] = struct.unpack("<H",s[32:34])[0]

    return d


def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val


#decode NTFS data runs from a MFT type 0x80 record ala:
#http://inform.pucp.edu.pe/~inf232/Ntfs/ntfs_doc_v0.5/concepts/data_runs.html
def decodeDataRuns(dataruns):
    decodePos=0
    header=dataruns[decodePos]
    while header !='\x00':
        offset=int(binascii.hexlify(header)[0])
        runlength=int(binascii.hexlify(header)[1])

        #move into the length data for the run
        decodePos+=1
        length=dataruns[decodePos:decodePos +int(runlength)][::-1]
        length=int(binascii.hexlify(length),16)
        hexoffset=dataruns[decodePos +runlength:decodePos+offset+runlength][::-1]
        cluster=twos_comp(int(binascii.hexlify(hexoffset),16),offset*8)

        yield(length,cluster)
        decodePos=decodePos + offset+runlength
        header=dataruns[decodePos]


def mft_raw_by_drive(drive='C'):
    ntfs_drive=file(r'\\.\%s:' % drive,'rb')
    if os.name=='nt':
        #poor win can't seek a drive to individual bytes..only 1 sector at a time..
        #convert MBR to stringio to make it seekable
        ntfs = ntfs_drive.read(512)
        ntfs_file = StringIO(ntfs)
    else:
        ntfs_file = ntfs_drive

    #parse the MBR for this drive to get the bytes per sector,sectors per cluster and MFT location.
    #bytes per sector
    ntfs_file.seek(0x0b)
    bytesPerSector=ntfs_file.read(WORD_SIZE)
    bytesPerSector=struct.unpack('<h', binascii.unhexlify(binascii.hexlify(bytesPerSector)))[0]

    #sectors per cluster

    ntfs_file.seek(0x0d)
    sectorsPerCluster=ntfs_file.read(BYTE_SIZE)
    sectorsPerCluster=struct.unpack('<b', binascii.unhexlify(binascii.hexlify(sectorsPerCluster)))[0]


    #get mftlogical cluster number
    ntfs_file.seek(0x30)
    cno=ntfs_file.read(LONG_LONG_SIZE)
    mftClusterNumber=struct.unpack('<q', binascii.unhexlify(binascii.hexlify(cno)))[0]

    #MFT is then at NTFS + (bytesPerSector*sectorsPerCluster*mftClusterNumber)
    mft_loc=long(bytesPerSector*sectorsPerCluster*mftClusterNumber)
    ntfs_drive.seek(0)
    ntfs_drive.seek(mft_loc)
    mft_raw=ntfs_drive.read(1024)

    read_ptr=0
    mftDict={}
    mftDict['attr_off'] = struct.unpack("<H",mft_raw[20:22])[0]
    read_ptr=mftDict['attr_off']
    mft_data = ''
    while read_ptr<len(mft_raw):
        ATRrecord = decodeATRHeader(mft_raw[read_ptr:])
        if ATRrecord['type'] == 0x80:
            dataruns=mft_raw[read_ptr+ATRrecord['run_off']:read_ptr+ATRrecord['len']]
            prevCluster=None
            prevSeek=0
            for length,cluster in decodeDataRuns(dataruns):
                if prevCluster==None:
                    ntfs_drive.seek(cluster*bytesPerSector*sectorsPerCluster)
                    prevSeek=ntfs_drive.tell()
                    mft_data+=ntfs_drive.read(length*bytesPerSector*sectorsPerCluster)
                    prevCluster=cluster
                else:
                    ntfs_drive.seek(prevSeek)
                    newpos=prevSeek + (cluster*bytesPerSector*sectorsPerCluster)
                    ntfs_drive.seek(newpos)
                    prevSeek=ntfs_drive.tell()
                    mft_data+=ntfs_drive.read(length*bytesPerSector*sectorsPerCluster)
                    prevCluster=cluster
            break
        if ATRrecord['len'] > 0:
            read_ptr = read_ptr + ATRrecord['len']

    return mft_data

if __name__ == '__main__':
    data = mft_raw_by_drive('C')
    open('mft_c','wb').write(data)