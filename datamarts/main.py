import os
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import sessionmaker

from .pal.load import update as pal
from .history.load import update as history
from .gnucash.load import update as gnucash
from .facebookchat.load import update as fb
from .notmuch.load import update as notmuch
from .twitter.load import update as twitter
from .branchable.load import update as branchable
from .piwik.load import update as piwik
from .muttalias.load import update as mutt
from .wtmp.load import update as wtmp

updaters = [
    # Minutely updates
    history,
    notmuch, # This one crashes on `notmuch new`.
    piwik,
    wtmp,

    # Daily updates
    fb,

    # This involves downloading a biggish file.
#   branchable,

    # These delete existing state and thus take a while.
    # Also, the data aren't updated that often.
    twitter,
    pal,
  # gnucash,
    mutt,
]

def load(engine):
    sm = sessionmaker(bind=engine)
    return notmuch(sm)

    # Import separate data marts in parallel.
    with ThreadPoolExecutor(max_workers = 8) as e:
        for updater in updaters:
            future = e.submit(updater, sm)
            future.add_done_callback(_raise)

def _raise(future):
    e = future.exception()
    if e != None:
        raise e
