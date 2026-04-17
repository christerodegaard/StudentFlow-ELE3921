from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_populate_join_codes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="join_code",
            field=models.CharField(
                max_length=8,
                unique=True,
                blank=True,
                editable=False,
            ),
        ),
    ]