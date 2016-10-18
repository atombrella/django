from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):
    def as_subquery_condition(self, alias, columns, compiler):
        qn = compiler.quote_name_unless_alias
        qn2 = self.connection.ops.quote_name
        sql, params = self.as_sql()
        return '(%s) IN (%s)' % (', '.join('%s.%s' % (qn(alias), qn2(column)) for column in columns), sql), params


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    def as_sql(self):
        """
        The default SQL required for the
        """
        if self.connection.features.supports_on_conflict:
            pass
        return super(SQLInsertCompiler, self).as_sql()

    def assemble_as_sql(self, fields, value_rows):
        return super().assemble_as_sql(fields, value_rows)


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass
