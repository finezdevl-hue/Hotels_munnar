from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hotels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HotelEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(default='Staff', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('can_view_bookings',    models.BooleanField(default=True)),
                ('can_manage_bookings',  models.BooleanField(default=False)),
                ('can_view_rooms',       models.BooleanField(default=True)),
                ('can_manage_rooms',     models.BooleanField(default=False)),
                ('can_view_guests',      models.BooleanField(default=True)),
                ('can_view_reviews',     models.BooleanField(default=True)),
                ('can_manage_reviews',   models.BooleanField(default=False)),
                ('can_edit_hotel_info',  models.BooleanField(default=False)),
                ('can_manage_employees', models.BooleanField(default=False)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='employee_profile',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('hotel', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='employees',
                    to='hotels.hotel',
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_employees',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
