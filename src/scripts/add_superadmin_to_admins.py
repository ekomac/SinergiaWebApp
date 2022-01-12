from django.contrib.auth.models import Group
from account.models import Account


def main():
    group = Group.objects.filter(name='Admins').first()
    admin_account = Account.objects.get(pk=1)
    admin_account.groups.add(group)
    return True


if __name__ == '__main__':
    main()


def run():
    main()
