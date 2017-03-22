from django.db.models import Expression

__all__ = ['Filter']


class Filter(Expression):
    template = '%(expression)s FILTER (WHERE %(condition)s)'
    contains_aggregate = True

    def __init__(self, expression, condition, output_field=None):
        if not expression.contains_aggregate:
            raise TypeError('Expression must either be an aggregate function or contain an aggregate function')

        if not hasattr(condition, 'resolve_expression'):
            raise TypeError('Condition must be a class defining resolve_expression')

        super().__init__(output_field=output_field)
        self.expression = self._parse_expressions(expression)[0]
        self.condition = condition

    def _resolve_output_field(self):
        if self._output_field is None:
            self._output_field = self.expression.output_field

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        clone = self.copy()
        clone.condition = self.condition.resolve_expression(query, allow_joins, reuse, summarize, for_save)
        clone.expression = self.expression.resolve_expression(query, allow_joins, reuse, summarize, for_save)
        return clone

    def as_sql(self, compiler, connection, template=None, ):
        if connection.pg_version < 90400:
            raise NotImplementedError('PostgreSQL 9.4+ is required.')

        params = []
        expr_sql, expr_params = compiler.compile(self.expression)
        condition_sql, condition_params = compiler.compile(self.condition)
        params.extend([*condition_params, *expr_params])

        return self.template % {
            'expression': expr_sql,
            'condition': condition_sql,
        }, params

    def get_group_by_cols(self):
        return []

    def __str__(self):
        return self.template % {
            'expression': str(self.expression),
            'condition': str(self.condition),
        }

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)
