from tinydb import TinyDB, Query
from tinydb.operations import set
import os
import threading



file_lock = threading.Lock()
def get_cache():
    dbfile = os.path.join(os.getcwd(), "cache.json")
    db = TinyDB(dbfile)
    query = Query()
    cache = db.table('cache')
    return query,cache