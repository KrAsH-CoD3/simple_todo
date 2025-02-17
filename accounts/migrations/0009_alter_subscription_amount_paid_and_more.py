# Generated by Django 5.1.1 on 2024-12-23 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_Added_subscription_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.CharField(choices=[('free', 'Free Plan'), ('premium', 'Premium Plan')], max_length=10),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('expired', 'Expired')], default='expired', max_length=10),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(condition=models.Q(('status__in', ['expired', 'pending'])), fields=('user', 'plan'), name='unique_pending_subscription_per_user_plan'),
        ),
    ]
