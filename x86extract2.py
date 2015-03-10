import os
import argparse
import string
import re
from pymongo import MongoClient
import pymongo
from pymongo import Connection
from bson.son import SON


db = MongoClient("localhost", 27017)['x86']
#collection = db.testcollection
#list(db.test.find())

#client = MongoClient()
#client.drop_database("objdumparser")
#db = client.objdumparser
#db.things.aggregate({"bytes": "instructions", "instruction": "move", "mnemonic": "command", "addr": "address"})
#posts = db.posts
#post_id = posts.insert("troll")
non_duplicateset = set()
argv = []
parser = argparse.ArgumentParser()
parser.add_argument("--no-duplicates", help="displays only unique commands and memory addresses", action="store_false")
parser.add_argument("--output", help="the output in which the objdump results will be stored")
parser.add_argument("--input", help="specify the name and number of input files", nargs='+', type=str)
args = parser.parse_args()
output = open(args.output, 'w')


def objdumparser(in_file, output_file):
    print in_file
    for line in os.popen("objdump -M intel -d -w \"" + in_file + "\"").readlines():
        line = line.split('<')[0]
        if ":" in line:
            address = line.split('<')[0].split()[0]
            line = line.split(':')[1]
            if len(line) > 1 and len(line.split("\t")) > 2:
                start_bytes = line.split("\t")[1].strip().replace(" ", "")
                if '(' not in line.split("\t")[2]:
                    mnemonic = line.split("\t")[2].split()[0]
                else:
                    mnemonic = line.split("\t")[2].rstrip("\n")
                total_mnemonic = mnemonic + ", " + start_bytes
                total_mnemonic = total_mnemonic.rstrip("\r\n")
                cleanstring = total_mnemonic
                no_copies = no_duplicates(cleanstring, args.no_duplicates)
                db_record = {
                    'bytes': start_bytes,
                    'source': input_file,
                    'mnemonic': mnemonic,
                    'instruction': line.split("\t")[2].rstrip('\r\n'),
                    'addr': int(address.strip(":"), 16)
                }
                if no_copies == "Not a duplicate":
                    non_duplicateset.add(cleanstring)
                    output_file.write("%s\n" % cleanstring)
                    if db.instructions.find(db_record) != "":
                        db.instructions.insert(db_record)
                    #print cleanstring
                elif no_copies == "Either case ok":  # Either we don't search for duplicates or not a duplicate
                    output_file.write("%s\n" % cleanstring)
                    if db.instructions.find(db_record) != "":
                        db.instructions.insert(db_record)
                    #print cleanstring
                else:
                    pass


def no_duplicates(cleanstring, noduplicates):
    if noduplicates:
        if cleanstring not in non_duplicateset:
            return "Not a duplicate"
        else:
            return "Duplicate entry"
    if not noduplicates or noduplicates and cleanstring not in non_duplicateset:
        return "Either case ok"

print args
for input_file in args.input:
    objdumparser(input_file, output)
