from tinydb import TinyDB, Query
import os
from utilscbb.constants import dbFileName,PAdbFileName, dbFileNameCopy, cacheFileNameCopy, PAdbFileNameCopy, PAcacheFileNameCopy
import shutil

dbfile = os.path.join(os.getcwd(), dbFileName)
PAdbfile = os.path.join(os.getcwd(), PAdbFileName)
PAdbfilecopy = os.path.join(os.getcwd(), PAdbFileNameCopy)

def copy_file(src_path,dest_path):
    """
    Copy a file from source path to destination path.

    Parameters:
    - src_path (str): The path of the source file.
    - dest_path (str): The path where the copy should be created.
    """
    try:
        shutil.copy2(src_path, dest_path)
        print(f"File copied successfully from {src_path} to {dest_path}")
    except FileNotFoundError:
        print(f"Error: Source file {src_path} not found.")
    except Exception as e:
        print(f"Error: {e}")
    

def delete_file(file_path):
    """
    Delete a file at the specified path.

    Parameters:
    - file_path (str): The path of the file to be deleted.
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted successfully.")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"Error: {e}")



def get_db_pa():
    db = TinyDB(PAdbfilecopy)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable
    

def get_db():
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
    return query,teamsTable



try:
    db = TinyDB(dbfile)
    query = Query()
    teamsTable = db.table('teams')
except:
    pass