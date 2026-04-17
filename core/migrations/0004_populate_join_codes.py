from django.db import migrations
import secrets
import string


def generate_join_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def populate_join_codes(apps, schema_editor):
    Course = apps.get_model("core", "Course")

    existing_codes = set(
        Course.objects.exclude(join_code__isnull=True)
        .exclude(join_code="")
        .values_list("join_code", flat=True)
    )

    for course in Course.objects.all():
        if not course.join_code:
            code = generate_join_code()
            while code in existing_codes:
                code = generate_join_code()

            course.join_code = code
            course.save(update_fields=["join_code"])
            existing_codes.add(code)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_add_join_code_safely"),
    ]

    operations = [
        migrations.RunPython(populate_join_codes, migrations.RunPython.noop),
    ]