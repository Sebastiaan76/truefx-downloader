import psycopg2
import time

# variables to hold info for what we want to import
table_name = 'AUDUSD2_ticks'
Database = 'dbname=truefxdb user=sebastiaan'
csv_file = '/home/sebastiaan/truefx/AUDUSD-2017-10.csv'
command = "CREATE TABLE " + table_name + " (currency text, datetime timestamp, bid numeric, ask numeric)"

# connect to the DB
conn = psycopg2.connect(Database)
cur = conn.cursor()

# create the table
try:
    cur.execute(command)
    conn.commit()
except psycopg2.ProgrammingError:
    print("table exists")
    conn.commit()

cur = conn.cursor()
start = time.time()
# import the contents of 'csv_file' into the table
with open(csv_file, 'r') as import_file:
    row_count  = 0
    for lines in import_file:
        row_count += 1
    import_file.seek(0)
    cur.copy_from(import_file, table_name, ',')

conn.commit()
conn.close()
elapsed = time.time() - start
print("imported {} rows in: {:.2f} seconds".format(row_count, elapsed))
