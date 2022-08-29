from django import forms


class MainForm(forms.Form):
    address = forms.CharField(label='Адрес', max_length=100)
    radius = forms.IntegerField(label='Радиус, км', min_value=00, max_value=500, step_size=10)

    def set_address(self, address):
        data = self.data.copy()
        data['address'] = address
        self.data = data
