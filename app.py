import os
import boto3
import requests
import hashlib
import json
import base64
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from botocore.exceptions import ClientError
from random import randrange


app = Flask(__name__)
app.secret_key = os.urandom(24)
session = boto3.session.Session()

region_name = 'us-east-1'
aws_access_key_id = 'ASIAZRNZRCV34ZJG7RVA'
aws_secret_access_key = 'd2GUaMfyc7hbek9T3/iN2WGN6hKnfoY7Fn54KtVc'
aws_session_token = 'FwoGZXIvYXdzEOn//////////wEaDHXOdrac3vmZ/8npPyK/AQ6URvrDkDefh5bnOf/pDUzKY1FnTL76e6mdiOR6rEmDFxJu4SY+8XgEU61pH5b3/ZkqA1XPracum7koVLUCGlRqP3/hTcU2FKsKpVYYKsRxM+7pkQyGmjKGV04TKADCN7Tx4asmdM14myKhpUuwWazgO0FL99sZD3ul6M62Np3nd9osao+KnZBOWH2Xm+xZu9+rv9O5HgA7N6Lkn8KIF+ae4FWUjEswJH2KALkt0pGptiVWQy651j7kyBn41nWAKIr8sYMGMi2LqPD+096toT1lYGHNgDDYjWk5Slhbx0CC8nKnYKZIeuACtlAYVIfHOT/F8g8 ='

client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

s3 = boto3.resource(
    service_name='s3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)
s3Client = boto3.client(
    service_name='s3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

get_secret_value_response = client.get_secret_value(
    SecretId="dy/read/hashkey1")
salt = json.loads(get_secret_value_response.get(
    'SecretString')).get('hash_key')
get_secret_value_responseurl = client.get_secret_value(
    SecretId="dy/read")
url = json.loads(get_secret_value_responseurl.get(
    'SecretString')).get('dynamodb-read')

get_secret_value_responseurlR = client.get_secret_value(
    SecretId="dy/set")
urlR = json.loads(get_secret_value_responseurlR.get(
    'SecretString')).get('dynamodb-set')


@app.route('/')
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    #url = "http://localhost:5001/index"
    return render_template('main.html')


@app.route('/desciption', methods=['GET', 'POST'])
def description():
    pdfbucket = request.args.get('url', '')
    temp = pdfbucket.split("?")
    detail = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': temp[0], 'Key': temp[1]},
                                             ExpiresIn=60)
    return render_template('description.html', fileURL=detail)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password = password+salt
        encrypted_password = str(hashlib.md5(password.encode()).hexdigest())
        url1 = url+"/dynamodb-read/?username="+str(username)
        content = {}
        try:
            res = requests.get(url1)
            content = res.json()
        except:
            pass
        if 'username' in content:
            usernameFromDB = content['username']
            passwordFromDB = content['password']
        else:
            return render_template('login.html', error="No Account!!Please Register")

        if username == usernameFromDB and encrypted_password == passwordFromDB:
            temp = url_for('upload')+"?username="+str(username)
            return render_template('login.html', message="Login successful", new_page=temp)
        else:
            return render_template('login.html', error="Invail Password!!")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password = password+salt
        encrypted_password = str(hashlib.md5(password.encode()).hexdigest())
        registe = username+"?"+encrypted_password
        url1 = urlR+"/dyset?username="+str(registe)
        content = {}
        try:
            res = requests.get(url1)
            content = res.json()
        except:
            pass
        if 'message' in content:
            message = content['message']
            temp = url_for('upload')+"?username="+str(username)
            return render_template('register.html', message=message, new_page=temp)
        elif 'error' in content:
            error = content['error']
            temp = url_for('login')
            return render_template('register.html', error=error, new_page=temp)
    return render_template('register.html')


@app.route('/breakfast', methods=['GET', 'POST'])
def breakfast():
    totalCountforBreakfast = 0
    for key in s3.Bucket("breakfast12").objects.all():
        totalCountforBreakfast += 1
# breakfast S3...................................................
    rb0 = randrange(totalCountforBreakfast)
    count0 = 0
    tempbreakfastkeyname0 = ''
    for key in s3Client.list_objects(Bucket="breakfast12")['Contents']:
        if count0 == rb0:
            tempbreakfastkeyname0 = key['Key']
        count0 = count0+1

    count00 = 0
    tempbreakfastkeyname00 = ''
    for key in s3Client.list_objects(Bucket="breakfast-image12")['Contents']:
        if count00 == rb0:
            tempbreakfastkeyname00 = key['Key']
        count00 = count00+1

    image1 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "breakfast-image12", 'Key': tempbreakfastkeyname00},
                                             ExpiresIn=60)
    name1 = tempbreakfastkeyname00[0:len(tempbreakfastkeyname00)-5]

    ab0 = url_for('description')+"?url=breakfast12?"+str(tempbreakfastkeyname0)
# ............................................................
    rb1 = randrange(totalCountforBreakfast)
    count1 = 0
    tempbreakfastkeyname1 = ''
    for key in s3Client.list_objects(Bucket="breakfast12")['Contents']:
        if count1 == rb1:
            tempbreakfastkeyname1 = key['Key']
        count1 = count1+1

    count01 = 0
    tempbreakfastkeyname01 = ''
    for key in s3Client.list_objects(Bucket="breakfast-image12")['Contents']:
        if count01 == rb1:
            tempbreakfastkeyname01 = key['Key']
        count01 = count01+1

    image2 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "breakfast-image12", 'Key': tempbreakfastkeyname01},
                                             ExpiresIn=60)
    name2 = tempbreakfastkeyname01[0:len(tempbreakfastkeyname01)-5]

    ab1 = url_for('description')+"?url=breakfast12?"+str(tempbreakfastkeyname1)
# ............................................................
    rb2 = randrange(totalCountforBreakfast)
    count2 = 0
    tempbreakfastkeyname2 = ''
    for key in s3Client.list_objects(Bucket="breakfast12")['Contents']:
        if count2 == rb2:
            tempbreakfastkeyname2 = key['Key']
        count2 = count2+1

    count02 = 0
    tempbreakfastkeyname02 = ''
    for key in s3Client.list_objects(Bucket="breakfast-image12")['Contents']:
        if count02 == rb2:
            tempbreakfastkeyname02 = key['Key']
        count02 = count02+1

    image3 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "breakfast-image12", 'Key': tempbreakfastkeyname02},
                                             ExpiresIn=60)
    name3 = tempbreakfastkeyname02[0:len(tempbreakfastkeyname02)-5]

    ab2 = url_for('description')+"?url=breakfast12?"+str(tempbreakfastkeyname2)
# ............................................................
    rb3 = randrange(totalCountforBreakfast)
    count3 = 0
    tempbreakfastkeyname3 = ''
    for key in s3Client.list_objects(Bucket="breakfast12")['Contents']:
        if count3 == rb3:
            tempbreakfastkeyname3 = key['Key']
        count3 = count3+1

    count03 = 0
    tempbreakfastkeyname03 = ''
    for key in s3Client.list_objects(Bucket="breakfast-image12")['Contents']:
        if count03 == rb3:
            tempbreakfastkeyname03 = key['Key']
        count03 = count03+1

    image4 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "breakfast-image12", 'Key': tempbreakfastkeyname03},
                                             ExpiresIn=60)
    name4 = tempbreakfastkeyname03[0:len(tempbreakfastkeyname03)-5]

    ab3 = url_for('description')+"?url=breakfast12?"+str(tempbreakfastkeyname3)

    return render_template('breakfast.html', detailforbreakfast=ab0, detailforlunch=ab1, detailfordinner=ab2, detailforsnack=ab3,
                           picture1=image1, name1=name1, picture2=image2, name2=name2, picture3=image3, name3=name3, picture4=image4, name4=name4
                           )


@app.route('/lunch', methods=['GET', 'POST'])
def lunch():
    totalCountforBreakfast = 0
    for key in s3.Bucket("lunch12").objects.all():
        totalCountforBreakfast += 1
# ............................................................
    rb0 = randrange(totalCountforBreakfast)
    count0 = 0
    tempbreakfastkeyname0 = ''
    for key in s3Client.list_objects(Bucket="lunch12")['Contents']:
        if count0 == rb0:
            tempbreakfastkeyname0 = key['Key']
        count0 = count0+1

    count00 = 0
    tempbreakfastkeyname00 = ''
    for key in s3Client.list_objects(Bucket="lunch-image12")['Contents']:
        if count00 == rb0:
            tempbreakfastkeyname00 = key['Key']
        count00 = count00+1

    image1 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "lunch-image12",
                                                     'Key': tempbreakfastkeyname00},
                                             ExpiresIn=60)
    name1 = tempbreakfastkeyname00[0:len(tempbreakfastkeyname00)-5]
    ab0 = url_for('description')+"?url=lunch12?"+str(tempbreakfastkeyname0)
# ............................................................
    rb1 = randrange(totalCountforBreakfast)
    count1 = 0
    tempbreakfastkeyname1 = ''
    for key in s3Client.list_objects(Bucket="lunch12")['Contents']:
        if count1 == rb1:
            tempbreakfastkeyname1 = key['Key']
        count1 = count1+1

    count01 = 0
    tempbreakfastkeyname01 = ''
    for key in s3Client.list_objects(Bucket="lunch-image12")['Contents']:
        if count01 == rb1:
            tempbreakfastkeyname01 = key['Key']
        count01 = count01+1

    image2 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "lunch-image12",
                                                     'Key': tempbreakfastkeyname01},
                                             ExpiresIn=60)
    name2 = tempbreakfastkeyname01[0:len(tempbreakfastkeyname01)-5]

    ab1 = url_for('description')+"?url=lunch12?"+str(tempbreakfastkeyname1)
# ............................................................
    rb2 = randrange(totalCountforBreakfast)
    count2 = 0
    tempbreakfastkeyname2 = ''
    for key in s3Client.list_objects(Bucket="lunch12")['Contents']:
        if count2 == rb2:
            tempbreakfastkeyname2 = key['Key']
        count2 = count2+1
    count02 = 0
    tempbreakfastkeyname02 = ''
    for key in s3Client.list_objects(Bucket="lunch-image12")['Contents']:
        if count02 == rb2:
            tempbreakfastkeyname02 = key['Key']
        count02 = count02+1

    image3 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "lunch-image12",
                                                     'Key': tempbreakfastkeyname02},
                                             ExpiresIn=60)
    name3 = tempbreakfastkeyname02[0:len(tempbreakfastkeyname02)-5]
    ab2 = url_for('description')+"?url=lunch12?"+str(tempbreakfastkeyname2)
# ............................................................
    rb3 = randrange(totalCountforBreakfast)
    count3 = 0
    tempbreakfastkeyname3 = ''
    for key in s3Client.list_objects(Bucket="lunch12")['Contents']:
        if count3 == rb3:
            tempbreakfastkeyname3 = key['Key']
        count3 = count3+1

        count03 = 0
    tempbreakfastkeyname03 = ''
    for key in s3Client.list_objects(Bucket="lunch-image12")['Contents']:
        if count03 == rb3:
            tempbreakfastkeyname03 = key['Key']
        count03 = count03+1

    image4 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "lunch-image12",
                                                     'Key': tempbreakfastkeyname03},
                                             ExpiresIn=60)
    name4 = tempbreakfastkeyname03[0:len(tempbreakfastkeyname03)-5]
    ab3 = url_for('description')+"?url=lunch12?"+str(tempbreakfastkeyname3)

    return render_template('lunch.html', detailforbreakfast=ab0, detailforlunch=ab1, detailfordinner=ab2, detailforsnack=ab3,
                           picture1=image1, name1=name1, picture2=image2, name2=name2, picture3=image3, name3=name3, picture4=image4, name4=name4
                           )


@app.route('/dinner', methods=['GET', 'POST'])
def dinner():

    totalCountforBreakfast = 0
    for key in s3.Bucket("dinner12").objects.all():
        totalCountforBreakfast += 1
# ............................................................
    rb0 = randrange(totalCountforBreakfast)
    count0 = 0
    tempbreakfastkeyname0 = ''
    for key in s3Client.list_objects(Bucket="dinner12")['Contents']:
        if count0 == rb0:
            tempbreakfastkeyname0 = key['Key']
        count0 = count0+1
    count00 = 0
    tempbreakfastkeyname00 = ''
    for key in s3Client.list_objects(Bucket="dinner-image12")['Contents']:
        if count00 == rb0:
            tempbreakfastkeyname00 = key['Key']
        count00 = count00+1

    image1 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "dinner-image12", 'Key': tempbreakfastkeyname00},
                                             ExpiresIn=60)
    name1 = tempbreakfastkeyname00[0:len(tempbreakfastkeyname00)-5]
    ab0 = url_for('description')+"?url=dinner12?"+str(tempbreakfastkeyname0)
# ............................................................
    rb1 = randrange(totalCountforBreakfast)
    count1 = 0
    tempbreakfastkeyname1 = ''
    for key in s3Client.list_objects(Bucket="dinner12")['Contents']:
        if count1 == rb1:
            tempbreakfastkeyname1 = key['Key']
        count1 = count1+1

    count01 = 0
    tempbreakfastkeyname01 = ''
    for key in s3Client.list_objects(Bucket="dinner-image12")['Contents']:
        if count01 == rb1:
            tempbreakfastkeyname01 = key['Key']
        count01 = count01+1

    image2 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "dinner-image12", 'Key': tempbreakfastkeyname01},
                                             ExpiresIn=60)
    name2 = tempbreakfastkeyname01[0:len(tempbreakfastkeyname01)-5]

    ab1 = url_for('description')+"?url=dinner12?"+str(tempbreakfastkeyname1)
# ............................................................
    rb2 = randrange(totalCountforBreakfast)
    count2 = 0
    tempbreakfastkeyname2 = ''
    for key in s3Client.list_objects(Bucket="dinner12")['Contents']:
        if count2 == rb2:
            tempbreakfastkeyname2 = key['Key']
        count2 = count2+1
    count02 = 0
    tempbreakfastkeyname02 = ''
    for key in s3Client.list_objects(Bucket="dinner-image12")['Contents']:
        if count02 == rb2:
            tempbreakfastkeyname02 = key['Key']
        count02 = count02+1

    image3 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "dinner-image12", 'Key': tempbreakfastkeyname02},
                                             ExpiresIn=60)
    name3 = tempbreakfastkeyname02[0:len(tempbreakfastkeyname02)-5]

    ab2 = url_for('description')+"?url=dinner12?"+str(tempbreakfastkeyname2)
# ............................................................
    rb3 = randrange(totalCountforBreakfast)
    count3 = 0
    tempbreakfastkeyname3 = ''
    for key in s3Client.list_objects(Bucket="dinner12")['Contents']:
        if count3 == rb3:
            tempbreakfastkeyname3 = key['Key']
        count3 = count3+1
    count03 = 0
    tempbreakfastkeyname03 = ''
    for key in s3Client.list_objects(Bucket="dinner-image12")['Contents']:
        if count03 == rb3:
            tempbreakfastkeyname03 = key['Key']
        count03 = count03+1

    image4 = s3Client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': "dinner-image12", 'Key': tempbreakfastkeyname03},
                                             ExpiresIn=60)
    name4 = tempbreakfastkeyname03[0:len(tempbreakfastkeyname03)-5]

    ab3 = url_for('description')+"?url=dinner12?"+str(tempbreakfastkeyname3)

    return render_template('dinner.html', detailforbreakfast=ab0, detailforlunch=ab1, detailfordinner=ab2, detailforsnack=ab3,
                           picture1=image1, name1=name1, picture2=image2, name2=name2, picture3=image3, name3=name3, picture4=image4, name4=name4
                           )


@app.route('/snack', methods=['GET', 'POST'])
def snack():

    totalCountforBreakfast = 0
    for key in s3.Bucket("snack12").objects.all():
        totalCountforBreakfast += 1
# ............................................................
    rb0 = randrange(totalCountforBreakfast)
    count0 = 0
    tempbreakfastkeyname0 = ''
    for key in s3Client.list_objects(Bucket="snack12")['Contents']:
        if count0 == rb0:
            tempbreakfastkeyname0 = key['Key']
        count0 = count0+1

    count00 = 0
    tempbreakfastkeyname00 = ''
    for key in s3Client.list_objects(Bucket="snack-image12")['Contents']:
        if count00 == rb0:
            tempbreakfastkeyname00 = key['Key']
        count00 = count00+1

    image1 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "snack-image12",
                                                     'Key': tempbreakfastkeyname00},
                                             ExpiresIn=60)
    name1 = tempbreakfastkeyname00[0:len(tempbreakfastkeyname00)-5]

    ab0 = url_for('description')+"?url=snack12?"+str(tempbreakfastkeyname0)
# ............................................................
    rb1 = randrange(totalCountforBreakfast)
    count1 = 0
    tempbreakfastkeyname1 = ''
    for key in s3Client.list_objects(Bucket="snack12")['Contents']:
        if count1 == rb1:
            tempbreakfastkeyname1 = key['Key']
        count1 = count1+1

    count01 = 0
    tempbreakfastkeyname01 = ''
    for key in s3Client.list_objects(Bucket="snack-image12")['Contents']:
        if count01 == rb1:
            tempbreakfastkeyname01 = key['Key']
        count01 = count01+1

    image2 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "snack-image12",
                                                     'Key': tempbreakfastkeyname01},
                                             ExpiresIn=60)
    name2 = tempbreakfastkeyname01[0:len(tempbreakfastkeyname01)-5]

    ab1 = url_for('description')+"?url=snack12?"+str(tempbreakfastkeyname1)
# ............................................................
    rb2 = randrange(totalCountforBreakfast)
    count2 = 0
    tempbreakfastkeyname2 = ''
    for key in s3Client.list_objects(Bucket="snack12")['Contents']:
        if count2 == rb2:
            tempbreakfastkeyname2 = key['Key']
        count2 = count2+1

    count02 = 0
    tempbreakfastkeyname02 = ''
    for key in s3Client.list_objects(Bucket="snack-image12")['Contents']:
        if count02 == rb2:
            tempbreakfastkeyname02 = key['Key']
        count02 = count02+1

    image3 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "snack-image12",
                                                     'Key': tempbreakfastkeyname02},
                                             ExpiresIn=60)
    name3 = tempbreakfastkeyname02[0:len(tempbreakfastkeyname02)-5]

    ab2 = url_for('description')+"?url=snack12?"+str(tempbreakfastkeyname2)
# ............................................................
    rb3 = randrange(totalCountforBreakfast)
    count3 = 0
    tempbreakfastkeyname3 = ''
    for key in s3Client.list_objects(Bucket="snack12")['Contents']:
        if count3 == rb3:
            tempbreakfastkeyname3 = key['Key']
        count3 = count3+1

    count03 = 0
    tempbreakfastkeyname03 = ''
    for key in s3Client.list_objects(Bucket="snack-image12")['Contents']:
        if count03 == rb3:
            tempbreakfastkeyname03 = key['Key']
        count03 = count03+1

    image4 = s3Client.generate_presigned_url('get_object',
                                             Params={'Bucket': "snack-image12",
                                                     'Key': tempbreakfastkeyname03},
                                             ExpiresIn=60)
    name4 = tempbreakfastkeyname03[0:len(tempbreakfastkeyname03)-5]

    ab3 = url_for('description')+"?url=snack12?"+str(tempbreakfastkeyname3)

    return render_template('snack.html', detailforbreakfast=ab0, detailforlunch=ab1, detailfordinner=ab2, detailforsnack=ab3,
                           picture1=image1, name1=name1, picture2=image2, name2=name2, picture3=image3, name3=name3, picture4=image4, name4=name4
                           )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    username = request.args.get('username', '')
    if request.method == "POST":
        filename = request.files['Recipes']
        image = request.files['coverPage']
        NameOfRecipes = request.form['NameOfRecipes']
        TypeOfRecipes = request.form['TypeOfRecipes']
        key = NameOfRecipes+".pdf"
        imagename = image.filename
        start = len(imagename)-4
        end = len(imagename)
        imagename = imagename[start:end]
        key1 = NameOfRecipes+imagename
        if TypeOfRecipes == "Breakfast":
            s3.Bucket('breakfast12').upload_fileobj(filename, key,
                                                    ExtraArgs={'ContentType': "application/pdf"})
            s3.Bucket('breakfast-image12').upload_fileobj(image, key1)
            return render_template('update.html', userName=username, message="Upload Successful!")
        elif TypeOfRecipes == "Lunch":
            s3.Bucket('lunch12').upload_fileobj(filename, key,
                                                ExtraArgs={'ContentType': "application/pdf"})
            s3.Bucket('lunch-image12').upload_fileobj(image, key1)
            return render_template('update.html', userName=username, message="Upload Successful!")
        elif TypeOfRecipes == "Dinner":
            s3.Bucket('dinner-image12').upload_fileobj(image, key1)
            s3.Bucket('dinner12').upload_fileobj(filename, key,
                                                 ExtraArgs={'ContentType': "application/pdf"})
            return render_template('update.html', userName=username, message="Upload Successful!")
        elif TypeOfRecipes == "Snack":
            s3.Bucket('snack-image12').upload_fileobj(image, key1)
            s3.Bucket('snack12').upload_fileobj(filename, key,
                                                ExtraArgs={'ContentType': "application/pdf"})
            return render_template('update.html', message="Upload Successful!")
        else:
            return render_template('update.html', error="Input Correct Type of Recipes")
    return render_template("update.html")


if __name__ == '__main__':
    app.run(debug=True)
