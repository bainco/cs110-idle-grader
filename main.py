from subprocess import Popen, PIPE
import os, re, shutil, sys, zipfile

GRADER_HEADER = r"""GRADE=0.0\n"""

COMMENT_HEADER = r'''CANVAS_COMMENT="""
Write your comment starting here
"""\n'''

GRADE_END = r"""#### END GRADE HEADER ####\n"""

PYTHON_PATH = sys.executable

def flatten(directory):
    for dirpath, _, filenames in os.walk(directory, topdown=False):
        for filename in filenames:
            i = 0
            source = os.path.join(dirpath, filename)
            target = os.path.join(directory, filename)

            while os.path.exists(target):
                i += 1
                file_parts = os.path.splitext(os.path.basename(filename))

                target = os.path.join(
                    directory,
                    file_parts[0] + "_" + str(i) + file_parts[1],
                )

            shutil.move(source, target)

        if dirpath != directory:
            os.rmdir(dirpath)

import pip

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
        print("That's not a valid directory. Try again later.")
        quit()
else:
    CWD = os.getcwd()

try:
    f = open("canvas_token.txt", 'r')
    API_KEY = f.readline()
    f.close()

except OSError:
    print("no existing token found.")
    API_KEY = input("please paste your canvas token here: ")
    if len(API_KEY) < 20:
        print("INVALID TOKEN. Please contact Connor")
        quit()
    text_file = open("canvas_token.txt", "wt")
    text_file.write(API_KEY)
    text_file.close()

# Canvas API URL
API_URL = "https://canvas.northwestern.edu/"
CANVAS_COURSE_ID = 165750
# Initialize a new Canvas object
canvas = canvasapi.Canvas(API_URL, API_KEY)
current_course = canvas.get_course(CANVAS_COURSE_ID)

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
    clean_name = re.sub(r"[^a-zA-Z0-9]","",the_assignment.name)

    try:
        os.mkdir(clean_name)
    except:
        import shutil
        print("folder already existed...deleting")
        shutil.rmtree(clean_name)
        os.mkdir(clean_name)

    os.chdir(clean_name)
    ASSIGNMENT_CWD = os.getcwd()

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

    subfolders = [ f.path for f in os.scandir(ASSIGNMENT_CWD) if f.is_dir() ]

    # Flatten all folders in case students do something funky
    for directory in subfolders:
        flatten(directory)

    ASSIGNMENT_DATA = {
        "homework 4": {
            'files_to_run': ['main.py'],
            'file_to_grade': 'main.py',
            'other_files_to_open': []
        }
    }

    files_to_run = ASSIGNMENT_DATA[assignment_name.lower()]['files_to_run']
    file_to_grade = ASSIGNMENT_DATA[assignment_name.lower()]['file_to_grade']
    files_to_comment = ASSIGNMENT_DATA[assignment_name.lower()]['other_files_to_open']

    for download in subfolders:
        os.chdir(download)
        name_header = "NAME = \"" + "-".join(download.split("/")[-1].split("_")[0:2]) + "\"\n"
        # Add grade header
        with open(file_to_grade, 'r+') as file:
            content = file.read()
            file.seek(0)
            file.write(name_header + GRADER_HEADER + COMMENT_HEADER + GRADE_END + content)

        runners = []
        for file in files_to_run:
            runners.append(Popen([PYTHON_PATH, "-m", "idlelib", "-r", file], stdout=PIPE, stderr=PIPE))

        editors = []
        for file in [file_to_grade] + files_to_comment:
            editors.append(Popen([PYTHON_PATH, "-m", "idlelib", "-e", file]))

        exit_codes = [p.wait() for p in runners + editors]

        print(download, "finished grading")

        with open(file_to_grade) as myfile:
            grade_head = []
            for line in myfile.readlines():
                grade_head.append(line)
                if line == GRADE_END:
                    break

        #print(grade_head)

        grade = float(grade_head[1].split("=")[-1].replace("\n", ""))
        comment = []
        i = 3
        while grade_head[i] != GRADE_END:
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

        maybe_wait = input("Is this correct? Hit enter for yes, anything else for no. ")
        if maybe_wait != "":
            quit()

        # TEMPORARY TEST STUDENT
        student_id = 211292

        the_submission = the_assignment.get_submission(student_id)

        #### POSTING TEXT COMMENTS AND GRADES
        comment_json = {"text_comment": canvas_comment}
        the_submission.edit(submission={'posted_grade': grade}, comment=comment_json)
        ## UPLOADING FILES AS COMMENTS (can't also upload text)
        the_submission.upload_comment(open(file_to_grade, 'rb'))

        ### VERIFY
        print("Please verify correct submission at the following link:")
        print("https://canvas.northwestern.edu/courses/{}/gradebook/speed_grader?assignment_id={}&student_id={}\n".format(CANVAS_COURSE_ID,the_assignment.id,student_id))

        maybe_wait = input("Continue? Hit enter for yes, anything else for no. ")
        if maybe_wait != "":
            quit()
