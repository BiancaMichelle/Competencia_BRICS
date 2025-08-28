from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blockchainhash',
            options={'ordering': ['-timestamp']},
        ),
    ]
