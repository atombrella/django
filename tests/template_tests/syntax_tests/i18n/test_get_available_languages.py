from django.template import TemplateSyntaxError
from django.test import SimpleTestCase

from ...utils import setup


class GetAvailableLanguagesTagTests(SimpleTestCase):
    libraries = {'i18n': 'django.templatetags.i18n'}

    @setup({'i18n12': '{% load i18n %}'
                      '{% get_available_languages as langs %}{% for lang in langs %}'
                      '{% if lang.0 == "de" %}{{ lang.0 }}{% endif %}{% endfor %}'})
    def test_i18n12(self):
        output = self.engine.render_to_string('i18n12')
        self.assertEqual(output, 'de')

    @setup({
        'invalid_template': '{% load i18n %}'
        '{% get_available_languages %}'
    })
    def test_no_args(self):
        msg = "get_available_languages' requires 'as variable' (got ['get_available_languages'])"
        with self.assertRaisesMessage(TemplateSyntaxError, msg):
            self.engine.render_to_string('invalid_template')

    @setup({
        'invalid_template': '{% load i18n %}'
        '{% get_available_languages as %}'
    })
    def test_only_as_arg(self):
        msg = "get_available_languages' requires 'as variable' (got ['get_available_languages', 'as'])"
        with self.assertRaisesMessage(TemplateSyntaxError, msg):
            self.engine.render_to_string('invalid_template')
