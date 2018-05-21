'testing code'

# import orm
# from models import User, Blog, Comment
# import asyncio
#
#
# async def test():
#     await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='password123456', db='awesome')
#
#     u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#
#     await u.save()
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(test())
# loop.close()

'sql check code'
import mysql.connector

conn=mysql.connector.connect(user='root', password='password123456', database='awesome')
cursor=conn.cursor()
cursor.execute('select * from users')
data=cursor.fetchall()
print(data)