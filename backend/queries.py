from database_connect import connection

cursor = connection.cursor()

# function that returns the number of students
def get_num_of_students():
    cursor.execute("SELECT COUNT(*) FROM student")
    student_count = cursor.fetchone()[0]

    return student_count


def get_all_students():
    cursor.execute('SELECT first_name, last_name, student_id, degree_program, status FROM student')
    rows = cursor.fetchall()
    students = []
    for first_name, last_name, student_id, degree_program, status in rows:
        students.append({
            "name": f"{last_name}, {first_name}",
            "course_name": degree_program,
            "student_number": student_id,
            "status": status or "pending"
        })

    connection.commit()
    return students


def get_student(student_id):
    cursor.execute(f"SELECT first_name, last_name, degree_program, student_id, gwa, total_units FROM student WHERE student_id = ?", student_id)
    first_name, last_name, course, student_id, gwa, total_units = cursor.fetchone()

    summary = standardize_data(get_student_data(student_id))
    student_data = {
        "name": first_name + ", " + last_name,
        "course": course,
        "student_number": student_id,
        "GWA": gwa,
        "total_units": total_units,
        "summary": summary,
    }
    
    connection.commit()
    return student_data


def get_student_data(student_id):
    cursor.execute(f"SELECT course_code, grade, units, weight, cumulative, semester, acad_year FROM studentData WHERE student_id = ?", student_id)
    raw_student_data = cursor.fetchall()

    student_data = []
    for course_code, grade, units, weight, cumulative, semester, acad_year in raw_student_data:
        
        student_dict = {
          acad_year: {
            semester: {
              "course_number": course_code,
              "grade": grade,
              "units": units,
              "weight": weight,
              "cumulative": cumulative,
            }
          }
        }
        student_data.append(student_dict)
        
    connection.commit()

    return student_data


def standardize_data(student_data_list):

    # student_data_list = [{}, {}, {},]
    acad_year = []
    for student_data in student_data_list:
        # if wala yung acad year 
        if student_data.keys() not in acad_year:
            acad_year.append(student_data.keys())

    acad_year = list(acad_year)
    # print(acad_year)
    # if equal yung acad_year (database side) sa acad_year ng (student_data.keys())
    # for year in acad_year:
        
    # separate for loop

    # student_data[acad_year].keys()

    sorted_student_data = []
    for i in range(len(acad_year)):
        sorted_student_data.append([])

    # len(acad_year) = 5
    # sorted_student_data = [[], [], [], [], []]

    for student_data in student_data_list:
        for i in range (len(acad_year)):
            if student_data.keys() == acad_year[i]:
                sorted_student_data[i].append(student_data[str(student_data.keys())[12:17]])

    # print(sorted_student_data[0].values())

    # "semester": 
# [
#   [ {} ],
#   [ {} ] 
# ]

    
    count = 0
    student_info = []
    for student_list in sorted_student_data:
        sem_1 = []
        sem_2 = []
        for dict in student_list:
            # print("dict key: " + str(dict.keys())[12:13])
            if str(dict.keys())[12:13] == "1":
                sem_1.append(dict[str(dict.keys())[12:13]])
            elif str(dict.keys())[12:13] == "2":
                sem_2.append(dict[str(dict.keys())[12:13]])

        

        student_grades = {
            
            # "semester": "Semester 1-" + "A.Y." + acad_year[count] + "-" + acad_year[count],
            "content": sem_1,
            "semester": "Semester 1-" + "A.Y." + "20"+ str(acad_year[count])[12:14] + "-" + "20"+ str(acad_year[count])[15:17],
        }

        student_info.append(student_grades)

        student_grades = {
            
            # "semester": "Semester 2-" + "A.Y." + str(acad_year[count]) + "-" + acad_year[count],
            "content": sem_2,
            "semester": "Semester 2-" + "A.Y." + "20"+ str(acad_year[count])[12:14] + "-" + "20"+ str(acad_year[count])[15:17],
        }

        student_info.append(student_grades)

        count += 1
        
    # print(student_info)
    # print(sem_2)

    return student_info

# function for adding or removing rows



# function for 
# ing the data in the database




# function that tracks the changelog

def delete_studentData(student_id, code, semester, acad_year):
    print(f"DELETE FROM studentData WHERE student_id = '{student_id}' AND course_code = '{code}' AND semester = '{semester}' AND acad_year = '{acad_year}'")
    cursor.execute(f"DELETE FROM studentData WHERE student_id = '{student_id}' AND course_code = '{code}' AND semester = '{semester}' AND acad_year = '{acad_year}'")

    connection.commit()

# function to add student
def add_studentData(student_id, code, grade, units, weight, cumulative, semester):
    # if the semester string contains the substirng "midyear", treat the added student data as midyear, else, it would the first or second semester
    if "midyear" in semester:
        semester_num = 'M'
        semester_year = semester[7:12]
    else:
        semester_num =  1 if len(semester) == 7 else 2 
        semester_year = semester[2:7] if len(semester) == 7 else semester[3:8]
    #IL/15/16
    #I/15/16
    #midyear 2016
    cursor.execute('insert into studentData(student_id, course_code, grade, units, weight, cumulative, semester, acad_year) values(?,?,?,?,?,?,?,?);', (student_id, code, grade, units, weight, cumulative, semester_num, semester_year))
    connection.commit()                                                                                                                #what do you need me to do? Hahaha

def check_credentials( username, password):
    values = cursor.execute('SELECT email, password FROM faculty')
    for i in values:
        if(i[0] == username.strip() and i[1] == password.strip()):
            return True
        # print( i[0] + ' ---- '+username.strip())
        # print(i[1]  + ' ---- '+password.strip())
    return False

# add_studentData('4579-76154', 'CMSC 128', 1, 3, 6, 156, 'll/15/16')
# delete_studentData('4579-76154', 'CMSC 128', 1, '15/16')

def get_GECourses():
    GEList = []

    for course_name, course_code,ge_type in cursor.execute('SELECT course_name, course_code, ge_type FROM geCourses'):
        temp = [str(course_name) + ' ' + str(course_code), ge_type]
        GEList.append(temp)

    return GEList

def check_ge_requirements(student_id):
    ge_courses = get_GECourses()
    students = get_student_data(student_id)
    # print(ge_courses)
    elective_count = 0
    core_count = 0
    hk11_count = 0
    hk12_count = 0
    nstp1_count = 0
    nstp2_count = 0

    

    for student in students:
        for student_data_acad_year in list(student.keys()):
            for student_data_semester in list(student[student_data_acad_year].keys()):
                course = student[student_data_acad_year][student_data_semester]['course_number']
                for i in ge_courses:
                    
                    if(i[0] in course):
                        try:
                            if (not course[len(i[0])].isdigit()):
                                print(course)
                                if(i[1] == 'elective'):
                                    elective_count += 1
                                else:
                                    core_count += 1
                        except:
                            print(course)
                            if(i[1] == 'elective'):
                                elective_count += 1
                            else:
                                core_count += 1
                if(course == 'HK 12'):
                    hk12_count +=1
                elif(course == 'HK 11'):
                    hk11_count += 1
                elif(course == 'NSTP 2'):
                    nstp2_count +=1
                elif(course == 'NSTP 1'):
                    nstp1_count += 1
    # print('hk count:' + str(hk_count))
    # print('nstp count:'+ str(nstp_count))
                        
                        
                        
    # 7 dapat yung core GEs
    # 3 lang yung elective GEs
                  

    if (core_count < 7 and elective_count < 3):
        cursor.execute('insert into studentFlags(student_id, flag) values(?,?);', (student_id, 'Incomplete GE'))
        connection.commit()
    if (hk12_count < 3):
        cursor.execute('insert into studentFlags(student_id, flag) values(?,?);', (student_id, 'Incomplete HK12'))
    
    if (hk11_count < 1):
        cursor.execute('insert into studentFlags(student_id, flag) values(?,?);', (student_id, 'Incomplete HK11'))
      
    if (nstp2_count == 0):
        cursor.execute('insert into studentFlags(student_id, flag) values(?,?);', (student_id, 'Incomplete NSTP2'))
        
    if (nstp1_count == 0 ):
        cursor.execute('insert into studentFlags(student_id, flag) values(?,?);', (student_id, 'Incomplete NSTP1'))
        
    connection.commit()
    
def edit_data(student_id, table, course_code, semester, acad_year, col_name, new_data):
    # try:
    cursor.execute(f"UPDATE {table} SET {col_name} = '{new_data}' WHERE student_id = '{student_id}' AND course_code = '{course_code}' AND acad_year = '{acad_year}' AND semester = '{semester}'")
    connection.commit()
    # except:
    #     print("Invalid Data!")           
            
def add_faculty(email, password, faculty_id, name):
    cursor.execute(f"INSERT into faculty(email, password, faculty_id, name) values(?,?,?,?);", (email, password, faculty_id, name))
    connection.commit()

def remove_faculty(faculty_id):
    cursor.execute(f"DELETE FROM faculty WHERE faculty_id = '{faculty_id}'")
    connection.commit()


def record_changelogs(faculty_id, student_id, justification, col_name, prev_data, new_data):
    cursor.execute(f"INSERT INTO changelogs(faculty_id, student_id, date, time, justification, col_name, prev_data, new_data) values('{faculty_id}','{student_id}',CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,'{justification}','{col_name}','{prev_data}','{new_data}')")
    connection.commit()

def get_all_faculties():
    faculties = []
    for name, faculty_id, email, in cursor.execute('SELECT name, faculty_id, email FROM faculty'):
        faculty = {
            "name": name,
            "faculty_id": faculty_id,
            "email": email
        }
        faculties.append(faculty)

    return faculties

def get_student_flags(student_id):
    errors = []
    for flags in cursor.execute(f"SELECT flag FROM studentFlags WHERE student_id = '{student_id}'"):
        errors.append(flags)
        
    return errors

def get_student_data_flags(student_id):
    flags = []
    for id, course_code, semester, acad_year, col_name, prev_data, new_data in cursor.execute(f"SELECT student_id, course_code, semester, acad_year, col_name, prev_data, new_data FROM remarks WHERE student_id = '{student_id}'"):
        flag = {
            "student_id": id,
            "course_code": course_code,
            "semester": semester,
            "acad_year": acad_year,
            "col_name": col_name,
            "prev_data": prev_data,
            "new_data": new_data
        }
        flags.append(flag)

    return flags

def edit_student(student_id, col_name, new_data):
    cursor.execute(f"UPDATE student SET {col_name} = '{new_data}' WHERE student_id = '{student_id}'")


record_changelogs('1111-11111', '1289-71389', 'Wrong grade in CMSC 123', 'grade', '2', '1')
# edit_data('3284-18043', 'studentData', 'ENG 1(AH)', '3', '15/16', 'grade', '2')

# check_ge_requirements('4579-76154')
# create_faculty('shac_shac91@gmail.com', 'shac', '1111-11111', 'Shac Member 91')

# print(get_all_faculties())


# def get_courses(student_number):
#     for student_number, first_name, last_name, degree_program, gwa, computed_gwa, college,  total_units, req_units, total_cumulative, first_verifier, second_verifier, other_verifier, status in cursor.execute(f"SELECT student_number, first_name, last_name, degree_program, gwa, computed_gwa, college,  total_units, req_units, total_cumulative, first_verifier, second_verifier, other_verifier, status FROM student WHERE student_number = ?", student_number):
#         student = {
#             "student_number": student_number,
#             "first_name": first_name,
#             "last_name": last_name,
#             "degree_program": degree_program,
#             "gwa": gwa,
#             "computed_gwa": computed_gwa,
#             "college": college,
#             "total_units": total_units,
#             "req_units": req_units,
#             "total_cumulative": total_cumulative,
#             "first_verifier": first_verifier,
#             "second_verifier": second_verifier,
#             "other_verifier" :other_verifier,
#             "status" : status,
#         }
#         return student