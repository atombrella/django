import hashlib

from django.db import NotSupportedError, connection
from django.db.backends.utils import split_identifier
from django.db.models import F
from django.db.models.sql import Query
from django.utils.encoding import force_bytes

__all__ = ['ExpressionIndexNotSupported', 'Index']


class ExpressionIndexNotSupported(NotSupportedError):
    pass


class Index:
    suffix = 'idx'
    # The max length of the name of the index (restricted to 30 for
    # cross-database compatibility with Oracle)
    max_name_length = 30

    def __init__(self, *, fields=(), name=None, db_tablespace=None):
        if not isinstance(fields, (list, tuple)):
            raise ValueError('Index.fields must be a list or tuple.')
        if not fields:
            raise ValueError('At least one field is required to define an index.')
        self.fields = list(fields)
        self.expressions = []
        self.fields_order = []

        for field in fields:
            if isinstance(field, str):
                expression = F(field[1:]).desc() if field.startswith('-') else F(field)
                self.expressions.append(expression)
                self.fields_order.append(getattr(expression, 'descending', False))
            else:
                self.expressions.append(field)
                self.fields_order.append(getattr(field, 'descending', False))

        # A list of 2-tuple with the field name and ordering ('' or 'DESC').
        self.fields_orders = [
            (field_name[1:], 'DESC') if field_name.startswith('-') else (field_name, '')
            for field_name in self.fields
        ]
        self.name = name or ''
        if self.name:
            errors = self.check_name()
            if len(self.name) > self.max_name_length:
                errors.append('Index names cannot be longer than %s characters.' % self.max_name_length)
            if errors:
                raise ValueError(errors)
        self.db_tablespace = db_tablespace

    def check_name(self):
        errors = []
        # Name can't start with an underscore on Oracle; prepend D if needed.
        if self.name[0] == '_':
            errors.append('Index names cannot start with an underscore (_).')
            self.name = 'D%s' % self.name[1:]
        # Name can't start with a number on Oracle; prepend D if needed.
        elif self.name[0].isdigit():
            errors.append('Index names cannot start with a number (0-9).')
            self.name = 'D%s' % self.name[1:]
        return errors

    def create_sql(self, model, schema_editor, using=''):
        # A Query can be used to compile expressions from the preprocessing.
        # Since a Query-object is linked to a model, a Query-object is good
        # enough. No need to use more classes. A Query compiles to SQL code
        # similar to SELECT "*"."*" FROM table, however we only care about
        # using the object to resolve the references for the columns and the

        # The Query-object also provides the resolve_ref method to get the
        # table alias
        query = Query(model)
        compiler = connection.ops.compiler('SQLCompiler')(query, connection, using)
        # This needs to be resolved to either
        columns = []

        for column_expression in self.expressions:
            expression = column_expression.resolve_expression(query)
            column_sql, params = compiler.compile(expression)
            params = tuple(map(schema_editor.quote_value, params))
            columns.append(column_sql % params)

        fields = [model._meta.get_field(field_name) for field_name, _ in self.fields_orders]
        col_suffixes = [order[1] for order in self.fields_orders]
        return schema_editor._create_index_sql(
            model, fields, name=self.name, using=using, db_tablespace=self.db_tablespace,
            col_suffixes=col_suffixes,
        )

    def remove_sql(self, model, schema_editor):
        quote_name = schema_editor.quote_name
        return schema_editor.sql_delete_index % {
            'table': quote_name(model._meta.db_table),
            'name': quote_name(self.name),
        }

    def deconstruct(self):
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        path = path.replace('django.db.models.indexes', 'django.db.models')
        kwargs = {'fields': self.fields, 'name': self.name}
        if self.db_tablespace is not None:
            kwargs['db_tablespace'] = self.db_tablespace
        return (path, (), kwargs)

    def clone(self):
        """Create a copy of this Index."""
        path, args, kwargs = self.deconstruct()
        return self.__class__(*args, **kwargs)

    @staticmethod
    def _hash_generator(*args):
        """
        Generate a 32-bit digest of a set of arguments that can be used to
        shorten identifying names.
        """
        h = hashlib.md5()
        for arg in args:
            h.update(force_bytes(arg))
        return h.hexdigest()[:6]

    def set_name_with_model(self, model):
        """
        Generate a unique name for the index.

        The name is divided into 3 parts - table name (12 chars), field name
        (8 chars) and unique hash + suffix (10 chars). Each part is made to
        fit its size by truncating the excess length.
        """
        _, table_name = split_identifier(model._meta.db_table)
        column_names = [model._meta.get_field(field_name).column for field_name, order in self.fields_orders]
        column_names_with_order = [
            (('-%s' if order else '%s') % column_name)
            for column_name, (field_name, order) in zip(column_names, self.fields_orders)
        ]
        # The length of the parts of the name is based on the default max
        # length of 30 characters.
        hash_data = [table_name] + column_names_with_order + [self.suffix]
        self.name = '%s_%s_%s' % (
            table_name[:11],
            column_names[0][:7],
            '%s_%s' % (self._hash_generator(*hash_data), self.suffix),
        )
        assert len(self.name) <= self.max_name_length, (
            'Index too long for multiple database support. Is self.suffix '
            'longer than 3 characters?'
        )
        self.check_name()

    def __repr__(self):
        return "<%s: fields='%s'>" % (self.__class__.__name__, ', '.join(self.fields))

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.deconstruct() == other.deconstruct())
