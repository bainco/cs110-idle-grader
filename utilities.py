import os, shutil

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

def flatten_all_directories(the_folder):
    subfolders = [f.path for f in os.scandir(the_folder) if f.is_dir()]
    # Flatten all folders in case students do something funky
    for directory in subfolders:
        flatten(directory)

    return subfolders

def gen_sg_link(cid:int, aid:int, sid:int):
    return "https://canvas.northwestern.edu/courses/{}/gradebook/speed_grader?assignment_id={}&student_id={}\n".format(cid, aid, sid)
