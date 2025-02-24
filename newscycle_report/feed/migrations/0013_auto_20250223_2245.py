from django.db import migrations, models
from django.utils import timezone

def set_created_defaults(apps, schema_editor):
    RSSDateTimeUpdate = apps.get_model('feed', 'RSSDateTimeUpdate')
    for instance in RSSDateTimeUpdate.objects.all():
        instance.created = instance.updated
        instance.save()

class Migration(migrations.Migration):
    dependencies = [
        ('feed', '0012_rssdatetimeupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='rssdatetimeupdate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='rssdatetimeupdate',
            options={'ordering': ['-updated']},
        ),
        migrations.RunPython(set_created_defaults),
    ]
