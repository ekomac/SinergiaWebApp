from tracking.models import TrackingMovement


def get_movement_as_response_data(movement: TrackingMovement, *args, **kwargs):
    result = {
        'tracking_movement': {
            'pk': movement.pk,
            'date_created': movement.date_created,
            'created_by': {
                'pk': movement.created_by.pk,
                'username': movement.created_by.username,
                'full_name': movement.created_by.full_name,
                'email': movement.created_by.email,
            },
            'action': {
                'key': movement.action,
                'display': movement.get_action_display(), },
            'result': {
                'key': movement.result,
                'display': movement.get_result_display(),
            },
            'envios_count': movement.envios.count(),
        }
    }
    print(movement.proof)
    if (movement.proof is not None
            and len(str(movement.proof)) > 0
            and kwargs.get('request', None) is not None):
        url = str(
            kwargs['request'].build_absolute_uri(movement.proof.url))
        if '?' in url:
            url = url[:url.rfind('?')]
        result['tracking_movement']['proof'] = url
    if movement.comment is not None and movement.comment != "":
        result['tracking_movement']['comment'] = movement.comment
    return result
