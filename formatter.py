import os

GRADER_HEADER = """GRADE=0.0\n"""
COMMENT_HEADER = '''CANVAS_COMMENT="""
Write your comment starting here
"""\n'''
GRADE_END = """#### END GRADE HEADER ####\n"""

def generate_grading_header(directory:str):

    name_splits = "_".join(directory.split(os.sep)[-1].split("_")[0:2])
    name_header = 'NAME = "{}"\n'.format(name_splits)
    return name_header + GRADER_HEADER + COMMENT_HEADER + GRADE_END

def print_verifier(sid, grade, comment):
    print("\n\n\n\n\nVERIFCATION STAGE:")
    print("Here's the input I read from the file:")
    print("Results for:", sid)
    print("Grade:", grade)
    print("Comment:", comment)
