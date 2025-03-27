import mysql.connector
import logging

# configuration for connecting to mysql database
config = {
    'user': 'runqi',
    'password': '5453',
    'host': '127.0.0.1',
    'database': 'academicworld',
    'raise_on_warnings': True
}

class MySQLDatabase:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.exception("Exception occurred")
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logging.exception(f"Failed to execute query: {error}")
            self.connection.rollback()
            return False

    def fetch_data(self, query, values=None):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()
    
def fetch_all_keywords():
    with MySQLDatabase(config) as db:
        query = "SELECT name FROM keyword"
        result = db.fetch_data(query)
        keywords = [row[0] for row in result]

    return keywords

def fav_keywords_exists(db):
    query = "SHOW TABLES LIKE 'fav_keywords'"
    return bool(db.fetch_data(query))

def create_fav_keywords_table(db):
    query = ("""
             CREATE TABLE `fav_keywords` (
             `name` varchar(512) NOT NULL,
             PRIMARY KEY (`name`))
             """)
    if db.execute_query(query):
        logging.info("fav_keywords table created successfully")

def fetch_all_fav_keywords():
    with MySQLDatabase(config) as db:
        if not fav_keywords_exists(db):
            create_fav_keywords_table(db)

        query = "SELECT name FROM fav_keywords"
        result = db.fetch_data(query)
        fav_keywords = [row[0] for row in result]

    return fav_keywords

def add_fav_keyword(keyword):
    with MySQLDatabase(config) as db:
        query = "INSERT INTO fav_keywords (name) VALUES (%s)"
        values = (keyword, )
        if db.execute_query(query, values):
            logging.info("Favorite keyword added")


def delete_fav_keyword(keyword):
    with MySQLDatabase(config) as db:
        if not fav_keywords_exists(db):
            logging.error("Error: fav_keywords table does not exist")
            return
        query = "DELETE FROM fav_keywords WHERE name = %s"
        values = (keyword, )
        if db.execute_query(query, values):
            logging.info("Favorite keyword deleted")


# widget 5 - recommended professors: given a list of favorite keywords, recommend top profs related to the keywords based on total KRC.
def get_recommended_prof():
    with MySQLDatabase(config) as db:
        if not fav_keywords_exists(db):
            logging.error("Error: fav_keywords table does not exist")
            return
        query = ("""
                    select a.name as professor, u.name as institute, round(sum(c.num_citations*d.score),2) as total_KRC
                    from faculty a
                    join faculty_publication b
                    on a.id = b.faculty_id
                    join publication c
                    on b.publication_id = c.id
                    join publication_keyword d
                    on c.id = d.publication_id
                    join university u
                    on a.university_id = u.id
                    where d.keyword_id in (select id from keyword where name in (select name from fav_keywords))
                    group by a.id
                    order by sum(c.num_citations*d.score) desc
                    limit 5;
                """)
        
        result = db.fetch_data(query)
        recommended_prof = [{"Professor": row[0], "Institute": row[1], "Total Citation Score": row[2]} for row in result]

    return recommended_prof

# widget 6 - recommended universities: given a list of favorite keywords, recommend top universities related to the keywords, based on the sum of total KRC of the faculty. 

def get_recommended_univ():
    with MySQLDatabase(config) as db:
        if not fav_keywords_exists(db):
            logging.error("Error: fav_keywords table does not exist")
            return
        query = ("""
                select u.name as institute, count(distinct a.id) as related_prof_count, round(sum(c.num_citations*d.score),2) as total_KRC
                from faculty a
                join faculty_publication b
                on a.id = b.faculty_id
                join publication c
                on b.publication_id = c.id
                join publication_keyword d
                on c.id = d.publication_id
                join university u
                on a.university_id = u.id
                where d.keyword_id in (select id from keyword where name in (select name from fav_keywords))
                group by u.id
                order by sum(c.num_citations*d.score) desc
                limit 5
                """)
        result = db.fetch_data(query)
        recommended_univ = [{"Institute": row[0], "Related Professor Count": row[1], "Total Citation Score": row[2]} for row in result]

    return recommended_univ


# added index to the keyword table
def add_index_to_keyword_table():
    with MySQLDatabase(config) as db:
        query = "ALTER TABLE keyword ADD INDEX idx_keyword_name (name);"
        if db.execute_query(query):
            logging.info("Index added to keyword table successfully")


# added foreign key constraint to the faculty_keyword table on keyword_id
def add_foreign_key_constraint():
    with MySQLDatabase(config) as db:
        query = "ALTER TABLE faculty_keyword ADD CONSTRAINT fk_keyword_id FOREIGN KEY (keyword_id) REFERENCES keyword (id);"
        if db.execute_query(query):
            logging.info(
                "Foreign key constraint added to faculty_keyword")


# added trigger on faculty_keyword to check if score is non-negative
def add_trigger():
    with MySQLDatabase(config) as db:
        query = ("""
                 CREATE TRIGGER faculty_keyword_score_check BEFORE INSERT ON faculty_keyword 
                 FOR EACH ROW 
                 BEGIN 
                 IF NEW.score < 0 THEN 
                 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'score cannot be negative'; 
                 END IF; 
                 END
                 """)
        if db.execute_query(query):
            logging.info("Trigger added to faculty_keyword")
