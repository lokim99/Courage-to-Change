import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from mysql.connector.pooling import MySQLConnectionPool


con_pool = MySQLConnectionPool(pool_name='my_connection_pool', pool_size=10,
                               pool_reset_session=True, host='digitalhealth.csgtay1k0lha.us-east-1.rds.amazonaws.com', database='digitalhealth', user='master', password='digitalhealth123')

# con_pool = MySQLConnectionPool(pool_name='my_connection_pool', pool_size=10,
#                                pool_reset_session=True, host='localhost', database='upscpre', user='root', password='')
