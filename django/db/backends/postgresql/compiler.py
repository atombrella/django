from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):
    pass


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    pass


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    # def as_sql(self):
    #     self.pre_sql_setup()
    #     if not self.query.values:
    #         return '', ()
    #     qn = self.quote_name_unless_alias
    #     values, update_params = [], []
    #     for field, model, val in self.query.values:
    #         if hasattr(val, 'resolve_expression'):
    #
    #             val = val.resolve_expression(self.query, for_save=True)
    #             if
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass
