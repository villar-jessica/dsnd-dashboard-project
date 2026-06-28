# Import the QueryBase class
try:
    from query_base import QueryBase
except ImportError:
    from .query_base import QueryBase

# Import dependencies needed for sql execution
# from the `sql_execution` module
try:
    from sql_execution import QueryMixin
except ImportError:
    from .sql_execution import QueryMixin


# Define a subclass of QueryBase called Employee
class Employee(QueryBase):

    # Set the class attribute `name` to the string "employee"
    name = "employee"

    # Define a method called `names` that receives no arguments
    # Returns a list of tuples from an sql execution
    def names(self):
        # Query 3: full name and employee_id for all employees
        return self.query("""
            SELECT first_name || ' ' || last_name, employee_id
            FROM employee
        """)

    # Define a method called `username` that receives an `id` argument
    # Returns a list of tuples from an sql execution
    def username(self, id):
        # Query 4: full name for the employee with the given id
        return self.query(f"""
            SELECT first_name || ' ' || last_name
            FROM employee
            WHERE employee_id = {id}
        """)

    # model_data: execute the SQL query and return a pandas DataFrame
    def model_data(self, id):
        return self.pandas_query(f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                """)
