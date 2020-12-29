from subprocess import Popen, PIPE

process = Popen([r'path/to/process', 'arg1', 'arg2', 'arg3'], stdin=PIPE, stdout=PIPE)

to_program = "something to send to the program's stdin"
while process.poll() == None:  # While not terminated
    process.stdin.write(to_program)

    from_program = process.stdout.readline()  # Modify as needed to read custom amount of output
    if from_program == "something":  # send something new based on stdout
       to_program = "new thing to send to program"
    else:
       to_program = "other new thing to send to program"

print("Process exited with code {}".format(process.poll()))
