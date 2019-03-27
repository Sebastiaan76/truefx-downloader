#!/usr/bin/env python3

from dateutil import parser
from datetime import datetime, timedelta
import sys
import psycopg2
import heapq


class Candle:
    def __init__(self, database_arg):
        self.dbname = database_arg['dbname']
        self.host = database_arg['host']
        self.port = database_arg['port']
        self.user = database_arg['user']
        self.password = database_arg['password']
        self.csv = False
        self.table = False

        # set attributes depending if user needs to make candles from a DB or a raw CSV file
        if 'table' in database_arg:
            self.table = database_arg['table']
            print("Import Mode: Database Source")
        elif 'csv' in database_arg:
            self.csv = database_arg['csv']
            print("Import Mode: CSV Source")

    def process_csv_line(self, line):
        line = line.rstrip('\n')
        line = line.split(",")
        dt = line[1].strip('"')
        newdt = parser.parse(dt)
        line[0] = line[0].strip('"')  # currency symbol as str: i.e. AUDUSD
        line[1] = newdt  # datetime as datetime object
        line[2] = float(line[2].strip('"'))  # bid price as float for this tick
        line[3] = float(line[3].strip('"'))  # ask price as float for this tick
        return line

    def generator(self):
        if self.csv:
            return self.generator_csv()
        else:
            return self.generator_db()

    def generator_csv(self):
        """Function creates a generator - [str, datetime.datetime(), float, float] from truefx.com format CSV file"""
        rows = 0
        process_count = 0
        with open(self.csv, "r") as file:
            for _ in file:
                rows += 1
        print("processing {} rows".format(rows))

        with open(self.csv, "r") as file:
            for line in file:
                transformed_line = self.process_csv_line(line)
                progress = "{}% complete".format(int((process_count / rows) * 100))
                sys.stdout.write("\r" + progress)
                sys.stdout.flush()
                process_count += 1
                yield transformed_line

    def generator_db(self):
        # connect to the DB
        process_count = 0
        with psycopg2.connect('dbname={} host={} port={} user={} password={}'
                     .format(self.dbname, self.host, self.port, self.user, self.password)) as conn:
            with conn.cursor() as count_cur:
                count_cur.execute("SELECT count(*) FROM " + self.table + ";")
                rows = count_cur.fetchall()[0][0]
                print("Processing {} rows".format(rows))

            with conn.cursor(name='fx_cursor') as cursor:
                cursor.itersize = 20000

                q = "SELECT * FROM " + self.table + " ORDER BY datetime"
                cursor.execute(q)

                for row in cursor:
                    progress = "{}% complete".format(int((process_count / rows) * 100))
                    sys.stdout.write("\r" + progress)
                    sys.stdout.flush()
                    process_count += 1
                    yield list(row)

    # from Stackoverflow: https://stackoverflow.com/questions/32723150/rounding-up-to-nearest-30-minutes-in-python
    def next_increment(self, dt, delta):
        """Function rounds up to the nearest 'delta' for a datetime i.e. 00:01:32 delta of 5min rounds up to 00:05:00"""
        return dt + (datetime.min - dt) % delta

    def make_candle(self, mins, generator):
        candle = []
        current_timestamp = None

        # build the candle list. Iterating over a generator of ticks in format ['CUR/CUR', datetime, bid, ask]
        for line in generator:
            # is this the first item? if so - set the timedate stamp based on the first datetime
            if not current_timestamp:
                current_timestamp = self.next_increment(line[1], timedelta(minutes=mins))

            # as long as we are within the bounds of our current candle time for the chosen timeframe
            if line[1] < current_timestamp:
                candle.append(line)

            # if we've iterated to a record with a datetime > current candle time - time to yield a full OHLC candle
            if line[1] >= current_timestamp:
                c_dt = current_timestamp
                c_vol = len(candle)      # no of ticks = volume ( tick volume )
                c_open = candle[0][2]    # open = first tick bid price
                c_close = candle[-1][2]  # close = last tick bid price

                # heapq returns a list of lists, here our list will only ever be 1 item, hence [0][2] returns bid
                c_high = heapq.nlargest(1, candle, key=lambda s: s[2])[0][2] # find the highest bid in [candle]
                c_low = heapq.nsmallest(1, candle, key=lambda s: s[2])[0][2] # find the lowest bid in [candle]

                yield [line[0], c_dt - timedelta(minutes=mins), c_open, c_high, c_low, c_close, c_vol, mins]

                # increment the next candle datetime and reset variables for next iteration
                current_timestamp = self.next_increment(line[1], timedelta(minutes=mins))
                candle = []
        return

    def check_exists(self, table):
        """checks if table already exists in the DB"""
        with psycopg2.connect('dbname={} host={} port={} user={} password={}'
                     .format(self.dbname, self.host, self.port, self.user, self.password)) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT to_regclass('public." + table + "')"
                cursor.execute(sql)
                result = cursor.fetchone()
                if str(result[0]).upper() == table.upper():
                    return True
                else:
                    return False

    def check_candle_exists(self, candle_datetime, table_name):
        """checks if an individual candle already exists"""
        flag = False
        sql = "SELECT candletime FROM " + table_name + " ORDER BY candletime"
        with psycopg2.connect('dbname={} host={} port={} user={} password={}'
                                      .format(self.dbname, self.host, self.port, self.user, self.password)) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                for row in data:
                    if candle_datetime == row[0]:
                        flag = True
        return flag

    def write_to_db(self, ohlc, tf, currency):
        table_name = "{}_TF_{}".format(currency, tf)
        # connect to DB
        with psycopg2.connect('dbname={} host={} port={} user={} password={}'
                     .format(self.dbname, self.host, self.port, self.user, self.password)) as conn:
        # check if minutes table already exists for that TF
            with conn.cursor() as cursor:
                if not self.check_exists(table_name):
                    sql = "CREATE TABLE " + table_name + " (currency text, candletime timestamp, open numeric, high numeric, low numeric, close numeric, volume numeric, candle_timeframe numeric)"
                    cursor.execute(sql)
                    conn.commit()
                    print("created table: {}".format(table_name))
                # check again and should result in TRUE now, so we import the candle data
                if self.check_exists(table_name):
                    iter_count = 0
                    non_dupe_count = 0
                    for row in ohlc:
                        iter_count += 1
                        sql = "INSERT INTO " + table_name + " VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".format(row[0], row[1],row[2], row[3], row[4], row[5], row[6], row[7])
                        #first check to make sure a candle with this timestamp doesn't already exist
                        if not self.check_candle_exists(row[1], table_name):
                            non_dupe_count += 1
                            with conn.cursor() as cursor:
                                cursor.execute(sql)
                                conn.commit()
                    print("imported {} new candles. Ignored {} candles because they were duplicate.".format(non_dupe_count, iter_count - non_dupe_count))
        return


if __name__ == '__main__':

    # adjust these to what currency & timeframe you want in minutes e.g. 240 = 240 mins which is a 4H candle
    currency = "EURCHF"
    timeframe = 240
    database = {"dbname": "fx_data", "host": "0.0.0.0", "port": "5432", "user": "<DBUSER>",
                "password": "<PASSWORD>", 'table': currency + '_ticks'}


    #instantiate the candle object & pass it the database arguments in dict form last key/value should be
    #'csv': 'CSV_FILE' or 'table': 'currency'
    candle = Candle(database)
    # create a generator object to iterate over
    gen = candle.generator()
    # call makecandle to generate ohlc data - pass timeframe in minutes and the generator object
    candles = candle.make_candle(timeframe, gen)
    # pass the resulting transformed data to the write_to_db method
    candle.write_to_db(candles, timeframe, currency)
