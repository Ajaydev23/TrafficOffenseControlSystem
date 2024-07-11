from flask import Flask, render_template, request, redirect,session
from DBConnection import Db
import datetime
import random


import os
from flask import *
import smtplib
from email.mime.text import MIMEText
from flask_mail import *

app = Flask(__name__)
app.secret_key="trafic"

# main_path="E:\\PycharmProjects\\hemet\\static\\user\\"
# main_path1="E:\\PycharmProjects\\hemet\\static\\trafficpolice\\"

main_path="C:\\Users\\hp\\PycharmProjects\\hemet\\static\\user\\"
main_path1="C:\\Users\\hp\\PycharmProjects\\hemet\\static\\trafficpolice\\"

@app.route('/logout')
def logout():
    session["lo"]=""
    return render_template("login.html")


@app.route('/forget_pswd')
def forget_pswd():
    return render_template("forgot_pswd.html")

@app.route('/forget_pswd1',methods=['post'])
def forget_pswd1():
    db=Db()
    mail=request.form['textfield']
    qry=db.selectOne("select * from login where username='"+mail+"'")
    res=qry['password']
    print(res)
    try:
        gmail = smtplib.SMTP('smtp.gmail.com', 587)

        gmail.ehlo()

        gmail.starttls()

        gmail.login('YOUR ACTIVE EMAILID@gmail.com', 'YOUR PASSWORD')

    except Exception as e:
        print("Couldn't setup email!!" + str(e))

    msg = MIMEText("Your Password is " + str(res))

    msg['Subject'] = 'Verification'

    msg['To'] = mail

    msg['From'] = 'YOUR ACTIVE EMAILID@gmail.com'

    try:

        gmail.send_message(msg)

    except Exception as e:

        print("COULDN'T SEND EMAIL", str(e))

    return render_template("login.html")

@app.route('/')
def login():
    return render_template("login.html")


@app.route('/click',methods=['post'])
def click():
    db=Db()
    n1=request.form['textfield']
    n2=request.form['textfield2']
    qry=db.selectOne("select * from login where username='"+n1+"' and password='"+n2+"'")
    if qry is not None:
        type=qry['type']
        session['login_id']=qry['lid']
        loid=session['login_id']
        session["ltype"]=type

        if type=='admin':
            session["lo"] = "lin"
            return redirect('/adminhome')

        if type=='rc_owner':
            session["lo"] = "lin"
            qry22 = db.selectOne("select * from black_list,vehicle,uv where vehicle.vid=black_list.vid and vehicle.vid=uv.vid and uv.uid='" + str(loid) + "'")
            if qry22 is None:
                qry2 = db.selectOne("select vehicle.vno,uv.vid from vehicle,uv where vehicle.vid=uv.vid and uv.uid='" + str(loid) + "'")
                print(qry2)
                vno = qry2['vno']
                print("vno", vno)
                vid = qry2['vid']
                print("vid", vid)
                qry1 = db.selectOne("select count(tid) as cntt from tracked_violation where vno='" + str(vno) + "'")
                print("count", qry1)
                cnt = qry1['cntt']
                print("cnt", cnt)
                if int(cnt) >= 5:
                    qry3 = db.insert("insert into black_list values(null,'" + str(vid) + "',curdate())")
                    return redirect('/rchome')
                else:
                    return redirect('/rchome')
            else:
                return redirect('/rchome')

        if type =='traffic_police':
            session["lo"] = "lin"
            return redirect('/tphome')
    else:
        return "pwd mismatch"

@app.route('/tphome')
def tphome():
    if session["lo"]=="lin":
        type=session["ltype"]
        if type=="traffic_police":
            return render_template("tphome.html")
        else:
            return login()
    else:
        return login()




@app.route('/reg')
def reg():
    return render_template("registr.html")

@app.route('/registr',methods=['post'])
def registr():
    db=Db()
    n1=request.form['name']
    n2=request.form['radio']
    n3 = request.form['dob']
    n4 = request.form['place']
    n5 = request.form['post']
    n6 = request.form['pin']
    n7 = request.form['email']
    n8 = request.files['photo']
    n9 = request.form['contact']
    a=request.form['password']
    b=request.form['cpass']

    data=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    n8.save(main_path+data+'.jpg')
    path="/static/user/"+data+'.jpg'
    qq=db.selectOne("select * from login where username='"+n7+"'")
    if qq is not None :
        return '<script>alert("This username already exist....Please enter valid datas...");window.location="/reg"</script>'
    else:
        if a==b:
            qry1=db.insert("insert into login(username,password,type)values('"+n7+"','"+a+"','pending')")
            qry=db.insert("insert into rc_owner(uid,uname,gender,dob,place,post,pin,email,photo,contact)VALUES ('"+str(qry1)+"','"+n1+"','"+n2+"','"+n3+"','"+n4+"','"+n5+"','"+n6+"','"+n7+"','"+str(path)+"','"+n9+"')")
            return '<script>alert("Successfully registered");window.location="/"</script>'
        else:
            return '<script>alert("Password mismatch");window.location="/reg"</script>'

@app.route('/viewrc')
def viewrc():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from rc_owner,login where login.lid=rc_owner.uid and type='pending'")
        return render_template("viewrc.html",data=qry)
    else:
        return login()

@app.route('/approve_rc/<id>')
def approve_rc(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.update("update login set type='rc_owner' where lid='"+str(id)+"'")
        return '<script>alert("successfully approved");window.location="/viewrc"</script>'
    else:
        return login()
#
# @app.route('/approve_rc1/<id>')
# def approve_rc1(id):
#     if session["lo"] == "lin":
#         db=Db()
#         qry=db.update("update login set type='rc_owner' where lid='"+str(id)+"'")
#         return '<script>alert("successfully approved");window.location="/viewrc"</script>'
#     else:
#         return login()

@app.route('/viewarc')
def viewarc():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from rc_owner,login where login.lid=rc_owner.uid and type='rc_owner'")
        return render_template("viewarc.html",data=qry)
    else:
        return login()

@app.route('/viewarc1')
def viewarc1():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from rc_owner,login where login.lid=rc_owner.uid and type='rc_owner'")
        return render_template("viewarc1.html",data=qry)
    else:
        return login()

@app.route('/reject_rc/<id>')
def reject_rc(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.update("update login set type='rejected' WHERE lid='"+str(id)+"'")
        return '<script>alert("failed");window.location="/viewrc"</script>'
    else:
        return login()

@app.route('/viewrrc')
def viewrrc():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from rc_owner,login where login.lid=rc_owner.uid and type='rejected'")
        return render_template("viewrrc.html",data=qry)
    else:
        return login()

@app.route('/viewcom')
def viewcam():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from complaint,rc_owner where complaint.uid=rc_owner.uid and complaint.reply='pending'")
        return render_template("complaint.html", data=qry)
    else:
        return login()

@app.route('/vcom')
def vcom():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from complaint,rc_owner WHERE complaint.uid=rc_owner.uid and reply='pending'")
        return render_template("complaint.html",data=qry)
    else:
        return login()

@app.route('/reply/<id>')
def reply(id):
    if session["lo"] == "lin":
        return render_template("reply.html",data=id)
    else:
        return login()

@app.route('/sreply',methods=['post'])
def sreply():
    if session["lo"] == "lin":
        db=Db()
        n2=request.form['cid']
        n1=request.form['reply']
        qry=db.update("update complaint set reply='"+n1+"',reply_date=curdate() where cid='"+str(n2)+"'")
        return '<script>alert("Replied successfully");window.location="/vcom"</script>'
    else:
        return login()

@app.route('/tp')
def tp():
    if session["lo"] == "lin":
        return render_template("addtp.html")
    else:
        return login()

@app.route('/add',methods=['post'])
def add():
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['tpn']
        n2=request.form['radio']
        n3 = request.form['dob']
        n4 = request.form['place']
        n7 = request.form['pin']
        n5 = request.form['post']
        n6 = request.form['email']
        n8 = request.files['photo']
        n9 = request.form['cn']
        pwd = random.randint(0000, 9999)
        pik=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        n8.save(main_path1+pik+'.jpg')
        path2="/static/trafficpolice/"+pik+'.jpg'
        qq = db.selectOne("select * from login where username='" + n6 + "'")
        if qq is not None:
            return '<script>alert("This username already exist....Please enter valid datas...");window.location="/reg"</script>'
        else:
            qry1 = db.insert("insert into login(username,password,type)values('" + n6 + "','" + str(pwd) + "','traffic_police')")
            qry=db.insert("insert into traffic_police(tid,tpname,gender,dob,place,email,post,pin,photo,contact)VALUES ('"+str(qry1)+"','"+n1+"','"+n2+"','"+n3+"','"+n4+"','"+n6+"','"+n5+"','"+n7+"','"+str(path2)+"','"+n9+"')")
            try:
                gmail = smtplib.SMTP('smtp.gmail.com', 587)

                gmail.ehlo()

                gmail.starttls()

                gmail.login('YOUR ACTIVE EMAILID@gmail.com', 'YOUR PASSWORD')

            except Exception as e:
                print("Couldn't setup email!!" + str(e))

            msg = MIMEText("Your Password is " + str(pwd))

            msg['Subject'] = 'Verification'

            msg['To'] = n6

            msg['From'] = 'YOUR ACTIVE EMAILID@gmail.com' # THIS EMAIL MUST SET AS 'LESS SECURE' ((OPEN YOUR MAIL-->MANAGE YOUR ACCOUNT-->SECURITY-->LESS SECURE(TURN ON))))

            try:

                gmail.send_message(msg)

            except Exception as e:

                print("COULDN'T SEND EMAIL", str(e))

            return '<script>alert("successfully registered");window.location="/viewtp"</script>'
    else:
        return login()

@app.route('/veh')
def veh():
    if session["lo"] == "lin":
        return render_template("vehicle.html")
    else:
        return login()

@app.route('/addv1',methods=['post'])
def addv():
    if session["lo"] == "lin":
        db=Db()
        id=session['login_id']
        # n1=request.form['vnum']
        n2=request.form['chnum']
        n3 = request.form['vname']
        n4 = request.form['adnum']
        n5 = request.form['mand']
        n6 = request.form['company']
        n7 = request.form['tov']

        qry=db.insert("insert into vehicle(vno,chno,vhname,adharno,manu_date,company,tov)VALUES ('0','"+n2+"','"+n3+"','"+n4+"','"+n5+"','"+n6+"','"+n7+"')")
        qry1=db.insert("insert into uv(vid,uid)values('"+str(qry)+"','"+str(id)+"')")
        return '<script>alert("successfully added");window.location="/vv"</script>'
    else:
        return login()

@app.route('/helmetvio')
def helmetvio():
    if session["lo"] == "lin":
        db=Db()
        # qq=db.select("select * from helmet_violation,tracked_violation,offence where tracked_violation.hid=helmet_violation.hid and offence.tid=tracked_violation.tid ")
        # qr=db.select("select tracked_violation.hid from helmet_violation,tracked_violation where tracked_violation.hid=helmet_violation.hid")
        qry=db.select("select * from helmet_violation,camera where cid=camid and status='pending'")
        return render_template("view_helmetvio.html",data=qry)
    else:
        return login()

@app.route('/trackvio/<hid>')
def trackvio(hid):
    if session["lo"] == "lin":
        db=Db()
        return render_template("capture_vehno.html",hid=hid)
    else:
        return login()

@app.route('/trackvio1/<hid>',methods=['post'])
def trackvio1(hid):
    if session["lo"] == "lin":
        db=Db()
        vno=request.form['vno']
        qryq = db.select("select * from penalty")
        qry=db.insert("insert into tracked_violation values(null,'"+hid+"','"+vno+"')")
        qq=db.update("update helmet_violation set status='tracked' where hid='"+hid+"'")
        qry2 = db.selectOne("select vid from vehicle where vehicle.vno='" + vno + "'")
        vid=qry2['vid']
        qry1 = db.selectOne("select rc_owner.* from vehicle,uv,rc_owner where rc_owner.uid=uv.uid and uv.vid=vehicle.vid and vehicle.vid='" + str(vid) + "'")
        email = qry1['email']

        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            gmail.login('YOUR ACTIVE EMAILID@gmail.com', 'YOUR PASSWORD')

        except Exception as e:
            print("Couldn't setup email!!" + str(e))

        msg = MIMEText("Your Vehicle No." +vno+ "has been spoted for not wearing helmet while driving...")

        msg['Subject'] = 'Verification'

        msg['To'] = str(email)

        msg[
            'From'] = 'YOUR ACTIVE EMAILID@gmail.com'  # THIS EMAIL MUST SET AS 'LESS SECURE' ((OPEN YOUR MAIL-->MANAGE YOUR ACCOUNT-->SECURITY-->LESS SECURE(TURN ON))))

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))

        return render_template("addoffence.html",tidd=hid,data=qryq)
    else:
        return login()


@app.route('/notif')
def notif():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        qry = db.select("select * from vehicle,uv,rc_owner,tracked_violation,helmet_violation where rc_owner.uid=uv.uid and uv.vid=vehicle.vid and uv.uid='" + str(lid) + "' and vehicle.vno=tracked_violation.vno and tracked_violation.hid=helmet_violation.hid")
        # q=db.select("select * from tracked_violation,offence where offence.tid=tracked_violation.tid")
        # qry=db.select("select * from helmet_violation,tracked_violation,uv,vehicle,rc_owner where tracked_violation.hid=helmet_violation.hid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid")
        return render_template("tracknotif.html",data=qry)
    else:
        return login()

@app.route('/viewtrackedvio')
def viewtrackedvio():
    if session["lo"] == "lin":
        db=Db()
        q=db.select("select * from tracked_violation,offence where offence.tid=tracked_violation.tid")
        qry=db.select("select * from helmet_violation,tracked_violation,uv,vehicle,rc_owner where tracked_violation.hid=helmet_violation.hid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid")
        return render_template("view_trackedvio.html",data=qry)
    else:
        return login()

@app.route('/viewoffence')
def viewoffence():
    if session["lo"] == "lin":
        db=Db()
        # q=db.select("select * from tracked_violation,offence where offence.tid=tracked_violation.tid")
        qry=db.select("select * from helmet_violation,tracked_violation,offence,uv,vehicle,rc_owner,penalty where penalty.pid=offence.penalty_id and tracked_violation.hid=helmet_violation.hid and offence.tid=tracked_violation.tid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid")
        return render_template("viewoffence.html",data=qry)
    else:
        return login()
#
# @app.route('/addoffence/<tid>')
# def addoffence(tid):
#     if session["lo"] == "lin":
#         db=Db()
#         qry=db.select("select * from penalty")
#         return render_template("addoffence.html",data=qry,tid=tid)
#     else:
#         return login()

@app.route('/addoffence1/<tid>',methods=['post'])
def addoffence1(tid):
    if session["lo"] == "lin":
        db=Db()
        off=request.form['off']
        pid=request.form['pen']
        # fin=request.form['fin']
        loc=request.form['loc']
        qry=db.insert("insert into offence values(null,'"+tid+"','"+off+"','"+pid+"','"+loc+"',curdate(),curtime())")
        return '<script>alert("successfully added");window.location="/viewtrackedvio"</script>'
    else:
        return login()

@app.route('/vv')
def vv():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from vehicle ")
        return render_template("vvehicle.html",data=qry)
    else:
        return login()

@app.route('/vveh')
def vveh():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from vehicle,uv,rc_owner where rc_owner.uid=uv.uid and uv.vid=vehicle.vid and vehicle.vno!='0' ")
        return render_template("vvehicles.html",data=qry)
    else:
        return login()

@app.route('/addv111/<id>')
def addv111(id):
    if session["lo"] == "lin":
        return render_template("assign_vehno.html",vid=id)
    else:
        return login()

@app.route('/addv11/<id>',methods=['post'])
def addv11(id):
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['vnum']
        qry=db.insert("update vehicle set vno='"+n1+"' where vid='"+id+"'")
        return '<script>alert("Assign vehicle no successfully");window.location="/adminhome"</script>'
    else:
        return login()

@app.route('/vv1/<uid>')
def vv1(uid):
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from vehicle,uv where vehicle.vid=uv.vid and uv.uid='"+str(uid)+"' ")
        if qry is not None:
            return render_template("vehicleno.html",data=qry)
        else:
            return '<script>alert("No vehicles are registered yet");window.location="/adminhome"</script>'
    else:
        return login()

@app.route('/delete3/<id>')
def delete3(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.delete("delete from vehicle where vid='"+id+"'")
        return redirect('/vv')
    else:
        return login()

@app.route('/edit3/<id>')
def edit3(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.selectOne("select * from vehicle where vid='"+str(id)+"'")
        return render_template("edit3.html",data=qry)
    else:
        return login()

@app.route('/update3')
def update3():
    if session["lo"] == "lin":
        db=Db()
        # n1=request.form['vnum']
        n2=request.form['chnum']
        n3=request.form['vname']
        n4=request.form['adnum']
        n5=request.form['mand']
        n6=request.form['company']
        n7=request.form['tov']

        qry=db.update("update vehicle set chno='"+n2+"',vhname='"+n3+"',adharno='"+n4+"',manu_date='"+n5+"',company='"+n6+"'",tov='"+n7+"')
        return '<script>alert("successfully updated");window.location="/vv"</script>'
    else:
        return login()

@app.route('/viewtp')
def view1():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from traffic_police ")
        return render_template('viewtp.html',data=qry)
    else:
        return login()

@app.route('/delete/<id>')
def delete(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.delete("delete from traffic_police where tid='"+id+"'")
        return redirect('/viewtp')
    else:
        return login()

@app.route('/edit/<id2>')
def edit(id2):
    if session["lo"] == "lin":
        db=Db()
        qry=db.selectOne("select * from traffic_police WHERE tid='"+id2+"'")
        return render_template("edit.html",data=qry)
    else:
        return login()

@app.route('/update/<id>',methods=['post'])
def update(id):
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['tpn']
        n2=request.form['place']
        n3 = request.form['post']
        n4 = request.form['pin']
        n5 = request.files['photo']
        n6 = request.form['cn']

        pik = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        n5.save(main_path1 + pik + '.jpg')
        path2 = "/static/trafficpolice/" + pik + '.jpg'
        if request.files:
            if n5.filename=="":
                qry=db.update("update  traffic_police set tpname='"+n1+"',place='"+n2+"',post='"+n3+"',pin='"+n4+"',contact='"+n6+"' where tid='"+id+"'")
                return '<script>alert("successfully updated");window.location="/viewtp"</script>'
            else:
                qry = db.update("update  traffic_police set tpname='" + n1 + "',place='" + n2 + "',post='" + n3 + "',pin='" + n4 + "',photo='" + str(path2) + "',contact='" + n6 + "' where tid='" + id + "'")
                return '<script>alert("successfully updated");window.location="/viewtp"</script>'
        else:
            qry = db.update("update  traffic_police set tpname='" + n1 + "',place='" + n2 + "',post='" + n3 + "',pin='" + n4 + "',contact='" + n6 + "' where tid='" + id + "'")
            return '<script>alert("successfully updated");window.location="/viewtp"</script>'
    else:
        return login()

@app.route('/camera')
def camera():
    if session["lo"] == "lin":
        return render_template("camera.html")
    else:
        return login()

@app.route('/addcam1',methods=['post'])
def addcam1():
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['sno']
        n2=request.form['cm']
        n3 = request.form['loc']
        n4 = request.form['lat']
        n5 = request.form['lon']
        qry=db.insert("insert into camera(serial_no,camera_model,location,latitude,longitude)VALUES ('"+n1+"','"+n2+"','"+n3+"','"+n4+"','"+n5+"')")
        return '<script>alert("successfully added");window.location="/viewcam"</script>'
    else:
        return login()

@app.route('/viewcam')
def vcam():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from camera")
        return render_template('viewcam.html',data=qry)
    else:
        return login()

@app.route('/delete2/<id>')
def delete2(id):
    if session["lo"] == "lin":
        db=Db()
        qry=db.delete("delete from camera where cid='"+id+"'")
        return redirect('/viewcam')
    else:
        return login()

@app.route('/edit2/<id2>')
def edit2(id2):
    if session["lo"] == "lin":
        db=Db()
        qry=db.selectOne("select * from camera WHERE cid='"+id2+"'")
        return render_template("edit2.html",data=qry)
    else:
        return login()

@app.route('/update2/<id>',methods=['post'])
def update2(id):
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['sno']
        n2=request.form['cm']
        n3 = request.form['loc']
        n4 = request.form['lat']
        n5 = request.form['lon']
        qry=db.update("update camera set serial_no='"+n1+"',camera_model='"+n2+"',location='"+n3+"',latitude='"+n4+"',longitude='"+n5+"' WHERE cid='"+id+"'")
        return '<script>alert("successfully updated");window.location="/viewcam"</script>'
    else:
        return login()


@app.route('/penalty')
def penalty():
    if session["lo"] == "lin":
        return render_template("penalty.html")
    else:
        return login()

@app.route('/addp',methods=['post'])
def addp():
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['pname']
        n2=request.form['des']
        n3=request.form['fine']
        qry=db.insert("insert into penalty(penaltyname,descr,fine) VALUES ('"+n1+"','"+n2+"','"+n3+"')")
        return '<script>alert("Inserted successfully");window.location="/tphome"</script>'
    else:
        return login()

@app.route('/vpen')
def vpen():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from penalty")
        return render_template("vpenalty.html",data=qry)
    else:
        return login()


@app.route('/viewpro')
def viewpro():
    if session["lo"] == "lin":
        db=Db()
        id = session['login_id']
        qry = db.selectOne("select * from traffic_police where tid='" + str(id) + "'")
        return render_template("viewtpprofile.html",data=qry)
    else:
        return login()

@app.route('/adminhome')
def adminhome():
    if session["lo"] == "lin":
        type = session["ltype"]
        if type == "admin":
            return render_template("adminhome.html")
        else:
            return login()
    else:
        return login()


@app.route('/complaint')
def complaint():
    if session["lo"] == "lin":
        return render_template("complaintu.html")
    else:
        return login()

@app.route('/tcom',methods=['post'])
def tcom():
    if session["lo"] == "lin":
        lid=session['login_id']
        db=Db()
        n1=request.form['com']
        qry=db.insert("insert into complaint(complaint,date,reply,uid)VALUES ('"+n1+"',curdate(),'pending','"+str(lid)+"')")
        return '<script>alert("successfully added");window.location="/complaint"</script>'
    else:
        return login()

@app.route('/vadminpen')
def vadminpen():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from helmet_violation,tracked_violation,offence,uv,vehicle,rc_owner,penalty where penalty.pid=offence.penalty_id and tracked_violation.hid=helmet_violation.hid and offence.tid=tracked_violation.tid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid")
        # qry=db.select("select helmet_violation.date,helmet_violation.time,offence.offence,tracked_violation.vno,tracked_violation.tid,penalty.*,uv.uid,helmet_violation.status from helmet_violation,tracked_violation,offence,uv,vehicle,rc_owner,penalty where penalty.pid=offence.penalty_id and tracked_violation.hid=helmet_violation.hid and offence.tid=tracked_violation.tid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid and rc_owner.uid='"+str(lid)+"'")
        return render_template("viewpenadmin.html",data=qry)
    else:
        return login()

@app.route('/viewreply')
def viewreply():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        qry=db.select("select * from complaint where uid='"+str(lid)+"'")
        return render_template("viewreply_rc.html",data=qry)
    else:
        return login()

@app.route('/adminvb')
def adminvb():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from black_list,vehicle,rc_owner,uv where black_list.vid=vehicle.vid and rc_owner.uid=uv.uid and uv.vid=black_list.vid")
        return render_template("blackviewadmin.html",data=qry)
    else:
        return login()

@app.route('/viewblacktp')
def viewblacktp():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from black_list,vehicle,rc_owner,uv where black_list.vid=vehicle.vid and rc_owner.uid=uv.uid and uv.vid=black_list.vid")
        return render_template("blackviewtp.html",data=qry)
    else:
        return login()

@app.route('/adminvb1')
def adminvb1():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        # qry=db.select("select * from black_list,vehicle where black_list.vid=vehicle.vid")
        qry=db.select("select helmet_violation.date,helmet_violation.time,offence.offence,tracked_violation.vno,tracked_violation.tid,penalty.*,uv.uid,helmet_violation.status from helmet_violation,tracked_violation,offence,uv,vehicle,rc_owner,penalty where penalty.pid=offence.penalty_id and tracked_violation.hid=helmet_violation.hid and offence.tid=tracked_violation.tid and uv.vid=vehicle.vid and vehicle.vno=tracked_violation.vno and uv.uid=rc_owner.uid and rc_owner.uid='"+str(lid)+"' ")
        return render_template("blackviewrc.html",data=qry)
    else:
        return login()

@app.route('/vvio')
def vvio():
    if session["lo"] == "lin":
        db=Db()
        qry=db.select("select * from helmet_violation,tracked_violation,vehicle,offence,camera where helmet_violation.hid=tracked_violation.hid and tracked_violation.vno=vehicle.vno and tracked_violation.tid=offence.tid and helmet_violation.camid=camera.cid")
        return render_template("vvio.html",data=qry)
    else:
        return login()


@app.route('/viewrcdata/<uid>')
def viewrcdata(uid):
    if session["lo"] == "lin":
        db=Db()
        qry=db.selectOne("select * from rc_owner where uid='"+str(uid)+"'")
        return render_template("viewrcdata.html",data=qry)
    else:
        return login()

@app.route('/viewrcdata1/<uid>')
def viewrcdata1(uid):
    if session["lo"] == "lin":
        db=Db()
        qry=db.selectOne("select * from rc_owner where uid='"+str(uid)+"'")
        return render_template("viewrcdata1.html",data=qry)
    else:
        return login()

@app.route('/viewprorc')
def viewprorc():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        qry=db.selectOne("select * from rc_owner where uid='"+str(lid)+"'")
        return render_template("viewprorc.html",data=qry)
    else:
        return login()

@app.route('/viewprorc1',methods=['post'])
def viewprorc1():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        qry=db.selectOne("select * from rc_owner where uid='"+str(lid)+"'")
        return render_template("viewprorc1.html",data=qry)
    else:
        return login()

@app.route('/viewblack')
def viewblack():
    if session["lo"] == "lin":
        lid = session['login_id']
        db=Db()
        qry=db.select("select black_list.bv,vehicle.vid,vehicle.vno,vehicle.vhname,black_list.date from black_list,uv,vehicle where black_list.vid=uv.vid and uv.vid=vehicle.vid and uv.uid='"+str(lid)+"' ")
        return render_template("viewblacklist.html",i=qry)
    else:
        return login()

# @app.route('/vo')
# def vo():
#     if session["lo"] == "lin":
#         db=Db()
#         lid=session['login_id']
#         qry=db.select("select * from helmet_violation,tracked_violation,vehicle,offence where helmet_violation.hid=tracked_violation.hid and tracked_violation.vno=vehicle.vno and tracked_violation.tid=offence.tid and ")
#         return render_template("vo.html",data=qry)
#     else:
#         return login()

@app.route('/vo')
def vo():
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        qry=db.select("select * from helmet_violation,tracked_violation,vehicle,offence where helmet_violation.hid=tracked_violation.hid and tracked_violation.vno=vehicle.vno and tracked_violation.tid=offence.tid and ")
        return render_template("vo.html",data=qry)
    else:
        return login()


@app.route('/updaterc/<id>',methods=['post'])
def updaterc(id):
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['name']
        n2=request.form['radio']
        n3=request.form['dob']
        n4=request.form['place']
        n5=request.form['post']
        n6=request.form['pin']
        n7=request.form['email']
        n8=request.files['photo']
        n9=request.form['contact']

        pik = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        n8.save(main_path1 + pik + '.jpg')
        path2 = "/static/user/" + pik + '.jpg'
        if request.files is not None:
            if n8.filename=="":
                qry=db.update("update rc_owner set uname='"+n1+"',gender='"+n2+"',dob='"+n3+"',place='"+n4+"',post='"+n5+"',pin='"+n6+"',contact='"+n9+"'where uid='"+id+"'")
                return '<script>alert("successfully updated");window.location="/viewprorc"</script>'
            else:
                qry=db.update("update rc_owner set uname='"+n1+"',gender='"+n2+"',dob='"+n3+"',place='"+n4+"',post='"+n5+"',pin='"+n6+"',photo='"+str(path2)+"',contact='"+n9+"'where uid='"+id+"'")
                return '<script>alert("successfully updated");window.location="/viewprorc"</script>'
        else:
            qry=db.update("update rc_owner set uname='"+n1+"',gender='"+n2+"',dob='"+n3+"',place='"+n4+"',post='"+n5+"',pin='"+n6+"',contact='"+n9+"'where uid='"+id+"'")
            return '<script>alert("successfully updated");window.location="/viewprorc"</script>'
    else:
        return login()

@app.route('/cpass')
def cpass():
    if session["lo"] == "lin":
        return render_template("changepass.html")
    else:
        return login()

@app.route('/changepass/<id>')
def changepass(id):
    if session["lo"] == "lin":
        db=Db()
        n1=request.form['npass']
        qry=db.update("update login set password='"+n1+"'where uid='"+id+"'")
        return '<script>alert("successfully updated");window.location="/viewprorc"</script>'
    else:
        return login()

@app.route('/payment/<tid>/<fine>')
def payment(tid,fine):
    if session["lo"] == "lin":
        return render_template("payfine.html",tid=tid,fine=fine)
    else:
        return login()

@app.route('/payment1/<tid>/<fine>',methods=['post'])
def payment1(tid,fine):
    if session["lo"] == "lin":
        db=Db()
        lid=session['login_id']
        acc=request.form['acc']
        sec=request.form['SEC']
        yy=db.selectOne("select hid from tracked_violation where tid='"+tid+"'")
        hid=yy['hid']
        qqq=db.selectOne("select * from bank where accno='"+acc+"' and secpin='"+sec+"'")
        if qqq is not None:
            qq=db.selectOne("select * from bank where bankid='2'")
            amt=qq['balance']
            if int(fine)<int(amt):
                qry = db.insert("insert into payment values(null,'" + str(lid) + "','" + fine + "',curdate(),curtime(),'" + tid + "')")
                qry1=db.update("update bank set balance=balance-'"+fine+"'where bankid='2'")
                qry2=db.update("update bank set balance=balance+'"+fine+"'where bankid='1'")
                yyy = db.update("update helmet_violation set status='paid' where hid='" + str(hid) + "'")
                return '<script>alert("Fine Paid");window.location="/rchome"</script>'
            else:
                return '<script>alert("Insufficient balance in your account");window.location="/rchome"</script>'
        else:
            return '<script>alert("Enter your valid account details");window.location="/adminvb1"</script>'
    else:
        return login()

@app.route('/rchome')
def rchome():
    if session["lo"] == "lin":
        type = session["ltype"]
        if type == "rc_owner":
            return render_template("rchome.html")
        else:
            return login()
    else:
        return login()





if __name__ == '__main__':
    app.run(port=3000,debug=True)




