# Import the QueryBase class
try:
    from query_base import QueryBase
except ImportError:
    from .query_base import QueryBase

# Import dependencies for sql execution
try:
    from sql_execution import QueryMixin
except ImportError:
    from .sql_execution import QueryMixin


# Create a subclass of QueryBase called Team
class Team(QueryBase):

    # Set the class attribute `name` to the string "team"
    name = "team"

    # Define a `names` method that receives no arguments
    # Returns a list of tuples from an sql execution
    def names(self):
        # Query 5: team_name and team_id for all teams
        return self.query("""
            SELECT team_name, team_id
            FROM team
        """)

    # Define a `username` method that receives an ID argument
    # Returns a list of tuples from an sql execution
    def username(self, id):
        # Query 6: team_name for the team with the given id
        return self.query(f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id}
        """)

    # model_data: execute the SQL query and return a pandas DataFrame
    def model_data(self, id):
        return self.pandas_query(f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                    GROUP BY employee_id
                   )
                """)
