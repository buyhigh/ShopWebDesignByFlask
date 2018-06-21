# -*- coding: UTF-8 -*-

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sys
import datetime

reload( sys )
sys.setdefaultencoding('utf-8')

DEBUG = True
SECRET_KEY = '8\x01\xa7Ry\xf6H\x8f^\xea\xd11\x7f\xc9\xa3\x88%\xf4\xae@\xd8\xd2!'

app = Flask(__name__)
app.config.from_object(__name__)

#######################################
###=========连接account============###
#######################################
def account_connect_db():
    connection = sqlite3.connect('d:/Project/shop-web-site-master_modify/database/account.db')
    connection.text_factory = str
    return connection

#######################################
###=========连接shopdata============###
#######################################
def shopdata_connect_db():
    connection = sqlite3.connect('d:/Project/shop-web-site-master_modify/database/shopdata.db')
    connection.text_factory = str
    return connection

#######################################
###=========连接profile============###
#######################################
def profile_connect_db():
    connection = sqlite3.connect('d:/Project/shop-web-site-master_modify/database/profile.db')
    connection.text_factory = str
    return connection

#######################################
###=========连接messageboard============###
#######################################
def massageboard_connect_db():
    connection = sqlite3.connect('d:/Project/shop-web-site-master_modify/database/messageboard.db')
    connection.text_factory = str
    return connection

#######################################
###=========钩子函数============###
#######################################
@app.before_first_request
def before_first_request():
    g.shop_db = shopdata_connect_db()

#######################################
###=========结束函数============###
#######################################
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'account_db'):
        g.account_db.close()
    if hasattr(g, 'shop_db'):
        g.shop_db.close()

#######################################
###=========/home相关函数============###
#######################################
@app.route('/')
@app.route('/home')
def home():
    try:
        username = session['username']
        g.profile_db = profile_connect_db()
        g.shop_db = shopdata_connect_db()
        cur = g.profile_db.execute('SELECT shopname, shopprice,cheapprice,place,shopid FROM preferentialgoods')
        cheapshopentries = [dict(shopname=row[0], shopprice=row[1], cheapprice=row[2], place=row[3], shopid=row[4]) for row in cur.fetchall()]

        cur = g.profile_db.execute('SELECT shopsname, advertiseword,id FROM homeadvertise')
        advertiseentries = [dict(shopsname=row[0], advertiseword=row[1], id=row[2]) for row in cur.fetchall()]

        cur = g.profile_db.execute('SELECT tag,enternum FROM tagrecord WHERE username = ? order by enternum desc limit 0,1',[username])
        tagrecordentry = cur.fetchone()
        if (tagrecordentry == None):#如果是为空的情况
            cur = g.shop_db.execute('select shopname, shopprice, shopstar, tag, id from shopdata order by shopstar desc limit 0,6')#如果是没有tag记录的情况下
            showperferentries = [dict(shopname=row[0], shopprice=row[1]*session['global_discount'],  shopstar=row[2], tag=row[3], id=row[4]) for row in cur.fetchall()]
            app.logger.debug("debug1")
        else:#已经获取到数据的时候
            if (len(tagrecordentry) < 6):#商品不足六个的时候
                cur = g.shop_db.execute('select shopname, shopprice, shopstar, tag, id from shopdata where tag = ? order by shopstar desc',[tagrecordentry[0]])  # 如果是没有tag记录的情况下
                showperferentries_1 = [dict(shopname=row[0], shopprice=row[1] * session['global_discount'], shopstar=row[2], tag=row[3],id=row[4]) for row in cur.fetchall()]
                cur = g.shop_db.execute('select shopname, shopprice, shopstar, tag, id from shopdata where tag <> ? order by shopstar desc limit 0,6',[tagrecordentry[0]])  # 如果是没有tag记录的情况下
                showperferentries_2 = [dict(shopname=row[0], shopprice=row[1] * session['global_discount'], shopstar=row[2], tag=row[3],id=row[4]) for row in cur.fetchall()]
                showperferentries = showperferentries_1 + showperferentries_2#将两个list合并
                app.logger.debug(showperferentries)
                app.logger.debug("debug2")
            else:#商品超过六个时候
                cur = g.shop_db.execute('select shopname, shopprice, shopstar, tag, id from shopdata where tag = ? order by shopstar desc limit 0,6',[tagrecordentry[1]])  # 如果是没有tag记录的情况下
                showperferentries = [dict(shopname=row[0], shopprice=row[1] * session['global_discount'], shopstar=row[2], tag=row[3],id=row[4]) for row in cur.fetchall()]
                app.logger.debug("debug3")

        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 1',[showperferentries[0]['shopname'], showperferentries[0]['shopprice'],
                              showperferentries[0]['id']])
        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 2',[showperferentries[1]['shopname'], showperferentries[1]['shopprice'],
                              showperferentries[1]['id']])
        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 3',[showperferentries[2]['shopname'], showperferentries[2]['shopprice'],
                              showperferentries[2]['id']])
        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 4',[showperferentries[3]['shopname'], showperferentries[3]['shopprice'],
                              showperferentries[3]['id']])
        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 5',[showperferentries[4]['shopname'], showperferentries[4]['shopprice'],
                              showperferentries[4]['id']])
        g.profile_db.execute('UPDATE predictlike SET shopname = ?,shopprice=?,shopid=? WHERE place LIKE 6',[showperferentries[5]['shopname'], showperferentries[5]['shopprice'],
                              showperferentries[5]['id']])
        g.profile_db.commit()

        cur = g.profile_db.execute('SELECT shopname, shopprice,place,shopid FROM predictlike')
        prefershopentries = [dict(shopname=row[0], shopprice=row[1], place=row[2], shopid=row[3]) for row in cur.fetchall()]
        return render_template('home.html',cheapshopentries=cheapshopentries,prefershopentries=prefershopentries,advertiseentries=advertiseentries)
    except:
        return redirect(url_for('signin'))

#######################################
###=========/about相关函数============###
#######################################
@app.route('/about')
def about():
    return render_template('about.html')

#######################################
###=========/contact相关函数============###
#######################################
@app.route('/contact')
def contact():
    return render_template('contact.html')

#######################################
###=========/contact相关函数============###
#######################################
@app.route('/contact_me')
def contact_me():
    return render_template('contact_me.html')

#######################################
###=========/entereditcheapplace相关函数============###
#######################################
@app.route('/entereditcheapplace')
def enter_editcheapplace():
    return render_template('editcheapplace.html')

#######################################
###=========/edit_cheapplace相关函数============###
#######################################
@app.route('/edit_cheapplace',methods=['post'])
def edit_cheapplace():
    g.shop_db = shopdata_connect_db()
    cur = g.shop_db.execute('select shopname, shopprice from shopdata where id = ?',[int(request.form['placeshopid'])])
    shopentry = cur.fetchone()
    g.profile_db = profile_connect_db()
    g.profile_db.execute('UPDATE preferentialgoods SET shopname = ?,shopprice=?,cheapprice=?,shopid=? WHERE place LIKE ?', [shopentry[0],int(request.form['placeprice']),int(request.form['placecheapprice'])
        ,int(request.form['placeshopid']),int(request.form['place'])])
    g.profile_db.commit()
    showinfotip = 'editcheapplace_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/addcontact相关函数============###
#######################################
@app.route('/addcontact', methods=['POST'])#别忘记声明提交的表单post方法
def add_contact():
    g.profile_db = profile_connect_db()
    g.account_db = account_connect_db()
    cur = g.profile_db.execute('SELECT username, shopsname,email FROM contactreview WHERE username LIKE ?',[request.form['selectname']])
    reviewentry = cur.fetchone()
    app.logger.debug(reviewentry)
    g.account_db.execute('insert into shopsaccount (name, shopsname,email) values (?,?,?)', [reviewentry[0], reviewentry[1] , reviewentry[2]])
    g.account_db.execute('UPDATE account SET shopsowner = ? WHERE username LIKE ?',[1, request.form['selectname']])
    g.account_db.commit()
    cur = g.profile_db.execute('DELETE FROM contactreview WHERE username LIKE ?',[request.form['selectname']])
    g.profile_db.commit()
    app.logger.debug(request.form['selectname'])
    return render_template('contact.html')

#######################################
###=========/contactreview相关函数============###
#######################################
@app.route('/contactreview', methods=['POST'])#别忘记声明提交的表单post方法
def contact_review():
    g.profile_db = profile_connect_db()
    g.profile_db.execute('insert into contactreview (username, shopsname,contactword,email) values (?,?,?,?)', [request.form['contactname'], request.form['contactshopsname'] ,request.form['contactword'], request.form['contactmail']])
    g.profile_db.commit()
    return render_template('contact.html')

#######################################
###=========/addmessage相关函数============###
#######################################
@app.route('/addmessage', methods=['POST'])#别忘记声明提交的表单post方法
def add_message():
    g.massageboard_db = massageboard_connect_db()
    g.massageboard_db.execute('insert into massageboard (name, massage,username,shopid) values (?,?,?,?)', [request.form['messagename'], request.form['message'], session['username'],session['now_shopid']])
    g.massageboard_db.commit()
    showinfotip = 'addmessage_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/profile相关函数============###
#######################################
@app.route('/profile',methods=['GET'])
def profile():
    g.profile_db = profile_connect_db()
    profile_showinfo=request.args.get('showinfo','')
    if profile_showinfo == 'personinfo':
        cur = g.profile_db.execute('SELECT name, Birthday, email, balance, sex,address  FROM user_profile WHERE name LIKE ?',[session['username']])
        userentries = [dict(username=row[0], Birthday=row[1], email=row[2], balance=row[3],sex=row[4],address=row[5]) for row in cur.fetchall()]
        return render_template('profile.html', userentries=userentries,showway='personinfo')
    elif profile_showinfo == 'buyinfo':
        if request.args.get('curpage', '') == '': 
            session['curbuyinfopage'] = 1
        cur = g.profile_db.execute(
            'SELECT shopname, salenum, buyer, money,datetime FROM shops_recordinfo WHERE buyer = ? ORDER BY id DESC ',[session['username']])
        buyentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], date_stamp=row[4]) for row in cur.fetchall()]

        total_buynum = len(buyentries)  # 全部信息数量
        if (total_buynum % 5 == 0):
            pagemax = total_buynum / 5  # 计算最大页数
        else:
            pagemax = total_buynum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':  # 下一页
            session['curbuyinfopage'] = session['curbuyinfopage'] + 1
            if session['curbuyinfopage'] >= pagemax:
                session['curbuyinfopage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':  # 上一页
            session['curbuyinfopage'] = session['curbuyinfopage'] - 1
            if session['curbuyinfopage'] <= 1:
                session['curbuyinfopage'] = 1
        elif request.args.get('curpage', '') == '1':  # 首页
            session['curbuyinfopage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
            session['curbuyinfopage'] = pagemax
        curpage = session['curbuyinfopage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_buynum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_buynum
        return render_template('profile.html', buyentries=buyentries, total_buynum=total_buynum,
                               curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange,
                               showway='buyinfo')
        #return render_template('profile.html', buyentries=buyentries,showway='buyinfo')
    elif profile_showinfo == 'confirmgoodsinfo':
        if request.args.get('curpage', '') == '':
            session['curconfirmgoodsinfopage'] = 1
        cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime,address,id FROM confirmgoodsreview WHERE buyer = ? order by id desc limit 0,5',
            [session['username']])
        confirmentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], date_stamp=row[4], address=row[5],buyid=row[6]) for row in cur.fetchall()]
        total_confirmnum = len(confirmentries)  # 全部信息数量
        if (total_confirmnum % 5 == 0):
            pagemax = total_confirmnum / 5  # 计算最大页数
        else:
            pagemax = total_confirmnum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':  # 下一页
            session['curconfirmgoodsinfopage'] = session['curconfirmgoodsinfopage'] + 1
            if session['curconfirmgoodsinfopage'] >= pagemax:
                session['curconfirmgoodsinfopage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':  # 上一页
            session['curconfirmgoodsinfopage'] = session['curconfirmgoodsinfopage'] - 1
            if session['curconfirmgoodsinfopage'] <= 1:
                session['curconfirmgoodsinfopage'] = 1
        elif request.args.get('curpage', '') == '1':  # 首页
            session['curconfirmgoodsinfopage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
            session['curconfirmgoodsinfopage'] = pagemax
        curpage = session['curconfirmgoodsinfopage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_confirmnum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_confirmnum
        return render_template('profile.html', confirmentries=confirmentries, total_confirmnum=total_confirmnum,
                               curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange,
                               showway='confirmgoodsinfo')
        #return render_template('profile.html', confirmentries=confirmentries, showway='confirmgoodsinfo')
    else:
        cur = g.profile_db.execute('SELECT name, Birthday, email, balance, sex,address  FROM user_profile WHERE name LIKE ?',[session['username']])
        userentries = [dict(username=row[0], Birthday=row[1], email=row[2], balance=row[3], sex=row[4], address=row[5]) for row in cur.fetchall()]
        return render_template('profile.html', userentries=userentries,showway='personinfo')

#######################################
###=========/sellercenter相关函数============###
#######################################
@app.route('/sellercenter',methods=['GET'])
def seller_center():
    g.profile_db = profile_connect_db()
    profile_showinfo=request.args.get('showinfo','')
    if profile_showinfo == 'shoporder':
        if request.args.get('curpage', '') == '':
            session['curshoporderpage'] = 1

        #cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime FROM shops_recordinfo WHERE shopowner = ? order by id desc limit 0,5',[session['username']])
        cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime FROM shops_recordinfo WHERE shopowner = ?',[session['username']])
        recordentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], date_stamp=row[4]) for row in cur.fetchall()]

        total_recordnum = len(recordentries)  # 全部信息数量
        if (total_recordnum % 5 == 0):
            pagemax = total_recordnum / 5  # 计算最大页数
        else:
            pagemax = total_recordnum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':#下一页
            session['curshoporderpage'] = session['curshoporderpage'] + 1
            if session['curshoporderpage'] >= pagemax:
                session['curshoporderpage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':#上一页
            session['curshoporderpage'] = session['curshoporderpage'] - 1
            if session['curshoporderpage'] <= 1:
                session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == '1':#首页
            session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):#最后一页
            session['curshoporderpage'] = pagemax
        curpage = session['curshoporderpage']
        app.logger.debug("debug1")
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_recordnum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_recordnum
        return render_template('sellercenter.html', recordentries=recordentries,total_recordnum=total_recordnum,
                               curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange,showway='shoporder')

    elif profile_showinfo == 'delivergoods':
        if request.args.get('curpage', '') == '':
            session['curdelivergoodspage'] = 1
        cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime,address,id FROM delivergoodsreview WHERE shopsowner = ? order by id desc limit 0,5',[session['username']])
        deliverentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], date_stamp=row[4],address=row[5],buyid=row[6]) for row in cur.fetchall()]
        total_delivernum = len(deliverentries)  # 全部信息数量
        if (total_delivernum % 5 == 0):
            pagemax = total_delivernum / 5  # 计算最大页数
        else:
            pagemax = total_delivernum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':  # 下一页
            session['curshoporderpage'] = session['curshoporderpage'] + 1
            if session['curshoporderpage'] >= pagemax:
                session['curshoporderpage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':  # 上一页
            session['curshoporderpage'] = session['curshoporderpage'] - 1
            if session['curshoporderpage'] <= 1:
                session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == '1':  # 首页
            session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
            session['curshoporderpage'] = pagemax
        curpage = session['curshoporderpage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_delivernum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_delivernum
        app.logger.debug("debug10")
        return render_template('sellercenter.html', deliverentries=deliverentries, total_delivernum=total_delivernum,curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange,
                               showway='delivergoods')
        #return render_template('sellercenter.html', deliverentries=deliverentries,showway='delivergoods')
    elif profile_showinfo == 'shopsmessage':
        if request.args.get('curpage', '') == '':
            session['curreplyshopsmessageinfopage'] = 1
        g.massageboard_db = massageboard_connect_db()
        cur = g.massageboard_db.execute('SELECT id, messageword,time,maker,reply FROM shopsmessage WHERE maker like ? order by id desc limit 0,5',[session['username']])
        messageentries = [dict(id=row[0], messageword=row[1], time=row[2], maker=row[3], reply=row[4]) for row in cur.fetchall()]
        app.logger.debug(messageentries)

        total_messagenum = len(messageentries)  # 全部信息数量
        if (total_messagenum % 5 == 0):
            pagemax = total_messagenum / 5  # 计算最大页数
        else:
            pagemax = total_messagenum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':  # 下一页
            session['curreplyshopsmessageinfopage'] = session['curreplyshopsmessageinfopage'] + 1
            if session['curreplyshopsmessageinfopage'] >= pagemax:
                session['curreplyshopsmessageinfopage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':  # 上一页
            session['curreplyshopsmessageinfopage'] = session['curreplyshopsmessageinfopage'] - 1
            if session['curreplyshopsmessageinfopage'] <= 1:
                session['curreplyshopsmessageinfopage'] = 1
        elif request.args.get('curpage', '') == '1':  # 首页
            session['curreplyshopsmessageinfopage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
            session['curreplyshopsmessageinfopage'] = pagemax
        curpage = session['curreplyshopsmessageinfopage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_messagenum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_messagenum
        return render_template('sellercenter.html', messageentries=messageentries,
                               total_messagenum=total_messagenum,
                               curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                               curendrange=curendrange,
                               showway='shopsmessage')
        #return render_template('sellercenter.html',messageentries=messageentries,showway='shopsmessage')
    else:
        if request.args.get('curpage', '') == '':
            session['curshoporderpage'] = 1
        # cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime FROM shops_recordinfo WHERE shopowner = ? order by id desc limit 0,5',[session['username']])
        cur = g.profile_db.execute(
            'SELECT shopname, salenum, buyer, money,datetime FROM shops_recordinfo WHERE shopowner = ?',
            [session['username']])
        recordentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], date_stamp=row[4]) for row in
                         cur.fetchall()]
        total_recordnum = len(recordentries)  # 全部信息数量
        if (total_recordnum % 5 == 0):
            pagemax = total_recordnum / 5  # 计算最大页数
        else:
            pagemax = total_recordnum / 5 + 1
        if request.args.get('curpage', '') == 'nextpage':  # 下一页
            session['curshoporderpage'] = session['curshoporderpage'] + 1
            if session['curshoporderpage'] >= pagemax:
                session['curshoporderpage'] = pagemax
        elif request.args.get('curpage', '') == 'prevpage':  # 上一页
            session['curshoporderpage'] = session['curshoporderpage'] - 1
            if session['curshoporderpage'] <= 1:
                session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == '1':  # 首页
            session['curshoporderpage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
            session['curshoporderpage'] = pagemax
        curpage = session['curshoporderpage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_recordnum - curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_recordnum
        return render_template('sellercenter.html', recordentries=recordentries, total_recordnum=total_recordnum,curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange,
                               showway='shoporder')

#######################################
###=========/savedeliver相关函数============###
#######################################
@app.route('/savedeliver',methods=['POST'])
def save_deliver():
    g.profile_db = profile_connect_db()
    deliverid=request.form['selectname']
    cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money,datetime,address,shopsowner FROM delivergoodsreview WHERE id = ? order by id desc limit 0,5',[deliverid])
    deliverentry = cur.fetchone()
    g.profile_db.execute('insert into confirmgoodsreview (shopname, salenum, buyer, money,datetime,address,shopsowner) values (?,?,?,?,?,?,?)',
                         [deliverentry[0], deliverentry[1], deliverentry[2],deliverentry[3],deliverentry[4],deliverentry[5],deliverentry[6]])
    g.profile_db.execute('DELETE FROM delivergoodsreview WHERE id LIKE ?', [deliverid])
    g.profile_db.commit()
    showinfotip = 'deliver_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/adminmanager相关函数============###
#######################################
@app.route('/adminmanager',methods=['GET'])
def admin_manager():
    if islogged() == False:
        return redirect(url_for('signin'))
    if session['admin_group']:
        g.profile_db = profile_connect_db()
        g.account_db = account_connect_db()
        profile_showinfo=request.args.get('showinfo','')
        if profile_showinfo == 'allshopinfo':
            if request.args.get('curpage', '') == '':
                session['curallshopinfopage'] = 1
            cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money, shopowner,datetime FROM shops_recordinfo  order by id desc ')
            allshopentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], shopowner=row[4], date_stamp=row[5]) for row in cur.fetchall()]

            total_allshopnum = len(allshopentries)  # 全部信息数量
            if (total_allshopnum % 5 == 0):
                pagemax = total_allshopnum / 5  # 计算最大页数
            else:
                pagemax = total_allshopnum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curallshopinfopage'] = session['curallshopinfopage'] + 1
                if session['curallshopinfopage'] >= pagemax:
                    session['curallshopinfopage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curallshopinfopage'] = session['curallshopinfopage'] - 1
                if session['curallshopinfopage'] <= 1:
                    session['curallshopinfopage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curallshopinfopage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curallshopinfopage'] = pagemax
            curpage = session['curallshopinfopage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_allshopnum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_allshopnum
            return render_template('adminmanager.html', allshopentries=allshopentries, total_allshopnum=total_allshopnum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='allshopinfo')
            #return render_template('adminmanager.html',allshopsentries=allshopsentries,showway='allshopinfo')
        elif profile_showinfo == 'shopappreview':
            if request.args.get('curpage', '') == '':
                session['curshopappreviewpage'] = 1
            cur = g.profile_db.execute('SELECT username,shopsname,contactword,email FROM contactreview  order by id desc ')
            reviewentries = [dict(username=row[0], shopsname=row[1], contactword=row[2], email=row[3]) for row in cur.fetchall()]

            total_reviewnum = len(reviewentries)  # 全部信息数量
            if (total_reviewnum % 5 == 0):
                pagemax = total_reviewnum / 5  # 计算最大页数
            else:
                pagemax = total_reviewnum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curshopappreviewpage'] = session['curshopappreviewpage'] + 1
                if session['curshopappreviewpage'] >= pagemax:
                    session['curshopappreviewpage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curshopappreviewpage'] = session['curshopappreviewpage'] - 1
                if session['curshopappreviewpage'] <= 1:
                    session['curshopappreviewpage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curshopappreviewpage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curshopappreviewpage'] = pagemax
            curpage = session['curshopappreviewpage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_reviewnum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_reviewnum
            return render_template('adminmanager.html', reviewentries=reviewentries, total_reviewnum=total_reviewnum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='shopappreview')
            #return render_template('adminmanager.html',reviewentries=reviewentries,showway='shopappreview')
        elif profile_showinfo == 'userinfo':
            if request.args.get('curpage', '') == '':
                session['curuserinfopage'] = 1
            cur = g.account_db.execute('SELECT username,admin,shopsowner,user,member FROM account  order by id desc ')
            accountentries = [dict(username=row[0], admin=row[1], shopsowner=row[2], user=row[3], member=row[4]) for row in cur.fetchall()]

            total_accountnum = len(accountentries)  # 全部信息数量
            if (total_accountnum % 5 == 0):
                pagemax = total_accountnum / 5  # 计算最大页数
            else:
                pagemax = total_accountnum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curuserinfopage'] = session['curuserinfopage'] + 1
                if session['curuserinfopage'] >= pagemax:
                    session['curuserinfopage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curuserinfopage'] = session['curuserinfopage'] - 1
                if session['curuserinfopage'] <= 1:
                    session['curuserinfopage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curuserinfopage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curuserinfopage'] = pagemax
            curpage = session['curuserinfopage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_accountnum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_accountnum
            return render_template('adminmanager.html', accountentries=accountentries, total_accountnum=total_accountnum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='userinfo')
            #return render_template('adminmanager.html',accountentries=accountentries,showway='userinfo')
        elif profile_showinfo == 'shopsownerinfo':
            if request.args.get('curpage', '') == '':
                session['curshopsownerinfopage'] = 1
            cur = g.account_db.execute('SELECT name,shopsname FROM shopsaccount  order by id desc ')
            shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]

            total_shopsnum = len(shopsentries)  # 全部信息数量
            if (total_shopsnum % 5 == 0):
                pagemax = total_shopsnum / 5  # 计算最大页数
            else:
                pagemax = total_shopsnum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curshopsownerinfopage'] = session['curshopsownerinfopage'] + 1
                if session['curshopsownerinfopage'] >= pagemax:
                    session['curshopsownerinfopage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curshopsownerinfopage'] = session['curshopsownerinfopage'] - 1
                if session['curshopsownerinfopage'] <= 1:
                    session['curshopsownerinfopage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curshopsownerinfopage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curshopsownerinfopage'] = pagemax
            curpage = session['curshopsownerinfopage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_shopsnum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_shopsnum
            return render_template('adminmanager.html', shopsentries=shopsentries, total_shopsnum=total_shopsnum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='shopsownerinfo')
            #return render_template('adminmanager.html',shopsentries=shopsentries,showway='shopsownerinfo')
        elif profile_showinfo == 'shopsmessage':
            if request.args.get('curpage', '') == '':
                session['curshopsmessageinfopage'] = 1
            g.massageboard_db = massageboard_connect_db()
            cur = g.massageboard_db.execute('SELECT id, messageword,time,maker,reply FROM shopsmessage order by id desc ')
            messageentries = [dict(id=row[0], messageword=row[1], time=row[2], maker=row[3], reply=row[4]) for row in cur.fetchall()]

            total_messagenum = len(messageentries)  # 全部信息数量
            if (total_messagenum % 5 == 0):
                pagemax = total_messagenum / 5  # 计算最大页数
            else:
                pagemax = total_messagenum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curshopsmessageinfopage'] = session['curshopsmessageinfopage'] + 1
                if session['curshopsmessageinfopage'] >= pagemax:
                    session['curshopsmessageinfopage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curshopsmessageinfopage'] = session['curshopsmessageinfopage'] - 1
                if session['curshopsmessageinfopage'] <= 1:
                    session['curshopsmessageinfopage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curshopsmessageinfopage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curshopsmessageinfopage'] = pagemax
            curpage = session['curshopsmessageinfopage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_messagenum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_messagenum
            return render_template('adminmanager.html', messageentries=messageentries,
                                   total_messagenum=total_messagenum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='shopsmessage')
            #return render_template('adminmanager.html',messageentries=messageentries, showway='shopsmessage')
        else:
            if request.args.get('curpage', '') == '':
                session['curallshopinfopage'] = 1
            cur = g.profile_db.execute('SELECT shopname, salenum, buyer, money, shopowner,datetime FROM shops_recordinfo  order by id desc limit 0,5')
            allshopentries = [dict(shopname=row[0], salenum=row[1], buyer=row[2], money=row[3], shopowner=row[4], date_stamp=row[5]) for row in cur.fetchall()]

            total_allshopnum = len(allshopentries)  # 全部信息数量
            if (total_allshopnum % 5 == 0):
                pagemax = total_allshopnum / 5  # 计算最大页数
            else:
                pagemax = total_allshopnum / 5 + 1
            if request.args.get('curpage', '') == 'nextpage':  # 下一页
                session['curallshopinfopage'] = session['curallshopinfopage'] + 1
                if session['curallshopinfopage'] >= pagemax:
                    session['curallshopinfopage'] = pagemax
            elif request.args.get('curpage', '') == 'prevpage':  # 上一页
                session['curallshopinfopage'] = session['curallshopinfopage'] - 1
                if session['curallshopinfopage'] <= 1:
                    session['curallshopinfopage'] = 1
            elif request.args.get('curpage', '') == '1':  # 首页
                session['curallshopinfopage'] = 1
            elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
                session['curallshopinfopage'] = pagemax
            curpage = session['curallshopinfopage']
            if (curpage == 1):
                curstartrange = 0
            else:
                curstartrange = 5 * (curpage - 2) + 5
            if (total_allshopnum - curstartrange > 5):
                curendrange = curstartrange + 5
            else:
                curendrange = total_allshopnum
            return render_template('adminmanager.html', allshopentries=allshopentries, total_allshopnum=total_allshopnum,
                                   curstartrange=curstartrange, curpage=curpage, pagemax=pagemax,
                                   curendrange=curendrange,
                                   showway='allshopinfo')
    else:
        showinfotip = 'adminmanager_no'
        return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/editprofile相关函数============###
#######################################
@app.route('/editprofile')
def editprofile():
    return render_template('editprofile.html')

#######################################
###=========/saveprofile相关函数============###
#######################################
@app.route('/saveprofile',methods=['POST'])
def saveprofile():
    g.profile_db = profile_connect_db()
    name=session['username']
    g.profile_db.execute('UPDATE user_profile SET Birthday = %s WHERE name LIKE ?' % (request.form['profilebirth']), [name])
    g.profile_db.execute('UPDATE user_profile SET email = ? WHERE name LIKE ?' ,[request.form['profilemail'], name])
    g.profile_db.execute('UPDATE user_profile SET sex = ? WHERE name LIKE ?', [request.form['profilesex'], name])
    g.profile_db.execute('UPDATE user_profile SET address = ? WHERE name LIKE ?', [request.form['profileaddress'], name])
    g.profile_db.commit()
    showinfotip = 'saveprofile'
    return render_template('infotippage.html',showinfotip=showinfotip)

#######################################
###=========/gonewshop相关函数============###
#######################################
@app.route('/gonewshop')#别忘记声明提交的表单post方法
def go_newshop():
    return render_template('createnewshop.html')

#######################################
###=========/createnewshop相关函数============###
#######################################
@app.route('/createnewshop', methods=['POST'])#别忘记声明提交的表单post方法
def create_newshop():
    g.shop_db = shopdata_connect_db()
    g.account_db = account_connect_db()
    cur = g.account_db.execute('SELECT shopsname FROM shopsaccount WHERE name LIKE ?', [session['username']])
    shopsname = cur.fetchone()
    cur = g.shop_db.execute('SELECT seq FROM sqlite_sequence')
    shopseq = cur.fetchone()
    g.shop_db.execute('insert into shopdata (shopname, shopprice,shopdes,shopstar,tag,owner,shopsname,shopid) values (?,?,?,?,?,?,?,?)',
                      [request.form['shopname'], int(request.form['shopprice']), request.form['shopintroduce'], int(request.form['shopstar']), request.form['shoptag'],session['username'],shopsname[0],int(shopseq[0])+1])
    g.shop_db.commit()
    showinfotip = 'createnewshop_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/goeditshop相关函数============###
#######################################
@app.route('/goeditshop')#别忘记声明提交的表单post方法
def go_editshop():
    if request.args.get('curpage', '') == '': 
        session['cureditshoppage'] = 1
    g.shop_db = shopdata_connect_db()
    cur = g.shop_db.execute('SELECT shopname,shopprice,shopdes,shopstar,tag,shopid FROM shopdata WHERE owner LIKE ?', [session['username']])
    shopentries = [dict(shopname=row[0], shopprice=row[1], shopdes=row[2], shopstar=row[3], tag=row[4], shopid=row[5]) for row in cur.fetchall()]

    total_shopnum = len(shopentries)  # 全部信息数量
    if (total_shopnum % 5 == 0):
        pagemax = total_shopnum / 5  # 计算最大页数
    else:
        pagemax = total_shopnum / 5 + 1
    if request.args.get('curpage', '') == 'nextpage':  # 下一页
        session['cureditshoppage'] = session['cureditshoppage'] + 1
        if session['cureditshoppage'] >= pagemax:
            session['cureditshoppage'] = pagemax
    elif request.args.get('curpage', '') == 'prevpage':  # 上一页
        session['cureditshoppage'] = session['cureditshoppage'] - 1
        if session['cureditshoppage'] <= 1:
            session['cureditshoppage'] = 1
    elif request.args.get('curpage', '') == '1':  # 首页
        session['cureditshoppage'] = 1
    elif request.args.get('curpage', '') == str(pagemax):  # 最后一页
        session['cureditshoppage'] = pagemax
    curpage = session['cureditshoppage']
    if (curpage == 1):
        curstartrange = 0
    else:
        curstartrange = 5 * (curpage - 2) + 5
    if (total_shopnum - curstartrange > 5):
        curendrange = curstartrange + 5
    else:
        curendrange = total_shopnum
    return render_template('edittheshop.html', shopentries=shopentries, total_shopnum=total_shopnum,
                           curstartrange=curstartrange, curpage=curpage, pagemax=pagemax, curendrange=curendrange)
    #return render_template('edittheshop.html',shopentries=shopentries)

#######################################
###=========/edittheshop相关函数============###
#######################################
@app.route('/edittheshop', methods=['POST'])#别忘记声明提交的表单post方法
def edit_theshop():
    g.shop_db = shopdata_connect_db()
    app.logger.debug(request.form['shopid'])
    g.shop_db.execute('UPDATE shopdata SET shopname=?, shopprice=?,shopdes=?,shopstar=?,tag=? WHERE shopid LIKE ?',
                      [request.form['shopname'], int(request.form['shopprice']), request.form['shopintroduce'], int(request.form['shopstar']), request.form['shoptag'],int(request.form['shopid'])])
    g.shop_db.commit()
    showinfotip = 'edittheshop_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/chargemoney相关函数============###
#######################################
@app.route('/chargemoney')
def charge_money():
    g.profile_db = profile_connect_db()
    cur = g.profile_db.execute('SELECT name, balance FROM user_profile WHERE name LIKE ?',[session['username']])
    chargeentries = [dict(username=row[0], balance=row[1]) for row in cur.fetchall()]
    return render_template('chargemoney.html',chargeentries=chargeentries)

#######################################
###=========/addcharge相关函数============###
#######################################
@app.route('/addcharge', methods=['POST'])
def add_charge():
    g.profile_db = profile_connect_db()
    chargename = "".join(request.form['chargename'])
    cur = g.profile_db.execute('SELECT name, balance FROM user_profile WHERE name LIKE ?' ,[chargename])
    OLD_entry = cur.fetchone()
    if (OLD_entry == None):
        showinfotip = 'addcharge_no'
        return render_template('infotippage.html', showinfotip=showinfotip)
    else:
        add_balance=request.form['chargenum']
        add_balance = "".join(add_balance)
        new_balance=int(add_balance)+OLD_entry[1]
        g.profile_db.execute('UPDATE user_profile SET balance = %s WHERE name LIKE ?' %(new_balance),[chargename])
        g.profile_db.commit()
        #cur = g.profile_db.execute('SELECT name, Birthday, email, balance FROM user_profile WHERE name LIKE "test"')
        #userentries = [dict(username=row[0], Birthday=row[1], email=row[2], balance=row[3]) for row in cur.fetchall()]
        showinfotip = 'addcharge_yes'
        return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/shop相关函数============###
#######################################
@app.route('/shop')
def shop():
    g.shop_db = shopdata_connect_db()
    g.account_db = account_connect_db()
    sort = str(request.args.get('sort',''))
    showcategory = str(request.args.get('showcategory', ''))
    app.logger.debug(showcategory)
    if (sort is None or sort is "") and (showcategory is None or showcategory is ""):
        cur = g.shop_db.execute('select shopname, shopprice, shopstar from shopdata order by id')
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        app.logger.debug('所有get为空')
        return render_template('shop.html', entries=entries,shopsentries=shopsentries)
    elif sort == 'shopstar':
        cur = g.shop_db.execute('select shopname, shopprice, shopstar from shopdata order by shopstar desc')
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries,shopsentries=shopsentries)
    elif sort == 'shopname':
        cur = g.shop_db.execute('select shopname, shopprice, shopstar from shopdata order by shopname')
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries,shopsentries=shopsentries)
    elif sort == 'shopprice':
        cur = g.shop_db.execute('select shopname, shopprice, shopstar from shopdata order by shopprice')
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries,shopsentries=shopsentries)
    elif showcategory == 'all':
        cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata ORDER BY shopstar DESC')
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1] * row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries, shopsentries=shopsentries)
    elif showcategory == 'clothes':
        showcategory = '%' + showcategory + '%'
        cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata WHERE category LIKE ? ORDER BY shopstar DESC',[showcategory])
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1] * row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries, shopsentries=shopsentries)
    elif showcategory == 'trousers':
        showcategory = '%' + showcategory + '%'
        cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata WHERE category LIKE ? ORDER BY shopstar DESC',[showcategory])
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1] * row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries, shopsentries=shopsentries)
    elif showcategory == 'sweater':
        showcategory = '%' + showcategory + '%'
        cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata WHERE category LIKE ? ORDER BY shopstar DESC',[showcategory])
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1] * row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries, shopsentries=shopsentries)
    elif showcategory == 'books':
        showcategory = '%' + showcategory + '%'
        cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata WHERE category LIKE ? ORDER BY shopstar DESC',[showcategory])
        entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1] * row[2]) for row in cur.fetchall()]
        cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
        shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
        return render_template('shop.html', entries=entries, shopsentries=shopsentries)
    else:
        return "error input!"

#######################################
###=========/entershops相关函数============###
#######################################
@app.route('/entershops')
def entershops():
    g.shop_db = shopdata_connect_db()
    g.account_db = account_connect_db()
    shopsname = str(request.args.get('shopsname',''))
    cur = g.shop_db.execute('SELECT shopname, shopprice, shopstar FROM shopdata WHERE shopsname LIKE ?',[shopsname])
    entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
    cur = g.account_db.execute('select name, shopsname from shopsaccount order by id')
    shopsentries = [dict(username=row[0], shopsname=row[1]) for row in cur.fetchall()]
    return render_template('shop.html', entries=entries,shopsentries=shopsentries)

#######################################
###=========/register相关函数============###
#######################################
@app.route('/register')
def register():
    return render_template('register.html')

#######################################
###=========/addaccount相关函数============###
#######################################
@app.route('/addaccount', methods=['POST'])
def add_account():
    g.account_db = account_connect_db()
    g.account_db.execute('insert into account (username, password,admin,shopsowner,user) values (?,?,?,?,?)', [request.form['username'], request.form['password'],0,0,1])
    g.account_db.commit()
    session['username'] = request.form['username']
    session['logged_in'] = True
    g.profile_db = profile_connect_db()
    g.profile_db.execute('insert into user_profile (name, Birthday , email,balance) values (?,?,?,?)',[session['username'],0,"",0])
    g.profile_db.commit()
    session['user_group'] = True
    session['admin_group'] = False
    session['shopsowner_group'] = False
    session['member_group'] = False
    session['global_discount'] = 1
    showinfotip = 'addaccount_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/addmember相关函数============###
#######################################
@app.route('/addmember')
def add_member():
    g.account_db = account_connect_db()
    g.account_db.execute('UPDATE account SET member = 1 WHERE username LIKE ?', [session['username']])
    g.account_db.commit()
    session['member_group'] = True
    session['global_discount'] = 0.9
    showinfotip = 'addmember_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/search相关函数============###
#######################################
@app.route('/search', methods=['GET'])
def search():
    g.shop_db = shopdata_connect_db()
    searchword = request.args.get('tag','')
    searchword = '%' + searchword + '%'
    cur = g.shop_db.execute('select shopname, shopprice, shopstar from shopdata where shopname LIKE ?', [searchword])
    entries = [dict(shopname=row[0], shopprice=row[1], shopstar=[1]*row[2]) for row in cur.fetchall()]
    return render_template('shop.html', entries=entries, search=searchword)

#######################################
###=========/shopmessage相关函数============###
#######################################
@app.route('/shopmessage', methods=['GET'])
def shopmessage():
    if islogged():
        g.shop_db = shopdata_connect_db()
        if request.args.get('shopname','') == '':
            shopname = session['curshowshopname']
        else:
            session['curshowshopname']=request.args.get('shopname', '')
            shopname = session['curshowshopname']
            session['curmessagepage']=1
        cur = g.shop_db.execute('select shopname, shopprice, shopdes, shopstar, tag, id from shopdata where shopname = ?', [shopname])
        entries = [dict(shopname=row[0], shopprice=row[1]*session['global_discount'], shopdes=row[2], shopstar=[1]*row[3], tag=row[4], id=row[5]) for row in cur.fetchall()]
        cur = g.shop_db.execute('select shopname, shopprice, shopdes, shopstar, tag, id from shopdata where shopname = ?', [shopname])
        temp_entry = cur.fetchone()
        cur = g.shop_db.execute('select id from shopdata where shopname = ?',[shopname])
        shop_one = cur.fetchone()
        session['now_shopid'] = shop_one[0]
        app.logger.debug(temp_entry[4])
        username = session['username']
        g.profile_db = profile_connect_db()
        cur = g.profile_db.execute('select enternum from tagrecord where tag = ? and username = ?',[temp_entry[4],username])
        record_exist = cur.fetchone()
        if (record_exist == None):
            cur = g.profile_db.execute('insert into tagrecord (username, tag, enternum) values (?,?,?)',[username, temp_entry[4], 1])
        else:
            new_enternum = record_exist[0] + 1
            g.profile_db.execute('update tagrecord set enternum = ? where tag = ? and username = ?', [new_enternum, temp_entry[4] ,username])
        g.profile_db.commit()

        g.massageboard_db = massageboard_connect_db()
        cur = g.massageboard_db.execute('select name,massage,username,shopid from massageboard where shopid = ?', [session['now_shopid']])#留言板信息
        messageentries = [dict(messagename=row[0], message=row[1], username=row[2]) for row in cur.fetchall()]
        total_messagenum=len(messageentries) #全部信息数量
        if (total_messagenum % 5 == 0):
            pagemax = total_messagenum / 5 #计算最大页数
        else:
            pagemax = total_messagenum / 5 + 1
        if request.args.get('curpage','') == 'nextpage':
            session['curmessagepage']=session['curmessagepage']+1
            if session['curmessagepage'] >= pagemax:
                session['curmessagepage'] = pagemax
        elif request.args.get('curpage','') == 'prevpage':
            session['curmessagepage'] = session['curmessagepage']-1
            if session['curmessagepage'] <= 1:
                session['curmessagepage'] = 1
        elif request.args.get('curpage','') == '1':
            session['curmessagepage'] = 1
        elif request.args.get('curpage', '') == str(pagemax):
            session['curmessagepage'] = pagemax
        curpage = session['curmessagepage']
        if (curpage == 1):
            curstartrange = 0
        else:
            curstartrange = 5 * (curpage - 2) + 5
        if (total_messagenum- curstartrange > 5):
            curendrange = curstartrange + 5
        else:
            curendrange = total_messagenum
        return render_template('shopmessage.html', entries=entries,messageentries=messageentries,total_messagenum=total_messagenum,
                               curstartrange=curstartrange,curpage=curpage,pagemax=pagemax,curendrange=curendrange)
    else:
        return redirect(url_for('signin'))

    
#######################################
###=========用于购物车商品结算为具体金额============###
#######################################
'''
a function to change sql data to shopcart data.
eg.
    "2:1##3:2"      -->     {"2":1, "3":2}
            ""      -->     {}
'''
def SQLtocart(sqldata=""):
    if sqldata == '':
        return {}
    else:
        tmp = sqldata.split("##")
        result = {}
        for i in tmp:
            i = i.split(':')
            result[i[0]] = int(i[1])
        return result

#######################################
###=========用于购物车商品结算为数据库保存============###
#######################################
'''
a function to change shopcart data to sql data.
eg.
    {"2":1, "3":2}      -->     "2:1##3:2"
                {}      -->     ""   
'''
def CARTtoSQL(cart=""):
    if len(cart) == 0:
        return ""
    else:
        tmp = []
        for i in cart:
            string = i + ':' + str(cart[i])
            tmp.append(string)
        return '##'.join(tmp)

'''
get the total price of the shopcart of the current user through session attr.
'''
#######################################
###=========获取购物车里金额============###
#######################################
def getprice():
    if islogged():
        g.account_db = account_connect_db()
        g.shop_db = shopdata_connect_db()
        shopprice = 0
        username = session['username']
        cur = g.account_db.execute('select shopcart from account where username = ?', [username])
        result = cur.fetchone()
        shopcart = result[0]
        shopcart = SQLtocart(shopcart)
        if len(shopcart) == 0: return 0
        for i in shopcart:
            cur = g.shop_db.execute('select shopprice from shopdata where id = ?', [i])
            shopprice += cur.fetchone()[0] * shopcart[i]
        return shopprice

#######################################
###=========刷新购物车============###
#######################################
def updatecart(cart):
    if islogged():
        g.account_db = account_connect_db()
        g.shop_db = shopdata_connect_db()
        username = session['username']
        cur = g.account_db.execute('select shopcart from account where username = ?', [username])
        result = cur.fetchone()
        shopcart = result[0]
        shopcart = SQLtocart(shopcart)
        cart = SQLtocart(cart)
        if len(shopcart) == 0: shopcart = CARTtoSQL(cart)
        else:
            for i in cart:
                if i in shopcart:
                    shopcart[i] += int(cart[i])
                else:
                    shopcart[i] = int(cart[i])
            shopcart = CARTtoSQL(shopcart)
        g.account_db.execute('update account set shopcart = ? where username = ?', [shopcart, session['username']])
        g.account_db.commit()
        session['total'] = getprice() * session['global_discount']
        
#######################################
###=========添加商品============###
#######################################
@app.route('/addshop', methods=['POST'])
def addshop():
    id = request.form['id']
    num = request.form['quantity']
    tmp = str(id) + ':' + str(num)
    updatecart(tmp)
    return redirect(url_for('shopmanager'))

#######################################
###=========删除商品============###
#######################################
@app.route('/deleteshop', methods=['GET'])
def deleteshop():
    if islogged():
        g.account_db = account_connect_db()
        g.shop_db = shopdata_connect_db()
        shopid = request.args.get('shopid','')
        
        username = session['username']
        cur = g.account_db.execute('select shopcart from account where username = ?', [username])
        result = cur.fetchone()
        shopcart = result[0]
        shopcart = SQLtocart(shopcart)
        print "shopid:",shopid,type(shopid)
        print "shopcart:",shopcart,type(shopcart)
        del shopcart[str(shopid)] #删除快捷命令？
        shopcart = CARTtoSQL(shopcart)
        g.account_db.execute('update account set shopcart = ? where username = ?', [shopcart, session['username']])
        g.account_db.commit()
        session['total'] = getprice()
        return redirect(url_for('shopmanager'))
    else:
        return redirect(url_for('signin'))


#######################################
###=========/shopmanager相关函数============###
#######################################
@app.route('/shopmanager')
def shopmanager():
    if islogged():
        g.account_db = account_connect_db()
        g.shop_db = shopdata_connect_db()
        entries = []
        username = session['username']
        cur = g.account_db.execute('select shopcart from account where username = ?', [username])
        result = cur.fetchone()
        shopcart = result[0]
        shopcart = SQLtocart(shopcart)
        length = len(shopcart)
        if length == 0: entries = []
        else:
            count = 1
            for i in shopcart:
                cur = g.shop_db.execute('select shopname, shopprice from shopdata where id = ?', [i])
                result = cur.fetchall()
                for row in result:
                    entries.append(dict(orderid=count, shopname=row[0], shopprice=row[1] * session['global_discount'], shopquantity=shopcart[i], entryprice=shopcart[i] * row[1], shopid=i))
                count += 1
        return render_template('shopmanager.html', entries=entries, number=length)
    else:
        return redirect(url_for('signin'))

#######################################
###=========/checkout相关函数============###
#######################################
# @app.route('/checkout')
# def check_out():
#     g.profile_db = profile_connect_db()
#     g.account_db = account_connect_db()
#     g.shop_db = shopdata_connect_db()
#     username = session['username']
#     #将购物车数据转换成字典进行遍历
#     shopprice=0
#     cur = g.account_db.execute('select shopcart from account where username = ?', [username])
#     result = cur.fetchone()
#     shopcart = result[0]
#     # print(str(shopcart))
#     shopcart = SQLtocart(shopcart)
#     if len(shopcart) == 0:
#         showinfotip = 'checkout_cartless'
#         return render_template('infotippage.html', showinfotip=showinfotip)
#     for i in shopcart:
#         time_stamp = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
#         cur = g.shop_db.execute('select shopprice,owner,shopname from shopdata where id = ?', [i])
#         record_result = cur.fetchone()
#         shopprice = record_result[0] * shopcart[i] * session['global_discount']
#         g.profile_db.execute('insert into shops_recordinfo (shopname, salenum, buyer, money, shopowner,datetime) values (?,?,?,?,?,?)', [record_result[2], shopcart[i], username, shopprice, record_result[1],time_stamp])
#         cur = g.profile_db.execute('SELECT balance FROM user_profile WHERE name LIKE ?', [record_result[1]])
#         old_balance = cur.fetchone()
#         new_balance = old_balance[0] + shopprice * session['global_discount']
#         g.profile_db.execute('UPDATE user_profile SET balance = %s WHERE name LIKE ?' % (new_balance), [record_result[1]])
#         g.profile_db.commit()
#     #结算
#     carprice=getprice()
#     cur = g.profile_db.execute('SELECT balance FROM user_profile WHERE name LIKE ?', [username])
#     OLD_entry = cur.fetchone()
#     if (OLD_entry[0] >= carprice):
#         new_balance = OLD_entry[0] - carprice*session['global_discount']
#         g.profile_db.execute('UPDATE user_profile SET balance = %s WHERE name LIKE ?' % (new_balance), [username])
#         g.profile_db.commit()
#         shopcart=""
#         g.account_db.execute('update account set shopcart = ? where username = ?', [shopcart, session['username']])
#         g.account_db.commit()
#         session['total'] = 0
#         showinfotip = 'checkout_yes'
#         return render_template('infotippage.html', showinfotip=showinfotip)
#     else:
#         showinfotip = 'checkout_moneyless'
#         return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/checkout相关函数============###
#######################################
@app.route('/checkout')
def check_out():
    g.profile_db = profile_connect_db()
    g.account_db = account_connect_db()
    g.shop_db = shopdata_connect_db()
    username = session['username']
    shopprice = 0
    cur = g.account_db.execute('select shopcart from account where username = ?', [username])#获取购物车
    result = cur.fetchone()
    shopcart = result[0]
    shopcart = SQLtocart(shopcart)
    if len(shopcart) == 0:
        showinfotip = 'checkout_cartless'
        return render_template('infotippage.html', showinfotip=showinfotip)
    carprice = getprice()
    cur = g.profile_db.execute('SELECT balance,address FROM user_profile WHERE name LIKE ?', [username])#获取用户钱包
    OLD_entry = cur.fetchone()
    if (OLD_entry[0] >= carprice):
        for i in shopcart:
            time_stamp = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            cur = g.shop_db.execute('select shopprice,owner,shopname from shopdata where id = ?', [i])
            record_result = cur.fetchone()
            shopprice = record_result[0] * shopcart[i] * session['global_discount']
            g.profile_db.execute('insert into shops_recordinfo (shopname, salenum, buyer, money, shopowner,datetime) values (?,?,?,?,?,?)',[record_result[2], shopcart[i], username, shopprice, record_result[1], time_stamp])
            g.profile_db.execute('insert into delivergoodsreview (shopname, salenum, buyer, money, shopsowner,datetime,address) values (?,?,?,?,?,?,?)',[record_result[2], shopcart[i], username, shopprice, record_result[1], time_stamp,OLD_entry[1]])
            g.profile_db.commit()
        shopcart = ""
        g.account_db.execute('update account set shopcart = ? where username = ?', [shopcart, session['username']])
        g.account_db.commit()
        session['total'] = 0
        showinfotip = 'checkout_yes'
        return render_template('infotippage.html', showinfotip=showinfotip)
    else:
        showinfotip = 'checkout_moneyless'
        return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/confirmreceive相关函数============###
#######################################
@app.route('/confirmreceive',methods=['POST'])
def confirm_receive():
    g.profile_db = profile_connect_db()
    cur = g.profile_db.execute('SELECT buyer,shopsowner, money FROM confirmgoodsreview WHERE id = ?',[request.form['selectname']])
    confirmentry = cur.fetchone()
    cur = g.profile_db.execute('SELECT balance FROM user_profile WHERE name LIKE ?', [confirmentry[0]])  # 获取用户钱包
    buyerentry = cur.fetchone()
    cur = g.profile_db.execute('SELECT balance FROM user_profile WHERE name LIKE ?', [confirmentry[1]])  # 获取用户钱包
    shopsownerentry = cur.fetchone()
    app.logger.debug(str(buyerentry[0])+"   "+str(confirmentry[2]))
    if (buyerentry[0] > confirmentry[2]):
        buyernewblance=buyerentry[0]-confirmentry[2]
        shopsownernewblance=shopsownerentry[0]+confirmentry[2]
        g.profile_db.execute('UPDATE user_profile SET balance = %s WHERE name LIKE ?' % (buyernewblance), [confirmentry[0]])
        g.profile_db.execute('UPDATE user_profile SET balance = %s WHERE name LIKE ?' % (shopsownernewblance), [confirmentry[1]])
        g.profile_db.execute('DELETE FROM confirmgoodsreview WHERE id LIKE ?', [request.form['selectname']])
        g.profile_db.commit()
        showinfotip='receive_yes'
        return render_template('infotippage.html', showinfotip=showinfotip)
    else:
        showinfotip = 'receive_no'
        return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/directpurchase相关函数============###
#######################################
@app.route('/directpurchase',methods=['POST'])
def direct_purchase():
    id = request.form['id']
    num = request.form['quantity']
    username = session['username']
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    g.shop_db = shopdata_connect_db()
    g.profile_db = profile_connect_db()
    cur = g.shop_db.execute('SELECT shopname,shopprice, owner,shopsname FROM shopdata WHERE id = ?',[id])
    shopentry = cur.fetchone()
    needmoney = shopentry[1] * float(num) * session['global_discount']
    cur = g.profile_db.execute('SELECT balance,address FROM user_profile WHERE name LIKE ?', [username])  # 获取用户钱包
    buyerentry = cur.fetchone()
    app.logger.debug(str(buyerentry[0])+"   "+str(needmoney))
    app.logger.debug(str(shopentry[1]) + "   " + str(num))
    if (buyerentry[0] > needmoney):
        g.profile_db.execute('insert into shops_recordinfo (shopname, salenum, buyer, money, shopowner,datetime) values (?,?,?,?,?,?)',
                             [shopentry[0], int(num), username, needmoney, shopentry[2], time_stamp])
        g.profile_db.execute('insert into delivergoodsreview (shopname, salenum, buyer, money, shopsowner,datetime,address) values (?,?,?,?,?,?,?)',
                             [shopentry[0], int(num), username, needmoney, shopentry[2], time_stamp, buyerentry[1]])
        g.profile_db.commit()
        showinfotip = 'checkout_yes'
        return render_template('infotippage.html', showinfotip=showinfotip)
    else:
        showinfotip = 'checkout_moneyless'
        return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/addshopsmessage相关函数============###
#######################################
@app.route('/addshopsmessage', methods=['POST'])#别忘记声明提交的表单post方法
def add_shopsmessage():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    g.massageboard_db = massageboard_connect_db()
    g.massageboard_db.execute('insert into shopsmessage (messagetitle, messageword,time,maker) values (?,?,?,?)', [request.form['messagetitle'], request.form['messageword'], time_stamp,session['username']])
    g.massageboard_db.commit()
    showinfotip = 'addmessage_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========/replyshopsmessage相关函数============###
#######################################
@app.route('/replyshopsmessage', methods=['POST'])#别忘记声明提交的表单post方法
def reply_shopsmessage():
    g.massageboard_db = massageboard_connect_db()
    g.massageboard_db.execute('UPDATE shopsmessage SET reply = ? WHERE id LIKE ?',[request.form['reply'], request.form['messageid']])
    #g.massageboard_db.execute('insert into shopsmessage (messagetitle, messageword,time,maker) values (?,?,?,?)', [request.form['messagetitle'], request.form['messageword'], time_stamp,session['username']])
    g.massageboard_db.commit()
    showinfotip = 'addmessage_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)

#######################################
###=========检测是否登录============###
#######################################
def islogged():
    if 'logged_in' in session and session['logged_in']:
        return True
    else:
        return False

#######################################
###=========/signin相关函数============###
#######################################
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        g.account_db = account_connect_db()
        username = request.form['username']
        password = request.form['password']
        cur = g.account_db.execute('select password,admin,shopsowner,user,member from account where username = ?', [username])
        result = cur.fetchone()
        if result == None:
            return render_template('signin.html', error="No such user!")
        if (str(password) == str(result[0])):
            session['logged_in'] = True
            session['username'] = username
            session['total'] = getprice()
            session['user_group'] = True
            if (result[1]==1):
                session['admin_group'] = True
            else:
                session['admin_group'] = False
            if (result[2]==1):
                session['shopsowner_group'] = True
            else:
                session['shopsowner_group'] = False
            if (result[4]==1):
                session['member_group'] = True
                session['global_discount'] = 0.9
            else:
                session['member_group'] = False
                session['global_discount'] = 1
            showinfotip = 'signin_yes'
            return render_template('infotippage.html', showinfotip=showinfotip)
        else:
            return render_template('signin.html', error="Wrong password!")
    else:
        return render_template('signin.html')

#######################################
###=========/signout相关函数============###
#######################################
@app.route('/signout')
def signout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
    if 'username' in session:
        session.pop('username', None)
    if 'total' in session:
        session.pop('total', None)
    showinfotip = 'signout_yes'
    return render_template('infotippage.html', showinfotip=showinfotip)
    
if __name__ == '__main__':
    app.run(host='127.0.0.1')
