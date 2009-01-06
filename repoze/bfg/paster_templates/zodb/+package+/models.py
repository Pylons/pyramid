from persistent.mapping import PersistentMapping

class MyApp(PersistentMapping):
    __parent__ = __name__ = None

def appmaker(root):
    if not 'myapp' in root:
        myapp = MyApp()
        root['myapp'] = myapp
        import transaction
        transaction.commit()
    return root['myapp']
