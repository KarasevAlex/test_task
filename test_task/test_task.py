import datetime, os
import psycopg2.extensions
import json
from threading import Thread
from Queue import PriorityQueue
from config import Config

class ItemHandler(Thread):
    path = None
    data = None
    logged_at = None

    def __init__(self, config):
        Thread.__init__(self)
        self.path = config.path

    def write_log(self):
        mode = 'a' if os.path.exists(self.path) else 'w'
        with open(self.path, mode) as f:
            f.write("%s %s\n" % (self.logged_at, json.dumps(self.data[1])))

    def run(self):
        while True:
            if not queue.empty():
                self.data = queue.get()
                self.logged_at = datetime.datetime.now().isoformat()
                self.write_log()
                self.update_logged_time()

    def update_logged_time(self):
        db.execute("UPDATE item SET logged_at='%s' WHERE id=%s" % (self.logged_at, self.data[0]))

class DB(Thread):
    conn = None
    curs = None

    def __init__(self, config):
        Thread.__init__(self)
        self.conn = psycopg2.connect(database=config.database, user=config.user, password=config.password)
        self.curs = self.conn.cursor()

    def execute(self, query):
        self.curs.execute(query)
        self.conn.commit()

    def run(self):
        self.execute("LISTEN item_change;")
        while True:
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop()
                item = json.loads(notify.payload)
                queue.put((item['id'], item))



if __name__ == '__main__':
    db = DB(Config)
    queue = PriorityQueue()

    itemHandler = ItemHandler(Config)

    db.start()
    itemHandler.start()