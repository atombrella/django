from django.contrib.postgres.aggregates import ArrayAgg, Filter
from django.db.models import Count, Q, Sum
from django.db.models.functions import Now

from . import PostgreSQLTestCase
from .models import AggregateTestModel


class FilterTestCase(PostgreSQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.obj1 = AggregateTestModel(char_field='Australia', integer_field=1000, boolean_field=True)
        cls.obj2 = AggregateTestModel(char_field='Botswana', integer_field=2000, boolean_field=True)
        cls.obj3 = AggregateTestModel(char_field='Canada', integer_field=3000, boolean_field=True)
        AggregateTestModel.objects.bulk_create([cls.obj1, cls.obj2, cls.obj3])

    def test_count_filter(self):
        qs = AggregateTestModel.objects.values('char_field').annotate(
            count=Filter(expression=Count('*'), condition=Q(integer_field__gte=2000)))
        self.assertQuerysetEqual(qs, [
            ('Australia', 0),
            ('Botswana', 1),
            ('Canada', 1),
        ], transform=lambda row: (row['char_field'], row['count']), ordered=False)

    def test_sum_filter(self):
        qs = AggregateTestModel.objects.values('boolean_field').annotate(
            sum=Sum('integer_field'),
            sum_with=Filter(expression=Sum('integer_field'), condition=Q(integer_field__gte=2000)))
        self.assertQuerysetEqual(qs, [
            (True, 6000, 5000),
        ], transform=lambda row: (row['boolean_field'], row['sum'], row['sum_with']), ordered=False)

    def test_array_agg_filter(self):
        qs = AggregateTestModel.objects.values('boolean_field').annotate(
            without_cond=ArrayAgg('char_field'),
            with_cond=Filter(expression=ArrayAgg('char_field'), condition=Q(integer_field__lte=1000))
        )
        for idx, val in zip(range(len(qs)), [({'boolean_field': True, 'with_cond': ['Australia'],
                                               'without_cond': ['Australia', 'Botswana', 'Canada']})]):
            with self.subTest(result=val):
                self.assertEqual(qs[idx], val)

    def test_repr_filter(self):
        filter = Filter(expression=Sum('value'), condition=Q(random__gte=1000))
        self.assertEqual(repr(filter), "<Filter: Sum(F(value)) FILTER (WHERE (AND: ('random__gte', 1000)))>")

    def test_invalid_expression(self):
        msg = 'Expression must either be an aggregate function or contain an aggregate function'
        with self.assertRaisesMessage(TypeError, msg):
            Filter(expression=Now(), condition=Q(hello__gte='a'))

    def test_invalid_condition_arg(self):
        msg = 'Condition must be a class defining resolve_expression'
        with self.assertRaisesMessage(TypeError, msg):
            Filter(expression=Count('*'), condition='hello')
