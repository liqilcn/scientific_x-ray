import os
import sys
import queue
import pathlib
import platform
import traceback
import threading
import subprocess


def usage(error=''):
    print(error)
    print('Usage: python run.py input_filename output_filename [thread_count=1]\n',
          'Or python run.py input_dir output_dir [thread_count=1]')
    exit(1)


def input_output_check():
    try:
        if not os.path.exists(input):
            usage('Input not exists')
        elif os.path.isfile(sys.argv[1]):
            basedir = os.path.dirname(output)
            if os.path.exists(basedir):
                open(output, 'a').close()
            else:
                os.makedirs(basedir)
        else:
            if os.path.exists(output):
                if not os.path.isdir(output):
                    usage('Output invalid')
            else:
                os.makedirs(output)
    except Exception as e:
        traceback.print_exc(e)
        usage('Input or Output invalid')


def run():
    while True:
        input_filename, output_filename = q.get()
        print(command % (input_filename, output_filename))
        output_prefix, output_filename = os.path.split(output_filename)
        print(output_prefix, output_filename)
        if len(os.path.splitext(output_filename)[0]) == 1:
            output_filename = 'tmp' + output_filename
        print(command % (input_filename, os.path.join(output_prefix, output_filename)))
        subprocess.call(command % (input_filename, os.path.join(output_prefix, output_filename)), shell=True)
        if output_filename.startswith('tmp'):
            with open(os.path.join(output_prefix, output_filename), 'rb') as fin, open(os.path.join(output_prefix, output_filename[3:]), 'wb') as fout:
                fout.write(fin.read())
            os.remove(os.path.join(output_prefix, output_filename))
        q.task_done()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        sys.argv.append('1')
    if len(sys.argv) != 4:
        usage()
    input = sys.argv[1]
    output = sys.argv[2]
    input_output_check()
    thread_count = int(sys.argv[3])
    if thread_count == 0:
        thread_count = int(os.cpu_count() * 0.8)
    ABS_PATH = pathlib.Path(sys.argv[0]).absolute().parents[1]
    if platform.system() == 'Windows':
        command = 'java -Dfile.encoding=UTF-8 -cp "{abs}/src;{abs}/lib/gephi-toolkit-0.9.2-all.jar" DoLayout %s %s'.format(abs=ABS_PATH)
    else:
        command = 'java -Dfile.encoding=UTF-8 -cp "{abs}/src:{abs}/lib/gephi-toolkit-0.9.2-all.jar" DoLayout %s %s'.format(abs=ABS_PATH)
    q = queue.Queue()

    print('multi threads starting')
    for i in range(thread_count):
        threading.Thread(target=run, daemon=True).start()

    if os.path.isfile(input):
        q.put((input, output))
    else:
        for name in os.listdir(input):
            if os.path.isfile(os.path.join(input, name)) and name.endswith('.gml'):
                q.put((os.path.join(input, name), os.path.join(output, name)))
    q.join()
