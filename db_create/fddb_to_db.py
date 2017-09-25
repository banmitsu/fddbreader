
#!/usr/bin/python
import glob
import os, sys
import psycopg2
from configparser import ConfigParser
from PIL import Image, ImageDraw 
 
def config(filename='database.ini', section='fddb'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
 
        # create a cursor
        cur = conn.cursor()
        
 	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
     # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def insert_images(foldid, filename, width, height, channel):
    """ Connect to the PostgreSQL database server and insert images (only image info) """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        data = (foldid, filename, width, height, channel)
        #insert_stmt = (
        #          "INSERT INTO Images (foldid, originalfilename) "
        #            "VALUES (%s, %s)"
        #            )

        #cur.execute(insert_stmt, data)
        cur.callproc('add_images', data)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print('ERROR: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()

def insert_faces(filename, major_r, minor_r, angle, cx, cy, label):
    """ Connect to the PostgreSQL database server and insert faces (image + annotation info) """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        data = (filename, major_r, minor_r, angle, cx, cy, label);
        cur.callproc('add_faces', data)

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print('ERROR: {}'.format(error))
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    try:
        connect()
    except:
        pass

    root_dataset= '/volNAS/dataset/face/fddb/'

    file_list = glob.glob(os.path.join(root_dataset, 'FDDB-folds/*ellipseList.txt'))

    for foldid, each_file in enumerate(file_list):
        with open(each_file) as f:
            while True:
                line = f.readline()
                if not line:
                    break

                img_filename = line.strip()+'.jpg'

                try:
                    width, height = Image.open(os.path.join(root_dataset, img_filename)).size
                    channel = Image.open(os.path.join(root_dataset, img_filename)).layers
                except:
                    width, height, channel = 0, 0, 0

                insert_images(foldid, img_filename, width, height, channel)

                num_of_face = int(f.readline().strip())
                for face_idx in range(num_of_face):
                    line = f.readline().strip()
                    splited = line.split()
                    r1 = float(splited[0])
                    r2 = float(splited[1])
                    angle = float(splited[2])
                    cx = float(splited[3])
                    cy = float(splited[4])
                    label = int(splited[5])

                    print(img_filename, r1, r2, angle, cx, cy, label, width, height, channel)
                    insert_faces(img_filename, r1, r2, angle, cx, cy, label) 
