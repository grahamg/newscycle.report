from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0013_auto_20250223_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='rssfeeditem',
            name='collected_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
