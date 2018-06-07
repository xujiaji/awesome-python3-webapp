#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jiaji Xu'

' url handlers '

from aiohttp import web
import re, time, hashlib, json, logging, send_email
from coroweb import get, post
from apis import Page, APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from models import User, Comment, Blog, next_id, Reply
from config import configs
import markdown2

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    """
    Generate cookie str by user.
    用户生成cookie字符串
    """
    # build cookie string by: id-expires-sha1
    # 通过id-expires-sha1构建cookie字符串
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


async def cookie2user(cookie_str):
    """
    Parse cookie and load user if cookie is valid.
    如果cookie有效则解析cookie并加载用户
    """
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


# @get('/')
# async def index(request):
#     users = await User.findAll()
#     return {
#         '__template__': 'test.html',
#         'users': users
#     }

@get('/')
async def index(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    page = Page(num)
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs
    }


@get('/blog/{id}')
async def get_blog(id):
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = markdown2.markdown(c.content)
        c.replies = await Reply.findAll('comment_id=?', [c.id], orderBy='created_at desc')
        for reply in c.replies:
            reply.html_content = markdown2.markdown(reply.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/manage/users')  # manage all users
async def manage_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    page = Page(num, page_index)
    if page_index > page.page_count:
        page_index = page_index - 1
    return {
        '__template__': 'manage_users.html',
        'page_index': page_index,
        'page_count': page.page_count,
        'item_count': page.item_count
    }


@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for comment in comments:
        # 找对应的文章
        id = comment.blog_id
        blog = await Blog.find(id)
        if blog:
            comment['blog_name'] = blog.name
        else:
            comment['blog_name'] = '该文章已删除'
    return dict(page=p, comments=comments)


@get('/email_confirm')
async def confirm_email(*, token=None):
    users = None
    if token is not None:
        users = await User.findAll('confirm=?', [token])
    if users is not None and len(users) == 1 and users[0].confirm == token:
        user = users[0]
        user.status = 1
        user.confirm = None
        await user.update()
        return {
            '__template__': 'email_confirm.html',
            '__user__': user
        }
    return {
        '__template__': 'email_confirm.html'
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@get('/manage/')
def manage():
    return 'redirect:/manage/comments'


@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }


@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }


@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@post('/api/comment/reply')
async def api_create_reply(request, *, blog_id, comment_id, content, reply_user_id):
    user = request.__user__
    if user is None:
        raise APIPermissionError('请先登录哦！(Please signin first.)')
    if not content or not content.strip():
        raise APIValueError('content')
    reply_user = await User.find(reply_user_id)
    if reply_user is None:
        raise APIPermissionError('您回复的账号不存在！')
    send_email.send_comment_email(reply_user.email, content, '/blog/%s' % blog_id)
    reply = Reply(comment_id=comment_id,
                  user_id=user.id,
                  reply_user_id=reply_user_id,
                  user_name=user.name,
                  user_image=user.image,
                  content=content)
    await reply.save()
    return reply


@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('请先登录哦！(Please signin first.)')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = await Blog.find(id)
    blog_user = await User.find(blog.user_id)
    send_email.send_comment_email(blog_user.email, content, '/blog/%s' % id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image,
                      content=content.strip())
    await comment.save()
    return comment


@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
    check_admin(request)
    c = await Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    await c.remove()
    return dict(id=id)


@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '*******'
    return dict(users=users)


@post('/api/users/{id}/delete')  # api for deleting an user
async def api_delete_users(id, request):
    check_admin(request)
    id_buff = id
    user = await User.find(id)
    if user is None:
        raise APIResourceNotFoundError('Comment')
    await user.remove()
    # 给被删除的用户在评论中标记
    comments = await Comment.findAll('user_id=?', [id])
    if comments:
        for comment in comments:
            id = comment.id
            c = await Comment.find(id)
            c.user_name = c.user_name + ' (该用户已被删除)'
            await c.update()
    id = id_buff
    return dict(id=id)


_RE_EMAIL = re.compile(r'^[a-z0-9.\-_]+@[a-z0-9\-_]+(\.[a-z0-9\-_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('注册:失败', 'email', '该邮箱已注册！')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(
        id=uid,
        name=name.strip(),
        email=email,
        passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
        image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest(),
        confirm=hashlib.md5(sha1_passwd.encode('utf-8')).hexdigest())
    await user.save()
    send_email.send_confirm_account(email, user.confirm)
    # make session cookie / 创建会话cookie
    # r = web.Response()
    # r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # user.passwd = '******'
    # r.content_type = 'application/json'
    # r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    # return r
    return {}


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', '无效邮箱.')
    if not passwd:
        raise APIValueError('passwd', '无效密码.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', '邮箱不存在！')
    user = users[0]
    if user.status == 0:
        raise APIError('登录失败', 'status', '该邮箱没有完成认证')
    # 检测密码
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', '密码错误!')
    # 设置Cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('用户已登出.')
    return r


@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog


@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', '名字不能为空。')
    if not summary or not summary.strip():
        raise APIValueError('summary', '概要不能为空。')
    if not content or not content.strip():
        raise APIValueError('content', '内容不能为空。')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog


@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    await blog.update()
    return blog


@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return dict(id=id)
