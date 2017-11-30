import psycopg2
from time import time
from datetime import datetime
from hashlib import sha512
import os


def get_hash(file_path):
    """returns Sha512 hash of file"""
    with open(file_path, 'rb') as f:
        return sha512(f.read()).hexdigest()


def get_files(start_dir):
    """gets list of csv files for import and returns list of tuples [(<file>, <hash>), (...)]"""
    raw_files = os.listdir(start_dir)
    csv_files = [f for f in raw_files if f.split('.')[-1] == 'csv']

    print("identifying files in {}".format(start_dir))
    print("---------------------" + "-" * len(start_dir))

    final_list = []
    for f in csv_files:
        print("{}...".format(f), end="")
        f_hash = get_hash(start_dir + '/' + f)
        pair = (f, f_hash)
        final_list.append(pair)
        print("signature identified")
    print("-" * 60)

    return final_list


def check_exists(table, cur):
    """checks if table already exists in the DB"""
    sql = "SELECT to_regclass('public." + table + "')"
    cur.execute(sql)
    result = cur.fetchone()
    if str(result[0]).upper() == table.upper():
        return True
    else:
        return False


def check_hash_exists(hash_to_check, cur):
    """checks DB metadata table to see if a file with the same checksum has been uploaded previously"""
    sql = "SELECT sha512 FROM HASHES_TABLE"
    cur.execute(sql)
    result = cur.fetchall()
    h_list = []
    for l in result:
        h_list.append(l[0])

    is_in = False
    for item in h_list:

        if item == hash_to_check:
            is_in = True
    return is_in


def copy_to_db(csv_file, table_name, cur):
    """helper function to abstract the actual copy_to() functionality"""
    start = time()
    print("importing file: {}".format(str(csv_file.split('/')[-1])))
    with open(csv_file, 'r') as import_file:
        row_count = 0
        for _ in import_file:
            row_count += 1
        import_file.seek(0)
        cur.copy_from(import_file, table_name, ',')
        elapsed = time() - start
        print("imported {:,} rows in: {:.2f} seconds".format(row_count, elapsed))
        print("------------------------------------")
    return


def import_files(start_dir, db, username):
    """main import function"""

    # connect to the DB
    Database = 'dbname={} user={}'.format(db, username)
    conn = psycopg2.connect(Database)
    cur = conn.cursor()
    print("connecting to database...")

    # get list of files in the directory and filter only CSV files
    file_list = get_files(start_dir)
    for f in file_list:
        table_name = "{}_ticks".format(str(f[0].split('-')[0])).upper()
        csv_file = "{}/{}".format(str(start_dir), str(f[0]))

        # start the process with checks and balances along the way
        if check_exists(table_name, cur):
            conn.commit()
        else:
            create_table = "CREATE TABLE " + table_name + " (currency text, datetime timestamp, bid numeric, ask numeric)"
            cur.execute(create_table)
            conn.commit()
            print("created table: {}".format(table_name))

        hashes_sql = "INSERT INTO HASHES_TABLE VALUES (\'{}\', \'{}\', \'{}\', \'{}\')".format(csv_file.split('/')[-1], f[1], table_name, str(datetime.now()))
        if check_exists('HASHES_TABLE', cur):
            if check_hash_exists(f[1], cur):
                print("{} already imported...skipping".format(f[0]))
                conn.commit()
            else:
                cur.execute(hashes_sql)
                copy_to_db(csv_file, table_name, cur)
                conn.commit()
        else:
            print("creating metadata table")
            cur.execute("CREATE TABLE HASHES_TABLE (file_name text, sha512 text, table_imported text, date_imported timestamp)")
            copy_to_db(csv_file, table_name, cur)
            cur.execute(hashes_sql)
            conn.commit()
    conn.close()


if __name__ == "__main__":
    import_files('/home/sebastiaan/Sebshare/TradeBot/zipfiles/USDJPY', 'truefxdb', 'sebastiaan')


