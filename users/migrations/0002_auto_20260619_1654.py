from django.db import migrations


def create_admin(apps, schema_editor):

    User = apps.get_model(
        'users',
        'User'
    )

    if not User.objects.filter(
        username='admin'
    ).exists():

        User.objects.create_superuser(
            username='admin',
            email='admin@cityops.com',
            password='admin123',
            role='ADMIN'
        )


def delete_admin(apps, schema_editor):

    User = apps.get_model(
        'users',
        'User'
    )

    User.objects.filter(
        username='admin'
    ).delete()



class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [

        migrations.RunPython(
            create_admin,
            delete_admin
        ),

    ]