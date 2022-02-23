from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from rest_framework import serializers
from envios.models import Envio
from tracking.models import TrackingMovement

# from tracking.utils.delivery import delivery_attempt


class DeliveryAttemptSerializer(serializers.ModelSerializer):

    envio_tracking_id = serializers.CharField(max_length=50, required=True)
    receiver_doc_id = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'result',
                  'envio_tracking_id', 'proof',
                  'comment', 'receiver_doc_id')
        extra_kwargs = {
            'created_by': {'required': True, },
            'result': {'required': True, },
            'envio_tracking_id': {'required': True, },
            'proof': {'required': False, },
            'comment': {'required': False, },
        }

    def check_envio_is_carried_by_author(self, data):
        author = data['created_by']
        envio_tracking_id = data['envio_tracking_id']
        envio = Envio.objects.get(tracking_id=envio_tracking_id)
        if envio.carrier != author:
            msg = "Envio is not carried by the Account trying to deliver it."
            raise serializers.ValidationError({"response": msg})

    def check_envio_is_still_moving_when_success(self, data):
        if data['result'] == TrackingMovement.RESULT_DELIVERED:
            return
        envio_tracking_id = data['envio_tracking_id']
        envio = Envio.objects.get(tracking_id=envio_tracking_id)
        if envio.status == Envio.STATUS_DELIVERED:
            msg = "Envio already delivered."
            raise serializers.ValidationError({"response": msg})

    def check_for_comment_if_result_is_other(self, data):
        result = data['result']
        if result == TrackingMovement.RESULT_OTHER:
            if ('comment' not in data or data['comment']
                    is None or data['comment'] == ""):
                msg = "Comment is required if result is other."
                raise serializers.ValidationError({"response": msg})

    def validate(self, data):
        self.check_envio_is_carried_by_author(data)
        self.check_for_comment_if_result_is_other(data)
        self.check_envio_is_still_moving_when_success(data)
        return data

    def save(self):
        author = self.validated_data['created_by']
        result = self.validated_data['result']
        envio_tracking_id = self.validated_data['envio_tracking_id']
        receiver_doc_id = self.validated_data['receiver_doc_id']
        proof = self.validated_data.get('proof', None)
        comment = self.validated_data.get('comment', "")
        movement = TrackingMovement(
            created_by=author,
            from_carrier=author,
            action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
            result=result,
            proof=proof,
            comment=comment,
        )
        movement.save()

        if proof is not None:
            movement.proof = proof

            url = os.path.join(settings.TEMP, str(proof))
            storage = FileSystemStorage(location=url)

            with storage.open('', 'wb+') as destination:
                for chunk in proof.chunks():
                    destination.write(chunk)
                destination.close()

            os.remove(url)
            movement.save()

        envio = Envio.objects.filter(tracking_id=envio_tracking_id).first()

        # Add envios to the movement
        movement.envios.add(envio)

        if result == TrackingMovement.RESULT_DELIVERED:
            envio.status = Envio.STATUS_DELIVERED
            envio.carrier = None
            envio.deposit = None
            envio.date_delivered = movement.date_created
            envio.updated_by = movement.created_by
            envio.receiver_doc = receiver_doc_id
            envio.save()
        return movement, envio
