from django import forms

class EnterURLForm(forms.Form):
    url = forms.URLField(label="URL", required=True)

    pag_choices = (
                ('10', '10 primeiros'),
                ('15', '15 primeiros'),
                ('20', '20 primeiros'),
                ('25', '25 primeiros'),
                ('30', '30 primeiros'),
                ('35', '35 primeiros'),
                ('-1', 'Todos'),
                )

    pag = forms.ChoiceField(label="Resultados", required=True, choices=pag_choices)

    def clean_url(self):
        data = self.cleaned_data['url']

        return data
