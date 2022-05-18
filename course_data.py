# Canvas API URL
API_URL = "https://canvas.northwestern.edu/"
CANVAS_COURSE_ID = 165750

FILE_SPEC = {
  "homework 4": {
      'files_to_run': ['main.py'],
      'file_to_grade': 'main.py',
      'other_files_to_open': []
  },
  "tutorial 6": {
      'files_to_run': ['01_mouse_events.py', '02_keyboard_events.py'],
      'file_to_grade': '01_mouse_events.py',
      'other_files_to_open': ['02_keyboard_events.py']
  },
  "tutorial 7": {
      'files_to_run': ['q1.py','q2.py','q3.py','q4.py'],
      'file_to_grade': 'q1.py',
      'other_files_to_open': ['q2.py','q3.py','q4.py']
  },
  "project 1": {
      'files_to_run': ['main.py'],
      'file_to_grade': 'main.py',
      'other_files_to_open': ['landscape.py', 'creature.py']
  }
}


def get_file_spec(a_name:str):
    a_name = a_name.lower()
    files_to_run = FILE_SPEC[a_name]['files_to_run']
    file_to_grade = FILE_SPEC[a_name]['file_to_grade']
    files_to_comment = FILE_SPEC[a_name]['other_files_to_open']

    return (files_to_run, file_to_grade, files_to_comment)
