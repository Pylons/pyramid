def includeme(config):
    config.add_route('gameactions_pet_get_pets', '/pet',
                     view='.views.PetRESTView',
                     view_attr='GET',
                     request_method='GET',
                     permission='view',
                     renderer='json')
    config.add_route('gameactions_pet_care_for_pet', '/pet',
                     view='.views.PetRESTView',
                     view_attr='POST',
                     request_method='POST',
                     permission='view',
                     renderer='json')
                     
