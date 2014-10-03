import re
import subprocess

def offlineimap_is_running(Popen = subprocess.Popen):
    pgrep = Popen(['pgrep', 'offlineimap'], stdout = subprocess.PIPE)
    pgrep.wait()
    stdout, stderr = pgrep.communicate()
    return len(stdout) > 0

EMAIL_ADDRESS = re.compile(r'''(?:.*<)?([^@"' ]+@[^@"'> ]+)>?''')


RECEIVED_RE = re.compile(r'[^;]+; *([^;]+) \(.*')
RECEIVED_FORMAT = '%a, %d %b %Y %H:%M:%S %z'
def received_datetime(m):
    received = re.match(RECEIVED_RE, m.get_header('received')).group(1)
    localdatetime = datetime.datetime.strptime(received, RECEIVED_FORMAT)
    utcdatetime = localtime.astimezone(datetime.timezone.utc)
    return utcdatetime

MAILING_LIST_HEADERS = [
    'List-Id', # Google Groups, Mailman
    'List-Unsubscribe', # LISTSERV, "cmail.dickblick", ConstantContact, Mailchimp
    'X-Campaign', # ConstantContact, Mailchimp
    'X-CiviMail-Bounce', # CiviCRM
    'X-CampaignId', # Loopfuse and others
]
