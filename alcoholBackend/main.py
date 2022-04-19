import json

import flask
from flask import Flask, request, jsonify

from connection import con_pool

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET', 'POST'])
def home():
    return "Hello"


@app.route('/questions', methods=['GET'])
def getquestions():
    if request.method == "GET":

        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "select q.id, q.question,u.username,q.upvotes,TIMESTAMPDIFF(hour,curtime(),q.created_at) as time," \
                    "count(c.comment) as comments from digitalhealth.questions q inner join digitalhealth.users u on " \
                    "q.user_id = u.id left join digitalhealth.comments c on q.id = c.question_id " \
                    "group by q.id,q.question,u.username,q.upvotes,q.created_at"

        cur.execute(sql_query)
        data = cur.fetchall()
        cur.close()
        db2.close()

        for d in data:
            if (abs(d[3]) >= 24):
                days = str(int(abs(d[3] / 24)))
                if (days == '1'):
                    time = days + ' day ago'
                else:
                    time = days + ' days ago'
            else:
                hours = str(abs(d[3]))
                time = hours + ' hours ago'

        json_data = []

        for d in data:
            json_data.append({"id": d[0], 'question': d[1], 'username': d[2], 'upvotes': d[3], 'comments': d[4], 'time': time})

        return jsonify(json_data)


@app.route('/getcomments', methods=['POST'])
def getcomments():
    if request.method == "POST":

        questionid = request.args.get('questionid', type=int)

        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "select c.comment,u.username,TIMESTAMPDIFF(hour,curtime(),c.created_at) from digitalhealth.comments c " \
                    "inner join digitalhealth.users u on c.user_id = u.id where c.question_id = %d;" % (
            questionid)

        cur.execute(sql_query)
        data = cur.fetchall()
        cur.close()
        db2.close()
        for d in data:
            if (abs(d[2]) >= 24):
                days = str(int(abs(d[2] / 24)))
                if (days == '1'):
                    time = days + ' day ago'
                else:
                    time = days + ' days ago'
            else:
                hours = str(abs(d[2]))
                time = hours + ' hours ago'
        print(data)
        json_data = []
        for d in data:
            json_data.append({'comment': d[0], 'username': d[1], 'time': time})

        print(json_data)
        return jsonify(json_data)


@app.route('/addquestion', methods=['POST'])
def addquestion():
    if request.method == "POST":

        question = request.args.get('question',type = str)
        user_id = request.args.get('userid',type = int)

        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "insert into digitalhealth.questions(question,user_id,upvotes,created_at) " \
                    "values('%s',%d,0,curtime())" % (question, user_id)
        cur.execute(sql_query)
        db2.commit()
        cur.close()
        db2.close()

        json_data = [{'status': "success"}]
        print(json_data)

        return jsonify(json_data)

@app.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        username = request.args.get('username', type=str)
        emailid = request.args.get('email', type=str)
        password = request.args.get('password', type=str)

        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "insert into digitalhealth.users(username,emailid,password) values('%s','%s','%s');" % (
            username, emailid, password)

        cur.execute(sql_query)
        db2.commit()

        query = "SELECT id, username, emailid FROM digitalhealth.users WHERE emailid = '%s'" % emailid
        cur.execute(query)
        data = cur.fetchone()
        json_data = []

        content = {'id': data[0], 'username': data[1], 'email': data[2], 'error': 'none'}
        json_data.append(content)

        # cur.close()
        # db2.close()

        print(json_data)

        return jsonify(json_data)

@app.route('/addcomment', methods=['POST'])
def addcomment():
    if request.method == "POST":

        question_id = request.args.get('questionid',type = int)
        comment = request.args.get('comment',type = str)
        user_id = request.args.get('userid',type = int)


        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "insert into digitalhealth.comments(question_id,comment,user_id,created_at) values(%d,'%s',%d,curtime())" % (question_id,comment,user_id)
        cur.execute(sql_query)
        db2.commit()
        cur.close()
        db2.close()

        json_data = [{'status': "success"}]
        print(json_data)

        return jsonify(json_data)

@app.route('/upvote', methods=['POST'])
def upvote():
    if request.method == "POST":

        question_id = request.args.get('questionid',type = int)


        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "update digitalhealth.questions set upvotes = upvotes+1 where id = %d" % (question_id)
        cur.execute(sql_query)
        db2.commit()
        cur.close()
        db2.close()

        json_data = [{'status': "success"}]
        print(json_data)

        return jsonify(json_data)

@app.route('/leaderboard', methods=['POST'])
def leaderboard():
    if request.method == "POST":

        db2 = con_pool.get_connection()
        cur = db2.cursor()
        sql_query = "with cte1 as (select u.id,u.username,count(distinct q.id) as questioncount from digitalhealth.questions q right join digitalhealth.users u on q.user_id = u.id group by u.id,u.username) ,cte2 as (select u.id,u.username,count(distinct c.id) as commentcount from digitalhealth.comments c right join digitalhealth.users u on c.user_id = u.id group by u.id,u.username) select c1.username,(c1.questioncount+c2.commentcount) as score from cte1 c1 inner join cte2 c2 on c1.id = c2.id order by score desc"
        cur.execute(sql_query)
        data = cur.fetchall()
        cur.close()
        db2.close()

        json_data = []
        for d in data:
            json_data.append({'username': d[0], 'score': d[1]})
        print(json_data)
        return jsonify(json_data)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
