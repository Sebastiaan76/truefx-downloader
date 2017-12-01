import psycopg2
import datetime

db = "dbname=truefxdb user=sebastiaan"
conn = psycopg2.connect(db)
cur = conn.cursor()


def get_ticks(currency, start_date, end_date):
    """This function returns a tuple of tuples containing STR representations of the data
    dates should be entered in the following format: '2017-10-31 13:45:59.000'
    Currencies should be entered as so: AUDUSD ( not AUD/USD )"""
    sql = "SELECT * FROM " + currency + "_TICKS WHERE datetime BETWEEN '" + start_date + "' AND '" + end_date + "' ORDER BY datetime ASC"
    cur.execute(sql)
    result = cur.fetchall()
    result_list = []
    for row in result:
        currentrow = []
        currentrow = [str(row[0]), row[1], float(row[2]), float(row[3])]
        currentrow = tuple(currentrow)
        result_list.append(currentrow)
    conn.commit()
    conn.close()
    return tuple(result_list)

time_range = get_ticks('AUDUSD', '2017-10-23 10:00:00.000', '2017-10-23 13:00:01.000')




