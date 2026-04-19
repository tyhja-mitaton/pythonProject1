from .models import BusinessElement, AccessRoleRule

def get_rule(user, element_name):
    print("GET_RULE USER:", user)
    print("GET_RULE ROLE:", getattr(user, "role", None))
    print("GET_RULE ELEMENT:", element_name)

    try:
        element_name = element_name.strip().lower().replace('/', '')
        element_name = element_name.strip().lower().replace('-', '_')
        element = BusinessElement.objects.get(name=element_name)

        rule = AccessRoleRule.objects.filter(
            role=user.role,
            element=element
        ).first()

        print("FOUND RULE:", rule)
        return rule

    except Exception as e:
        print("GET_RULE ERROR:", e)
        return None

def has_permission(user, element_name, action):
    print("HAS_PERMISSION USER:", user)
    print("HAS_PERMISSION ROLE:", getattr(user, "role", None))
    print("HAS_PERMISSION ELEMENT:", element_name)
    print("HAS_PERMISSION ACTION:", action)

    try:
        element = BusinessElement.objects.get(name=element_name.strip().lower().replace('-', '_'))
        rule = AccessRoleRule.objects.filter(
            role=user.role,
            element=element
        ).first()

        print("HAS_PERMISSION RULE:", rule)

        if not rule:
            return False

        if action == 'read':
            return rule.read_permission or rule.read_all_permission
        if action == 'update':
            return rule.update_permission or rule.update_all_permission
        if action == 'delete':
            return rule.delete_permission or rule.delete_all_permission
        if action == 'create':
            return rule.create_permission

        return False

    except Exception as e:
        print("HAS_PERMISSION ERROR:", e)
        return False