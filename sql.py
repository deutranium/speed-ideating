from functools import wraps
import sqlite3


def catch_err(f):
    """
    Wrapper for adding a try-catch block
    """

    @wraps(f)
    def _catch_err(*args, **kwargs):
        """
        add a try-catch block to func call
        """
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            print(e)

        return _catch_err

    return _catch_err


# taken from https://stackoverflow.com/q/6307761
def for_all_methods(decorator):
    """
    A decorator which decorates all methods in a class
    """

    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


@for_all_methods(catch_err)
class SQL:
    """
    Class for managing db
    """

    def __init__(self, path="./team-info.db"):
        self.conn = None
        self.setup_db(path)

    def setup_db(self, path):
        """
        Creates the db
        """
        self.conn = sqlite3.connect(path)

    def setup_table(self):
        """
        Creates the table
        """
        create_table_scoreboard = """
            create table if not exists scoreboard (
                id integer primary key,
                team_name text not null,
                score integer not null
            );
        """

        c = self.conn.cursor()
        c.execute(create_table_scoreboard)

    def populate_table(self, team_names, initial_score=20):
        """
        populates the table with id, names and an initial score
        """
        insert_sql_cmd = "insert into scoreboard(id, team_name, score) values (?, ?, ?)"

        c = self.conn.cursor()
        for idx, team_name in enumerate(team_names):
            c.execute(insert_sql_cmd, [idx, team_name, initial_score])
        self.conn.commit()

    def count_rows(self):
        """
        Returns number of rows found in db
        """
        c = self.conn.cursor()
        c.execute("select id from scoreboard")
        return len(c.fetchall())

    def get_scoreboard(self):
        """
        Returns the scoreboard
        """
        c = self.conn.cursor()
        c.execute("select * from scoreboard")
        rows = c.fetchall()
        return rows

    def update_score(self, from_team_id, to_team_id, delta):
        """
        Transfer delta points from from_team_id to to_team_id
        Returns whether the transaction was successful
        """
        c = self.conn.cursor()

        c.execute("select score from scoreboard where id=?", [from_team_id])
        from_current_score = c.fetchall()[0][0]

        c.execute("select score from scoreboard where id=?", [to_team_id])
        to_current_score = c.fetchall()[0][0]

        from_new_score = from_current_score - delta
        to_new_score = to_current_score + delta

        if from_new_score < 0:
            return False

        update_table_sql = """
            update scoreboard
            set score = ?
            where id = ?
        """
        c.execute(update_table_sql, [from_new_score, from_team_id])
        c.execute(update_table_sql, [to_new_score, to_team_id])
        self.conn.commit()

        return True

    def __del__(self):
        self.conn.close()
