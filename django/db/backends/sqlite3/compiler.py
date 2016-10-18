from django.db.models.sql import compiler


__all__ = ['SQLAggregateCompiler', 'SQLDeleteCompiler', 'SQLInsertCompiler',
           'SQLUpdateCompiler', 'SQLCompiler']


class SQLCompiler(compiler.SQLCompiler):
    pass


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):

    def as_sql(self):
        pass


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass
