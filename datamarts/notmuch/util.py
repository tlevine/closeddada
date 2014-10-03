import re
import subprocess

def offlineimap_is_running(Popen = subprocess.Popen):
    pgrep = Popen(['pgrep', 'offlineimap'], stdout = subprocess.PIPE)
    pgrep.wait()
    stdout, stderr = pgrep.communicate()
    return len(stdout) > 0

EMAIL_ADDRESS = re.compile(r'''(?:.*<)?([^@"' ]+@[^@"'> ]+)>?''')
