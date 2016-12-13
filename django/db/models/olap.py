"""
Functionality for OLAP, which includes syntax for rollup, cube and grouping
sets.

Used as modifiers for aggregation, to compute the aggregation in multiple
ways, often for different permutations of the columns.

The expressions can be used along with annotations, similarly to any
aggregate-function.
"""
from django.db.models import Expression, Field


class RollUp(Expression):

    template = 'ROLLUP(%(expressions)s)'
    _output_field = Field()

    def __init__(self, *expressions, **extra):
        self.expressions = expressions
        super().__init__(**extra)

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        c = self.copy()
        c.is_summary = summarize
        c.expressions = self.expressions
        return c

    def contains_aggregate(self):
        return False

    def copy(self):
        clone = super().copy()
        clone.expressions = self.expressions
        return clone

    def as_sql(self, compiler, connection, template=None):
        template = template or self.template
        return template % {
            'expressions': self.expressions
        }

    def as_mysql(self, compiler, connection, template='%(expressions)s WITH ROLLUP'):
        return super().as_sql(compiler, connection, template=template)

    def get_group_by_cols(self):
        return []
