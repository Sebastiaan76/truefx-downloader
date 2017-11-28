import psycopg2
import time
from datetime import datetime
import hashlib
import os
# TODO make function to compare hashes when importing to avoid duplicate imports, refactor, tidy up

# returns Sha512 hash of file
def get_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha512(f.read()).hexdigest()


# gets list of csv files for import and returns list of tuples [(<file>, <hash>), (...)]
def get_files(start_dir):
    raw_files = os.listdir(start_dir)
    csv_files = [f for f in raw_files if f.split('.')[-1] == 'csv']
    print("identifying files in {}".format(start_dir))
    final_list = []
    for f in csv_files:
        f_hash = get_hash(start_dir + '/' + f)
        pair = (f, f_hash)
        final_list.append(pair)
    for f in final_list:
        print("{}...hashed".format(f[0]))
    return final_list


def import_files(start_dir):
    Database = 'dbname=truefxdb user=sebastiaan'
    conn = psycopg2.connect(Database)
    cur = conn.cursor()
    print("connecting to database...")
    file_list = get_files(start_dir)
    for f in file_list:
        table_name = str(f[0].split('-')[0]) + "_ticks"
        table_name = table_name.upper()
        check_table = "SELECT to_regclass('public." + table_name + "')"
        check_hashes_table = "SELECT to_regclass('public.HASHES_TABLE')"
        imported_files = "CREATE TABLE HASHES_TABLE (file_name text, sha512 text, table_imported text, date_imported timestamp)"

        create_table = "CREATE TABLE " + table_name + " (currency text, datetime timestamp, bid numeric, ask numeric)"
        csv_file = str(start_dir) + '/' + str(f[0])

        cur.execute(check_table)
        check = cur.fetchone()
        if str(check[0]).upper() == table_name.upper():
            print("Table '{}' exists - adding to existing".format(check[0]))
            conn.commit()
        else:
            cur.execute(create_table)
            conn.commit()
            print("created table: {}".format(table_name))

        start = time.time()
        # import the contents of 'csv_file' into the table
        print("importing file: {}".format(str(csv_file.split('/')[-1])))
        with open(csv_file, 'r') as import_file:
            row_count = 0
            for lines in import_file:
                row_count += 1
            import_file.seek(0)
            cur.copy_from(import_file, table_name, ',')

        hashes_sql = "INSERT INTO HASHES_TABLE VALUES (\'{}\', \'{}\', \'{}\', \'{}\')".format(csv_file.split('/')[-1], f[1], table_name, str(datetime.now()))
        cur.execute(check_hashes_table)
        if str(cur.fetchone()[0]).upper() == 'HASHES_TABLE':
            print("adding import details")

            cur.execute(hashes_sql)
            conn.commit()
        else:
            print("creating log table to track imports")
            cur.execute(imported_files)
            cur.execute(hashes_sql)
            conn.commit()

        conn.commit()
        elapsed = time.time() - start
        print("imported {:,} rows in: {:.2f} seconds".format(row_count, elapsed))
    conn.close()

import_files('/home/seb-i3/truefx')


