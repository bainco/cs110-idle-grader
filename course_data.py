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
  }
}


def get_file_spec(a_name:str):
    a_name = a_name.lower()
    files_to_run = FILE_SPEC[a_name]['files_to_run']
    file_to_grade = FILE_SPEC[a_name]['file_to_grade']
    files_to_comment = FILE_SPEC[a_name]['other_files_to_open']

    return (files_to_run, file_to_grade, files_to_comment)
