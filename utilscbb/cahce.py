from tinydb import TinyDB, Query
from tinydb.operations import set
import os
import threading
from utilscbb.constants import PAcacheFileName,cacheFileName



file_lock = threading.Lock()
def get_cache():
    dbfile = os.path.join(os.getcwd(), cacheFileName)
    db = TinyDB(dbfile)
    query = Query()
    cache = db.table('cache')
    return query,cache

#update cache for PA
def get_pa_cache():
    dbfile = os.path.join(os.getcwd(), PAcacheFileName)
    db = TinyDB(dbfile)
    query = Query()
    cache = db.table('cache')
    return query,cache