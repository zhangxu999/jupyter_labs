from sqlalchemy.exc import ProgrammingError
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Sequence
from pandas import DataFrame, Series

def drop_table(engine,table_name,schema = None):
    schema = schema or ''

    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        schema = schema
    )
    
    s = "DROP TABLE IF EXISTS {schema}.{table_name} CASCADE".format(table_name = table_name, schema = schema)
    
    engine.execute(s)


def create_table(engine,table_name,column_configs, schema = None, metadata = None):
    try:
        metadata = metadata or MetaData()

        columns = [
            Column(*args,**kwargs) for
            args, kwargs in column_configs
        ]

        table = Table(
            table_name,
            metadata,
            *columns,
            schema = schema
        )
        
        engine.execute(CreateTable(table))
    except ProgrammingError as e:
        if 'already exists' in str(e):
            print('Table already exists')
        else:
            raise e

def define_tables(engine, table_configs, schema = None):
    tables = []
    metadata = MetaData()
    
    for table_name, schema, column_configs in table_configs:
        try:
            columns = [
                Column(*args,**kwargs) for
                args, kwargs in column_configs
            ]

            table = Table(
                table_name,
                metadata,
                *columns,
                schema = schema
            )
            tables.append(table)
        except ProgrammingError as e:
            if 'already exists' in str(e):
                print('Table {}.{} already exists'.format(schema,table_name))
                tables.append(None)
            else:
                raise e
    return tables, metadata

users_data = DataFrame.from_records(
    [
        (1,'jack', 'Jack Jones'),
        (2,'wendy', 'Wendy Williams')
    ],
    columns = ['id','name','fullname']
)

addresses_data = DataFrame.from_records(
    [
        {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
        {'user_id': 1, 'email_address' : 'jack@msn.com'},
        {'user_id': 2, 'email_address' : 'www@www.org'},
        {'user_id': 2, 'email_address' : 'wendy@aol.com'},
    ],
    columns = ['user_id','email_address']
)

def clear_db(engine):
    schema = 'test'
    drop_table(engine,'users',schema)
    drop_table(engine,'addresses',schema)


def reset_db(engine):
    schema = 'test'
    drop_table(engine,'users',schema)
    drop_table(engine,'addresses',schema)


    
    users_column_configs = [
        (['id',Integer],{'primary_key':True}),
        (['name',String(20)],{}),
        (['fullname',String(20)],{})
    ]

    addresses_column_configs = [
        (['id',Integer],{'primary_key':True}),
        (['user_id',None,ForeignKey('test.users.id')],{}),
        (['email_address',String(20)],{'nullable':False})
    ]

    table_configs = [
        ('users','test',users_column_configs),
        ('addresses','test',addresses_column_configs),
    ]

    (users, addresses), metadata = define_tables(engine, table_configs, schema)
    metadata.create_all(engine)    
    


    engine.execute(users.insert().values(users_data[['name','fullname']].to_dict(orient = 'records')))

    engine.execute(addresses.insert().values(addresses_data.to_dict(orient = 'records')))
    
    return users, addresses

def read_table(engine, table):
    d = engine.execute(table.select()).fetchall()
    return DataFrame.from_records(d,columns = table.c.keys())

def read_select(engine, select, **kwargs):
    d = engine.execute(select,**kwargs).fetchall()
    return DataFrame.from_records(d,columns = select.c.keys())    
