#!/usr/bin/env python3
import psycopg2

#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''
def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    # userid = "root"
    # passwd = "123456"
    # myHost = "localhost"
    database = "postgres"
    userid = "postgres"
    passwd ="123456"
    myHost = "localhost" 


    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(
                                    user = userid,
                                    password = passwd,
                                    host = myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    
    # return the connection to use
    return conn

'''
Validate staff based on username and password
'''
def checkLogin(login, password):
    # Attempt to connect to the databese 尝试连接数据库
    conn = openConnection()

    if conn is None:
        return None
    
    cursor = conn.cursor()

    try:
        # Use Pointers to execute SQL statements and search for user information 使用指针来执行SQL语句，搜索用户信息
        cursor.execute(
            '''
                SELECT username, firstname, lastname, email
                FROM administrator
                WHERE username = %s AND password = %s;
            '''
            ,(login, password)
        )

        user = cursor.fetchall()
        
        # If login fails, None is returned 如果登录失败，返回None
        if not user:
            return None
        
        # Format conversion 格式转换
        user_info = list(user[0])

        return user_info
    
    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
        return None
    
    finally:
        cursor.close()
        conn.close()
   


'''
List all the associated admissions records in the database by staff
'''
def findAdmissionsByAdmin(login):
    # Connect to the database
    conn = openConnection()

    if conn is None:
        return None

    cursor = conn.cursor()

    try:
        # Call the stored procedure for fetching admissions by administrator
        cursor.callproc('get_admissions_by_admin', [login])
        rows = cursor.fetchall()

        if not rows:
            return None

        attributes = [attrib[0] for attrib in cursor.description]
        row_to_dictionary = [dict(zip(attributes, row)) for row in rows]

        return row_to_dictionary

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
        return None

    finally:
        cursor.close()
        conn.close()


    


'''
Find a list of admissions based on the searchString provided as parameter
See assignment description for search specification
'''
def findAdmissionsByCriteria(searchString):
    conn = openConnection()

    if conn is None:
        return None

    cursor = conn.cursor()

    try:
        # Call the stored procedure for finding admissions by keyword
        cursor.callproc('find_admissions', [searchString])
        rows = cursor.fetchall()

        if not rows:
            return None

        attributes = [attrib[0] for attrib in cursor.description]
        row_to_dictionary = [dict(zip(attributes, row)) for row in rows]

        return row_to_dictionary

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
        return None

    finally:
        cursor.close()
        conn.close()


'''
Add a new addmission 
'''
def addAdmission(type, department, patient, condition, admin):
    # Attempt to connect to the databese 尝试连接数据库
    conn = openConnection()

    if conn is None:
        return False
    
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO admission(admissiontype, department, patient, "condition", administrator)
                VALUES(
                    (SELECT admissiontypeid FROM admissiontype WHERE LOWER(admissiontypename) LIKE LOWER('%%' || %s ||'%%')),
                    (SELECT deptid FROM department WHERE LOWER(deptname) LIKE LOWER('%%' || %s ||'%%')),
                    (SELECT patientid FROM patient WHERE LOWER(patientid) LIKE LOWER('%%' || %s ||'%%')),
                    %s,
                    %s);
            ''', (type, department, patient, condition, admin)
        )

        conn.commit()
        return True

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
        return False
    
    finally:
        cursor.close()
        conn.close()
    


'''
Update an existing admission
'''
def updateAdmission(id, type, department, dischargeDate, fee, patient, condition):
    conn = openConnection()

    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        # Call the stored procedure for updating admission
        cursor.callproc('update_admission', [id, type, department, dischargeDate, fee, patient, condition])
        conn.commit()

        return True

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
        return False

    finally:
        cursor.close()
        conn.close()