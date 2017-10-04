from django.template import Variable
from django.test import SimpleTestCase


class VariableTests(SimpleTestCase):
    var1 = Variable('b')
    var2 = Variable(3)

    def test_repr(self):
        self.assertEqual(repr(self.var1), "<Variable: 'b'>")
        self.assertEqual(repr(self.var2), "<Variable: 3>")

    def test_str(self):
        self.assertEqual(str(self.var1), 'b')
        self.assertEqual(str(self.var2), 3)
