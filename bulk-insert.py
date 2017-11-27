import psycopg2

# variables to hold info for what we want to import
table_name = 'AUDJPY_ticks'
Database = 'dbname=truefxdb user=sebastiaan'
csv_file = '/home/seb-i3/truefx/AUDJPY-2017-01.csv'
command = "CREATE TABLE " + table_name + " (currency text, datetime timestamp, bid numeric, ask numeric)"

# connect to the DB
conn = psycopg2.connect(Database)
cur = conn.cursor()

# create the table
cur.execute(command)
conn.commit()

# import the contents of 'csv_file' into the table
with open(csv_file, 'r') as import_file:
    cur.copy_from(import_file, table_name, ',')
conn.commit()
conn.close()
