import urllib

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=AAA\KHODLKPDL;"
                                 "DATABASE=test;"
                                 "UID=sa;"
                                 "PWD=1")

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
