# encoding: utf-8
__author__ = 'PyBeaner'
import sys
import struct


class SimpleMFT:
    def __init__(self, file_mft='', drive='C'):
        self.file_mft = file_mft
        self.drive = drive

    def get_records(self):
        with open(self.file_mft,'rb') as mft_to_read:
            mft_to_read.seek(0)
            raw_record = mft_to_read.read(1024)
            records = []
            while raw_record:
                record = self.parse_record(raw_record)
                if record:
                    records.append(record)
                raw_record = mft_to_read.read(1024)
            self.gen_record_paths(records)
        return records

    def parse_record(self, raw_record):
        record = {}
        self.decodeMFTHeader(record, raw_record)
        read_ptr = record['attr_off']
        while (read_ptr < 1024):
            ATRrecord = self.decodeATRHeader(raw_record[read_ptr:])
            if ATRrecord['type'] == 0xffffffff:             # End of attributes
                break
            elif ATRrecord['type'] == 0x30:                 # File name
                FNrecord = self.decodeFNAttribute(raw_record[read_ptr+ATRrecord['soff']:])
                record.update(FNrecord)

            if ATRrecord['len'] > 0:
                read_ptr = read_ptr + ATRrecord['len']
            else:
                break
        return record

    def gen_record_paths(self, records):
        for record in records:
            try:
                record['parent_path'] = self.get_parent_path(record, records)
            except:
                print sys.exc_info(), record

    def get_parent_path(self, record, records):
        try:
            if record['par_ref'] == 5:
                return '%s:' % self.drive

            par_record = records[record['par_ref']]
            grand_par_path = self.get_parent_path(par_record, records)
            return grand_par_path + '/' + par_record['name']
        except:
            pass

    def decodeMFTHeader(self,record,raw_record):
        record['attr_off'] = struct.unpack("<H",raw_record[20:22])[0]

    def decodeATRHeader(self,s):
        d = {}
        d['type'] = struct.unpack("<L",s[:4])[0]
        if d['type'] == 0xffffffff:
            return d
        d['len'] = struct.unpack("<L",s[4:8])[0]
        d['res'] = struct.unpack("B",s[8])[0]
        if d['res'] == 0:
            d['soff'] = struct.unpack("<H",s[20:22])[0]
        return d

    def decodeFNAttribute(self, s):
        d = {}
        # d['nlen'] = struct.unpack("B",s[64])[0]
        # bytes = s[66:66 + d['nlen']*2]
        d['par_ref'] = struct.unpack("<Lxx", s[:6])[0]
        nlen = struct.unpack("B",s[64])[0]
        bytes = s[66:66 + nlen*2]
        try:
            d['name'] = bytes.decode('utf-16').encode('utf-8')
        except:
            d['name'] = 'UnableToDecodeFilename'
        return d

if __name__ == '__main__':
    session = SimpleMFT(file_mft=r'../data/mft_c', drive='C')
    records = session.get_records()
    print records[5616]

    # import json
    # db = [record['full_path'] for record in records]
    # f = open('../data/db', 'wb').write(json.dumps(db))
    # for item in json.loads(open('../data/db','rb').read()):
    #     if item:
    #         if 'pycharm' in item.lower():
    #             print item