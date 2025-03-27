from neo4j import GraphDatabase
import pandas as pd

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(
                database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

# connect to neo4j database, neo4j local server need to be open
conn = Neo4jConnection(uri="bolt://localhost:7687",
                       user="neo4j", pwd="12345678")


# widget 2 - top professors of keyword: for a given keyword and time period, return 10 top professors related to the keyword based on keyword-relevant citation (KRC).
def get_top_professor(keyword, start_year, end_year):
    query = f'''
    MATCH (f1:FACULTY)-[:PUBLISH]-(p:PUBLICATION)-[l:LABEL_BY]-(k:KEYWORD),
    (f2:FACULTY)-[:AFFILIATION_WITH]-(i:INSTITUTE)
    WHERE k.name = "{keyword}" AND p.year >= {start_year} AND p.year <= {end_year}  AND f1.id = f2.id
    WITH f1, SUM(p.numCitations * l.score) AS krc, i
    RETURN f1.name, i.name as institute, ROUND(krc, 2) AS citation_score
    ORDER BY citation_score DESC
    LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'f1.name': 'Professor','institute': 'Institute', 'citation_score': 'Citation Score'})
    return df

# widget 3 - top keywords of univerisity: for a given university, return top keywords based on the number of professors insterested in the keyword.
def get_top_keywords_of_univ(univ):
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) -[i:INTERESTED_IN] -> (k:KEYWORD)
        WHERE i1.name = "{univ}"
        RETURN k.name, count(DISTINCT f1.id) AS n_prof
        ORDER BY n_prof DESC
        LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'k.name': 'Keyword', 'n_prof': 'Professor Count'})
    return df


# widget 4 - top keywords of professor: for a given professor, return top keywords based on KRC.
def get_top_keywords_of_prof(prof):
    query = f'''
        MATCH (k1:KEYWORD) <- [i:INTERESTED_IN]- (f1:FACULTY) -[:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k2:KEYWORD)
        WHERE f1.name = "{prof}" AND k2.name = k1.name
        RETURN k2.name, ROUND(SUM(l.score * p.numCitations),2) AS citation_score
        ORDER BY citation_score DESC
        LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'k2.name': 'Keyword', 'citation_score': 'Citation Score'})
    return df

# list of universities
def get_univ_list():
    query = '''
        MATCH (i:INSTITUTE)
        RETURN i.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    universities = [record['name'] for record in result]
    return universities

# list of professors
def get_prof_list():
    query = '''
        MATCH (f:FACULTY)
        RETURN f.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    profs = [record['name'] for record in result]
    return profs