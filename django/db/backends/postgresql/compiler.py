from __future__ import print_function

from django.db.models.olap import RollUp
from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):

    def get_group_by(self, select, order_by):
        cols = super().get_group_by(select, order_by)
        if self.query.group_by_rollup:
            return RollUp(cols)
        return cols


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    pass


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass
