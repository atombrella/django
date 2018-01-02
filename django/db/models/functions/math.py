from django.db.models import FloatField, Func, IntegerField

__all__ = ['ArcCos', 'ArcSin', 'Cos', 'Cot', 'Log', 'Log10', 'Power', 'Sin', 'Tan']


class ArcCos(Func):
    name = 'ArcCos'
    function = 'ACOS'
    output_field = FloatField()


class ArcSin(Func):
    name = 'ArcSin'
    function = 'ASIN'
    output_field = FloatField()


class Cos(Func):
    name = 'Cos'
    function = 'COS'
    output_field = FloatField()


class Cot(Func):
    name = 'Cot'
    function = 'COT'
    output_field = FloatField()


class Log(Func):
    function = 'LOG'
    name = 'Log'
    output_field = FloatField()


class Log10(Func):
    name = 'Log10'
    function = 'LOG10'
    output_field = FloatField()


class Power(Func):
    name = 'Pow'
    function = 'POW'
    output_field = FloatField()

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='django_power', **extra_context)


class Round(Func):
    name = 'Round'
    function = 'ROUND'
    output_field = IntegerField()


class Sin(Func):
    name = 'Sin'
    output_field = FloatField()


class Sqrt(Func):
    name = 'Sqrt'
    function = 'SQRT'
    output_field = FloatField()


class Tan(Func):
    name = 'Tan'
    function = 'TAN'
    output_field = FloatField()
