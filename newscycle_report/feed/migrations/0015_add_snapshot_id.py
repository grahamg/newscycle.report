from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0014_modify_collected_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='rssfeeditem',
            name='snapshot_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
