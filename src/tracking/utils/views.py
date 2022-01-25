from tracking.models import TrackingMovement


def get_movement_as_response_data(movement: TrackingMovement):
    return {
        'tracking_movement': {
            'pk': movement.pk,
            'date_created': movement.date_created,
            'created_by': {
                'pk': movement.created_by.pk,
                'username': movement.created_by.username,
            },
            'action': movement.get_action_display(),
            'result': movement.get_result_display(),
            'envios_count': movement.envios.count(),
        }
    }
