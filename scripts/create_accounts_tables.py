from django.apps import apps
from django.db import connection

Partner = apps.get_model('accounts', 'PartnerOrganisation')
User = apps.get_model('accounts', 'User')

existing = connection.introspection.table_names()

with connection.schema_editor() as schema_editor:
    try:
        if 'accounts_partnerorganisation' not in existing:
            schema_editor.create_model(Partner)
        else:
            print('accounts_partnerorganisation exists')
    except Exception as e:
        print('partnerorganisation create skipped:', e)
    try:
        if 'accounts_user' not in existing:
            schema_editor.create_model(User)
        else:
            print('accounts_user exists')
    except Exception as e:
        print('accounts_user create skipped:', e)
    try:
        if User.groups.through._meta.db_table not in existing:
            schema_editor.create_model(User.groups.through)
        else:
            print(f'{User.groups.through._meta.db_table} exists')
    except Exception as e:
        print('user groups through create skipped:', e)
    try:
        if User.user_permissions.through._meta.db_table not in existing:
            schema_editor.create_model(User.user_permissions.through)
        else:
            print(f'{User.user_permissions.through._meta.db_table} exists')
    except Exception as e:
        print('user permissions through create skipped:', e)

print('create_accounts_tables done')
