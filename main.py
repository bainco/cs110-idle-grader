from subprocess import Popen, PIPE
import os, re, sys, zipfile, pip, shutil

import utilities, headers, course_data

try:
    canvasapi = __import__("canvasapi")
except ImportError:
    pip.main(['install', "canvasapi"])

try:
    requests = __import__("requests")
except ImportError:
    pip.main(['install', "requests"])

print("Your current working directory is {}.\nWould you like to change it to something else?".format(os.getcwd()))
CWD = input("Leave blank to leave the working directory as is. Enter a new one to overwrite.")

if len(CWD) > 0:
    try:
        os.chdir(CWD)
    except:
        print("That's not a valid directory. Exiting.")
        quit()
else:
    CWD = os.getcwd()

try:
    f = open("canvas_token.txt", 'r')
    API_KEY = f.readline()
    f.close()

except OSError:
    print("No existing CANVAS API token found.")
    print("Instructions to make one can be found here https://community.canvaslms.com/docs/DOC-16005-42121018197")
    API_KEY = input("please paste your canvas token here: ")

try:
    canvas = canvasapi.Canvas(course_data.API_URL, API_KEY)
    text_file = open("canvas_token.txt", "wt")
    text_file.write(API_KEY)
    text_file.close()
except:
    print("INVALID TOKEN. Please contact Connor.")
    quit()

# Initialize a new Canvas object
current_course = canvas.get_course(course_data.CANVAS_COURSE_ID)

pm_name = input("What's your first name? (e.g. Connor) ")
pm_name = pm_name.capitalize()
assignment_name = input("Which assignment would you like to grade? (e.g. Homework 2) ")

assignments = current_course.get_assignments(search_term=assignment_name.lower())
tutorials = current_course.get_groups()

submissions = []
for the_assignment in assignments:
    print("Downloading submissions for", the_assignment.name)
    for tutorial in tutorials:
        if pm_name in tutorial.name:
            for student in tutorial.get_users():
                the_submission = the_assignment.get_submission(student)
                print("{} - {}: ".format(student.name, student.sis_user_id),the_submission.workflow_state)
                if the_submission.workflow_state in ["submitted", "pending_review"]:
                    submissions.append(the_submission)

    os.chdir(CWD)
    clean_name = re.sub(r"[^a-zA-Z0-9]", "", the_assignment.name)

    try:
        os.mkdir(clean_name)
    except:
        print("folder already existed...deleting")
        shutil.rmtree(clean_name)
        os.mkdir(clean_name)

    os.chdir(clean_name)
    for sub in submissions:
        the_student = current_course.get_user(sub.user_id)
        if hasattr(sub, "attachments"):
            r = requests.get(sub.attachments[-1]['url'])
            with open(str(sub.user_id) + ".zip",'wb') as f:
                f.write(r.content)
            the_zip = zipfile.ZipFile(str(sub.user_id) + ".zip")
            the_zip.extractall("{}_{}_{}_pending".format(the_student.name, the_student.sis_user_id, the_student.id))
        else:
            print("This student does not have any attachments for this assignment.", the_student.name, the_student.sis_user_id)

    subfolders = [f.path for f in os.scandir(os.getcwd()) if f.is_dir()]

    # Flatten all folders in case students do something funky
    for directory in subfolders:
        utilities.flatten(directory)

    (files_to_run, file_to_grade, files_to_comment) = course_data.get_file_spec(assignment_name)

    for download in subfolders:
        os.chdir(download)

        # Add grade header
        with open(file_to_grade, 'r+') as file:
            content = file.read()
            file.seek(0)
            file.write(headers.generate_grading_header(download))

        runners = []
        for file in files_to_run:
            runners.append(Popen([sys.executable, "-m", "idlelib", "-r", file], stdout=PIPE, stderr=PIPE))

        editors = []
        for file in [file_to_grade] + files_to_comment:
            editors.append(Popen([sys.executable, "-m", "idlelib", "-e", file]))

        exit_codes = [p.wait() for p in runners + editors]

        print(download, "finished grading assignment", download)

        with open(file_to_grade) as myfile:
            grade_head = []
            for line in myfile.readlines():
                grade_head.append(line)
                if line == headers.GRADE_END:
                    break

        grade = float(grade_head[1].split("=")[-1].replace("\n", ""))

        comment = []
        i = 3
        while grade_head[i] != headers.GRADE_END:
            comment.append(grade_head[i])
            i += 1

        comment.pop()
        canvas_comment = "".join(comment)

        student_id = int(download.split("_")[-2])

        print("\n\n\n\n\nVERIFCATION STAGE:")
        print("Here's the input I read from the file:")
        print("Results for:", student_id)
        print("Grade:", grade)
        print("Comment:", canvas_comment)

        maybe_wait = input("Is this correct? Hit enter for yes, type s to skip, anything else to quit. ")
        if maybe_wait == "s":
            continue
        elif maybe_wait != "":
            quit()

        # TEMPORARY TEST STUDENT (Uncomment if you want )
        #student_id = 211292

        the_submission = the_assignment.get_submission(student_id)

        #### POSTING TEXT COMMENTS, GRADE, and FILE
        the_submission.edit(submission={'posted_grade': grade}, comment={"text_comment": canvas_comment})
        the_submission.upload_comment(open(file_to_grade, 'rb'))

        ### VERIFY
        print("Please verify correct submission at the following link:")
        print(utilities.gen_sg_link(course_data.CANVAS_COURSE_ID, the_assignment.id, student_id))

        maybe_wait = input("Continue? Hit enter for yes, anything else for no. ")
        if maybe_wait != "":
            quit()
