from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_remove_enrollment_unique_enrollment_user_course_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="course",
            options={"ordering": ["code", "semester"]},
        ),
        migrations.AlterModelOptions(
            name="enrollment",
            options={"ordering": ["course", "user"]},
        ),
        migrations.AddField(
            model_name="course",
            name="join_code",
            field=models.CharField(
                max_length=8,
                blank=True,
                null=True,
                editable=False,
            ),
        ),
        migrations.AddConstraint(
            model_name="course",
            constraint=models.UniqueConstraint(
                fields=("code", "semester"),
                name="unique_course_code_semester",
            ),
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(
                fields=("user", "course"),
                name="unique_user_course_enrollment",
            ),
        ),
    ]