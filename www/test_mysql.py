'testing code'

import orm
from models import User, Blog, Comment, Reply
import asyncio


async def test():
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='password123456', db='awesome')

    # u = User(name='Test2', email='test2@example.com', passwd='1234567890', image='about:blank2')

    # await u.save()
    reply = Reply(comment_id='001527235629310f05f5b66fd3f441dac59368bc6a5c243000',
                  user_id='0015271444248050b6689072c8f441cb53e158e535c2a9a000',
                  user_name='abc',
                  user_image='http://www.gravatar.com/avatar/4adcca49b3b1e5a08ac202f5d5a9e688?d=mm&s=120',
                  content='content content content2')

    await reply.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

# 'sql check code'
# import mysql.connector
#
# conn=mysql.connector.connect(user='root', password='password123456', database='awesome')
# cursor=conn.cursor()
# cursor.execute('select * from users')
# data=cursor.fetchall()
# print(data)