# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # SQLAlchemy Practice
#
# ## Set-Up
#
# Begin by importing packages.

# %%
# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String # datatypes
from sqlalchemy import ForeignKey

from sqlalchemy import and_, or_, asc, desc, between # conjunctions
from sqlalchemy import text # for textual statements

from sqlalchemy.sql import select 
from sqlalchemy.sql import alias # represents 'as' in sql
from sqlalchemy.sql import func # standard sql functions

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship # describe relationships between tables
from sqlalchemy.orm import sessionmaker, Query

# Misc
import os


# %% [markdown]
# In the course of the notebook some files are created. We delete them if they already exist for a clean slate.

# %%
def remove_file(path):
    if os.path.isfile(path):
        os.remove(path)

        
COLLEGE_DB_PATH = 'college.db'
SALES_DB_PATH = 'sales.db'

remove_file(COLLEGE_DB_PATH)
remove_file(SALES_DB_PATH)

# %% [markdown]
# **SQLAlchemy** is a Python toolkit for dealing with databases. It has two ways of interacting with them.
#
# **SQLAlchemy Core:** Uses SQL Expression Language that provides schema-centric usage paradigm
# - **SQL Expression Language** allows you represent structures in a relational database using Python
# - You can specify SQL statements in Python and use it directly
# - This is the closest part to raw SQL in SQLAlchemy
#
# **SQLAlchemy ORM:** Allows classes to be mapped to tables in the database to provide domain-centric usage.

# %% [markdown]
# ## Resources
#
# Quick Guide: https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_quick_guide.htm

# %% [markdown]
# ## SQLAlchemy Core
#
# ### Connecting to Database
#
# **Engine:** Class that provides a source of database connectivity and behaviour.
#
# **MetaData:** A collection of *Table* objects and associated schema constructs
# - Has an optional binding to an engine

# %%
# Define local sqlite database to be hosted in repo
engine = create_engine(
    os.path.join('sqlite:///', COLLEGE_DB_PATH), # Different syntax for different database types
    echo = True # sets up SQLAlchemy logging - print SQL used
)
meta = MetaData()

# Define table
students = Table(
   'students', meta, 
   Column('id', Integer, primary_key = True), 
   Column('name', String), 
   Column('lastname', String), 
)

# Use engine object to create table and other objects and store info in metadata
# This creates the local database
meta.create_all(engine)

# %% [markdown]
# **SQL expressions:** Constructed by using methods on tables
# - Print corresponding SQL code using `str(<exp>)` (doesn't store specific values)
# - Specific values are stored in bind parameter which is visible in compiled form - access using `.compile().params`
# - Insert bound parameters into query using `.compile(compile_kwargs={"literal_binds": True})`
#
# **Connection:** Represents an active *DBAPI* (Python Database API) connection
# - Run expressions by passing to `execute(<exp>)` method on connection
# - This also returns `ResultProxy` object that holds information

# %%
# Insert expression
ins = students.insert().values(name = 'Ravi', lastname = 'Kapoor')

# Equivalent SQL insert statement (without specific values)
print(str(ins))

# Access specific parameters
print(ins.compile().params)

# Parameters in Query
print(ins.compile(compile_kwargs={"literal_binds": True}))

# %%
# Create connection to database
conn = engine.connect()
result = conn.execute(ins)

# Check last set of params inserted
print(result.last_inserted_params())

# %%
# Can insert many rows at once by passing list of dictionaries
conn.execute(students.insert(), [
   {'name':'Rajiv', 'lastname' : 'Khanna'},
   {'name':'Komal','lastname' : 'Bhandari'},
   {'name':'Abdul','lastname' : 'Sattar'},
   {'name':'Priya','lastname' : 'Rajhans'},
]);

# %% [markdown]
# ### Basic Select Statements
#
# **Select:** Either a method on table or function with table as argument
# - Limit columns by passing specific columns as argument of `select()` function
# - Columns referenced using `<table>.c.<column>` (`c` is an alias for 'column')
# - Rename columns using `.label()` method on columns in `select`
#
# **ResultProxy:** Object returned by executing select
# - Is iterable with items corresponding to rows
# - Has other methods for accessing results: `fetchone()`, `fetchall()`,...

# %%
# Select all
s = students.select()
print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

# Run expression
result = conn.execute(s)
print('')

for row in result:
    print(row)

# %%
# Alternative syntax
s = select(students)
print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

# Run expression
result = conn.execute(s)
result.fetchall()

# %%
# Specific columns
s = select(
    students.c.name, 
    students.c.lastname.label('surname')
)
print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

# Run expression
result = conn.execute(s)
result.fetchall()

# %% [markdown]
# ### Where Clauses
#
# **Where:** Use `.where()` method on `select` and pass column conditions
# - Use `where(_and(<cond1>, <cond2>))` for multiple conditions
# - Use `where(between(<col>, <val1>, <val2>)` for between
# - Use `table.c.column.is_(True)` for `IS true`, `.is_(None)` for `IS NULL`, and `.isnot(None)` for `IS NOT NULL`

# %%
# Select first 3 rows
s = students.select().where(students.c.id <= 3)
print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

print('Params: ', s.compile().params, '\n')

result = conn.execute(s)
print('')
for row in result:
    print(row)

# %%
# Select Ravi in first 3 rows
s = students.select().where(
    and_(
        students.c.id <= 3,
        students.c.name == 'Ravi'
    )
)
print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

print('Params: ', s.compile().params, '\n')

result = conn.execute(s)
print('')
for row in result:
    print(row)

# %%
# Select students with 2nd and 3rd ids
s = students.select().where(
    between(
        students.c.id,
        2,
        3
    )
)

print('Equivalent SQL')
print('--------------')
print(str(s), '\n')

print('Params: ', s.compile().params, '\n')

result = conn.execute(s)
print('')
for row in result:
    print(row)

# %% [markdown]
# ### Textual SQL
#
# **TextClause:** Represents an SQL statement directly
# - Constructed by passing SQL query into `text(<string>)`
# - Parameters are denoted by colons and passed as kwargs into `execute()`
# - Good when SQL is known and static

# %%
s = text('SELECT * FROM students WHERE students.id <= :x AND students.name = :y')
result = conn.execute(s, x=3, y='Ravi')
print('')

for row in result:
    print(row)

# %% [markdown]
# ### Some Common Operations
#
# **Alias:** Represents 'AS' in SQL statements
# - There is a difference between the name of the variable representing alias table and the alias
#
# **Order By:** Use `order_by(asc(<col>))` or `order_by(desc(<col>))` methods on select
#
# **Functions:** Standard SQL functions are accessed through `func`
# - Ex: `func.now()`, `func.count()`, `func.max()`
#
# **Generate Series:** Accessed by `func.generate_series(<start>, <stop>, <interval>)`
# - Acts a little strangely because it is both a table and a column of that table: use `.column` method to refer to the *column*

# %%
# Variable st represents students table aliased as 'a'
st = students.alias('a')
print('Original table name: ', students.name)
print('Alias table name: ', st.name)
print('')

# Run select all against aliased table
s = st.select().where(st.c.id == 1)
result = conn.execute(s)
result.fetchall()

# %%
# Select students in alphabetical order
s = select(students).order_by(
    asc(students.c.name)
)
print(str(s))

# %%
# Count rows in table
s = select(func.count(students.c.id))
print(str(s))

# %%
# Generate series
# SQLite doesn't support generate_series by default so can't actually run this
gs = func.generate_series(1, 10, 1).alias('num')
s = select(gs.column).select_from(gs)
print(str(s))

# %% [markdown]
# ### Working with Multiple Tables

# %%
# Define new table
addresses = Table(
   'addresses', meta, 
   Column('id', Integer, primary_key = True), 
   Column('st_id', Integer, ForeignKey('students.id')), # Foreign key to students table
   Column('postal_add', String), 
   Column('email_add', String)
)

# Create the table
meta.create_all(engine)

# Populate new table
conn.execute(addresses.insert(), [
   {'st_id':1, 'postal_add':'Shivajinagar Pune', 'email_add':'ravi@gmail.com'},
   {'st_id':1, 'postal_add':'ChurchGate Mumbai', 'email_add':'kapoor@gmail.com'},
   {'st_id':3, 'postal_add':'Jubilee Hills Hyderabad', 'email_add':'komal@gmail.com'},
   {'st_id':5, 'postal_add':'MG Road Bangaluru', 'email_add':'as@yahoo.com'},
   {'st_id':2, 'postal_add':'Cannought Place new Delhi', 'email_add':'admin@khanna.com'},
]);

# %% [markdown]
# **Implicit Joins:** Simple implicit join by passing both tables as arguments of `select` and defining join condition in `where` clause

# %%
# Select all from both joining on foreign key
s = select(
    students,
    addresses
).where(
    students.c.id == addresses.c.st_id
)
print(str(s))

# %% [markdown]
# **Join:** Method on tables
# - Use `select_from()` method on `select` to explicitly set left hand side of join
# - Can be multiple ways of phrasing
# - Just specifying table name in `select` is equivalent to all columns from that table

# %%
# Join on its own
j = students.join(
    addresses,
    students.c.id == addresses.c.st_id,
    isouter = True # outer join - default is false
)
print(str(j))

# %%
# As part of select statement
s = select(
    students.c.name,
    students.c.lastname,
    addresses
).select_from(
    j # equivalent to block commented code below
    # students.join(
    #     addresses,
    #     students.c.id == addresses.c.st_id,
    #     isouter=True
    # )
)
print(str(s))

# %%
# An equivalent formulation
s = select(
    students.c.name,
    students.c.lastname,
    addresses
).select_from(
    students
).join(
    addresses,
    students.c.id == addresses.c.st_id,
    isouter=True
)
print(str(s))

# %% [markdown]
# ## SQLAlchemy ORM
#
# **SQLAlchemy ORM:** Main objective it to associate user-defined Python classes with databases and objects with rows
# - Is constructed on top of SQL Expression Language
# - High-level and abstracted usage of the Expression Language

# %% [markdown]
# ### Declaring Mappings
#
# **Declarative System:** Classes created include directives to describe actual database table they are mapped to.
#
# **Declarative Base:** Class that stores catalogue of classes and mapped tables in Declarative system
# - Usually only one instance
# - Has a `MetaData` object as an attribute
#
# **Mapped Classes:** Subclasses of declarative base that will be mapped to tables
# - Must include `__tablename__` attribute giving name of corresponding table
# - Includes `Column`s with their datatypes
#
# **Session:** Handle to the database - it encapsulates a single connection to the DB
# - `Session` class defined by the engine and a session object is an instantiation of this

# %%
# Create engine that describes database
engine = create_engine(
    os.path.join('sqlite:///', SALES_DB_PATH),
    echo = True
)
Base = declarative_base()

class Customers(Base):
   __tablename__ = 'customers'
   id = Column(Integer, primary_key=True)

   name = Column(String)
   address = Column(String)
   email = Column(String)

# Uses metadata of declarative base to turn engine into source of connection
# Issues create table statements for tables that don't yet exist
Base.metadata.create_all(engine)

# %% [markdown]
# Now create a session

# %%
Session = sessionmaker(bind=engine)
session = Session()

# %% [markdown]
# **Adding Objects:** Equivalent to inserting rows
# - Instantiate an instance of mapped class and call `add()` method on session
# - Transactions are pending until flushed using `commit()` method on session

# %%
# Add row to customers table
c1 = Customers(
    name = 'Ravi Kumar',
    address = 'Station Road Nanded',
    email = 'ravi@gmail.com'
)
session.add(c1)
session.commit()

# %%
# Can add multiple at once by passing list
session.add_all([
   Customers(name = 'Komal Pande', address = 'Koti, Hyderabad', email = 'komal@gmail.com'), 
   Customers(name = 'Rajender Nath', address = 'Sector 40, Gurgaon', email = 'nath@gmail.com'), 
   Customers(name = 'S.M.Krishna', address = 'Budhwar Peth, Pune', email = 'smk@gmail.com')]
)
session.commit()

# %% [markdown]
# ### Basic Select Statements
#
# **Query:** SELECT statements are generated by query objects
# - Query objects can be generated by `query(<mappedClass>)` method on Session
# - Or by instantiating `Query` class directly through `Query(<mappedClass>, <session>)`
# - Limit columns by passing specific column attributes as argument of `query()`
# - Rename columns using `label()` method on columns
# - Can call `str(<query>)` to get equivalent SQL statement
# - Convert to equivalent Core Select object via `statement` attribute - then use compile to get params
#
# **Accessing Results:**
# - *Directly:* Query objects are iterable with items corresponding to rows
#     - If whole MappedClass selected in query then items are mappedClass instances
#     - If individual columns selected then items are of column dtype (can still be accessed like a dict with column name)
#     - I think the query is only run against the database when iteration starts?
# - *`all`:* Method on query object that runs the query and returns list of results
#     - Valuable because it gives snapshot of query run that is stored - accessing directly from query object multiple times is inefficient and results may change
# - *Get:* Quickly retrieve row from Query object by primary key using `get(<primary_key>)` method

# %%
# Select all
q = session.query(Customers)
print('Equivalent SQL')
print('--------------')
print(str(q))
print('')

# Print results
for row in q:
    print('id: ', row.id, ', name: ', row.name, ', address: ', row.address, ', email: ', row.email)

# %%
# Limit columns
q = session.query(
    Customers.id,
    Customers.name.label('full_name')
)
print('Equivalent SQL')
print('--------------')
print(str(q))
print('')

result = q.first()
print('\nFirst result: ', result)
print('Data types: ', (type(result.id), type(result.full_name)))

# %%
# Run query and store results in list
q = session.query(Customers)
print('Query is run now:')
result = q.all()
print('\nResults are printed now:')

# Print results
for row in result:
    print('id: ', row.id, ', name: ', row.name, ', address: ', row.address, ', email: ', row.email)

# %%
# Alternative syntax
q = Query(Customers, session)
print(str(q))
print('')

result = q.all()

# %%
# Equivalent Select object
q = session.query(Customers)
type(q.statement)

# %%
# Query with parameters by compile select object
print(q.statement.compile(compile_kwargs={"literal_binds": True}))

# %%
# Customer with id = 2
q = session.query(Customers)
result = q.get(2)
print('Name: ', result.name)

# %% [markdown]
# ### WHERE Clauses
#
# **Filters:** WHERE clauses are applying using `filter(<cond>)` method on query objects
# - Columns are referenced using corresponding attribute of class
# - `str(<query>)` doesn't show specific values - access by converting to Core Select object and using `.compile().params`
#
# **Filter Operators:** Apply to columns in `filter`
# - Ex: `.like()`, `.in_(<list>)`, `or_(<cond1>, <cond2>)`, `and_(<cond1>, <cond2>)` (the `and_` is actually unnecessary, can just separate conditions with commas in `filter()`)

# %%
# Rows with id > 2
q = session.query(Customers).filter(Customers.id > 2)
print('Equivalent SQL')
print('--------------')
print(str(q))
print('')
print('Params: ', q.statement.compile().params)

# %%
# Query with AND condition
q = session.query(Customers).filter(
    Customers.id>2,
    Customers.name.like('Ra%')
)
print(str(q))

# %%
# Equivalent formulation
q = session.query(Customers).filter(and_(
    Customers.id>2,
    Customers.name.like('Ra%')
))
print(str(q))

# %% [markdown]
# ### Textual SQL
#
# **TextClauses in ORM:** Apply `TextClause`s from Core to Query objects flexibly
# - Can apply using `from_statement` method on Query object
# - `filter` can automatically translate into WHERE clause - this way specific values are stores in `str(<query>)`
# - Bind parameters using colon syntax and `params()` method on Query object

# %%
# Select all and display first result
stmt = text('SELECT * FROM customers')
q = session.query(Customers).from_statement(stmt)
print('Query SQL: ', str(q))
print('')

result = q.first()
print('')
print('First result name: ', result.name)

# %%
# Filter with textual SQL
q = session.query(Customers).filter(text('id == 4'))
print('Query SQL')
print('---------')
print(str(q))
print('')

result = q.one() # Throws an error if more than one result
print('')
print('Unique result name: ', result.name)

# %%
# Filter with textual SQL and parameter binding
q = session.query(Customers).filter(text('id == :id')).params(id = 4)
print('Query SQL')
print('---------')
print(str(q))
print('')

# Print params
print('Bound params: ', q.statement.compile().params)
print('')

result = q.one() # Throws an error if more than one result
print('')
print('Unique result name: ', result.name)


# %% [markdown]
# ### Working with Multiple Tables
#
#

# %%
# Define new MappedClass
class Invoices(Base):
   __tablename__ = 'invoices'
   
   id = Column(Integer, primary_key = True)
   custid = Column(Integer, ForeignKey('customers.id'))
   invno = Column(Integer)
   amount = Column(Integer)
   customer = relationship("Customers", back_populates = "invoices")


# Add relationship to Customers MappedClass
Customers.invoices = relationship(
    "Invoices",
    order_by = Invoices.id,
    back_populates = "customer"
)

# Create tables that don't exist yet
Base.metadata.create_all(engine)

# %%
# Create new customer
c1 = Customers(
    name = "Gopal Krishna",
    address = "Bank Street Hydarebad",
    email = "gk@gmail.com"
)

# Can create invoices for customer by passing list as invoices attribute
c1.invoices = [
    Invoices(invno = 10, amount = 15000),
    Invoices(invno = 14, amount = 3850)
]

# Adding customer automatically adds invoices as well
session.add(c1)
session.commit()

# %%
# Select all rows from Invoices table
q = session.query(Invoices)
result = q.all()
print('\nInvoices:')

for row in result:
    print('id :', row.id, ', cust_id:', row.custid, ', amount: ', row.amount)

# %%
# Add more rows
rows = [
   Customers(
      name = "Govind Pant", 
      address = "Gulmandi Aurangabad",
      email = "gpant@gmail.com",
      invoices = [
          Invoices(invno = 3, amount = 10000), 
          Invoices(invno = 4, amount = 5000)
      ]
   ),

   Customers(
      name = "Govind Kala", 
      address = "Gulmandi Aurangabad", 
      email = "kala@gmail.com", 
      invoices = [
          Invoices(invno = 7, amount = 12000),
          Invoices(invno = 8, amount = 18500)
      ]
   ),

   Customers(
      name = "Abdul Rahman", 
      address = "Rohtak", 
      email = "abdulr@gmail.com",
      invoices = [
          Invoices(invno = 9, amount = 15000), 
          Invoices(invno = 11, amount = 6000)
       ]
   )
]

session.add_all(rows)
session.commit()

# %% [markdown]
# **Implicit Join:** Pass both mapped classes to `query()` and specify join condition in `filter()`
# - If full classes are passed then items in `Query` iterable are instances of classes
# - If certain columns passed then items are objects of column datatype

# %%
# Select * on implicit join
q = session.query(Customers, Invoices).filter(Customers.id == Invoices.custid)
print('Equivalent SQL')
print('--------------')
print(str(q))
print('')

results = q.all()
print('')
print('First result: ', results[0])

print('\nIterating over all results:')
for c, i in results:
    print('ID: {} Name: {} Invoice No: {} Amount: {}'.format(c.id,c.name, i.invno, i.amount))

# %%
# Select certain columns on implicit join
q = session.query(
    Customers.id,
    Customers.name,
    Invoices.invno,
    Invoices.amount
).filter(Customers.id == Invoices.custid)
print('Equivalent SQL')
print('--------------')
print(str(q))
print('')

results = q.all()
print('')
print('First result: ', results[0])

print('\nIterating over all results:')
for row in results:
    print('ID: {} Name: {} Invoice No: {} Amount: {}'.format(row.id, row.name, row.invno, row.amount))

# %% [markdown]
# **Join:** `join` method on Query object syntax `join(<mappedClass>, <cond1>)`
# - `outerjoin` method for left outer join
# - Condition can be dropped for join on foreign keys
# - Can join with Table objects from Core (see subquery below)
# - Use `select_from()` method on query to explicitly set left side of join

# %%
# Just select customers.
q = session.query(Customers).join(
    Invoices,
    Customers.id == Invoices.custid
)
print(str(q))

# %%
# Select all
q = session.query(
    Customers,
    Invoices
).join(
    Invoices,
    Customers.id == Invoices.custid
)
print(str(q))

# %%
# Explicitly set left side of join
q = session.query(
    Customers.name,
    Invoices.amount
).select_from(
    Customers
).outerjoin(
    Invoices,
    Customers.id == Invoices.custid
)
print(str(q))

# %% [markdown]
# **Subqueries:** Created by `subquery()` method on Query object, acts like a Table object from Core
# - Useful to combine with `alias()`

# %%
# Create subquery object - acts like a table
sub = session.query(
   Invoices.custid, func.count('*').label('invoice_count')
).group_by(Invoices.custid).subquery().alias('i')
print(str(sub))
print('\nTable alias: ', sub.name)

# %%
# Use subquery in outer query
q = session.query(
    Customers,
    sub.c.invoice_count # Use syntax for Tables
).outerjoin(
    sub,
    Customers.id == sub.c.custid
).order_by(Customers.id)
print(str(q))
