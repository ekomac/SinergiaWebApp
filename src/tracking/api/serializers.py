from django.conf import settings
from rest_framework import serializers

from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from places.models import Partido, Town, Zone

from tracking.models import TrackingMovement
from tracking.tracking_funcs import withdraw

MIN_COMMENT_LENGTH = 10
MAX_COMMENT_LENGTH = 200
NOT_ZONE_ERROR = "La zona con id {id} no existe."
NOT_PARTIDO_ERROR = "El partido con id {id} no existe."
NOT_TOWN_ERROR = "La localidad con id {id} no existe."


class WithdrawCreateSerializer(serializers.ModelSerializer):

    WHAT_TO_WITHDRAW_OPTIONS = ('all', 'one', 'by_filter',)
    what_to_withdraw_error = "El tipo de retiro no es válido. Los " + \
        f" admitidos son: {WHAT_TO_WITHDRAW_OPTIONS}"
    FILTER_BY_OPTIONS = ('zone', 'partido', 'town',)
    filter_by_error = "El filtro '{used_filter}' no es válido. " +\
        "Los admitidos son: {options}"

    what_to_withdraw = serializers.ChoiceField(
        choices=WHAT_TO_WITHDRAW_OPTIONS)
    scanned_envio_id = serializers.CharField(
        allow_blank=True, trim_whitespace=True)
    selected_filter_ids = serializers.CharField(
        allow_blank=True, trim_whitespace=True)
    filter_by = serializers.ChoiceField(
        allow_blank=True, choices=FILTER_BY_OPTIONS)

    class Meta:
        model = TrackingMovement
        fields = (
            'created_by',
            'carrier',
            'deposit',
            # 'comment',
            # 'proof',
            'what_to_withdraw',
            'scanned_envio_id',
            'selected_filter_ids',
            'filter_by',
        )

    def save(self):

        try:
            carrier = self.validated_data['carrier']
            deposit = self.validated_data['deposit']
            # comment = self.validated_data['comment']
            # proof = self.validated_data['proof']
            what_to_withdraw = self.validated_data['what_to_withdraw']
            scanned_envio_id = self.validated_data['scanned_envio_id']
            selected_filter_ids = self.validated_data['selected_ids'].split(
                "-")
            filter_by = self.validated_data['filter_by']
            author = self.validated_data['created_by']

            try:
                carrier = Account.objects.get(pk=carrier)
            except Account.DoesNotExist:
                raise serializers.ValidationError(
                    {"response": "El usuario portador no existe."})
            try:
                deposit = Deposit.objects.get(pk=deposit)
            except Deposit.DoesNotExist:
                raise serializers.ValidationError(
                    {"response": "El depósito no existe."})

            if what_to_withdraw not in self.WHAT_TO_WITHDRAW_OPTIONS:
                raise serializers.ValidationError(
                    {"response": self.what_to_withdraw_error})
            elif what_to_withdraw == 'all':
                withdraw(author=author, carrier=carrier, deposit=deposit)
            elif what_to_withdraw == 'one':
                withdraw(
                    author=author,
                    carrier=carrier,
                    deposit=deposit,
                    envios_ids=[scanned_envio_id]
                )

            # if len(comment) < MIN_COMMENT_LENGTH:
            #     raise serializers.ValidationError(
            #         {"response": "El comentario debe tener al menos " +
            #                      f"{MIN_COMMENT_LENGTH} caracteres."})

            # if len(comment) > MAX_COMMENT_LENGTH:
            #     raise serializers.ValidationError(
            #         {"response": "El comentario no puede tener más de " +
            #                      f"{MAX_COMMENT_LENGTH} caracteres."})

            # if scanned_envio_id:
            #     if not Envio.objects.filter(pk=scanned_envio_id).exists():
            #         raise serializers.ValidationError(
            #             {"response": "El envío con id {id} no existe.".format(
            #                 id=scanned_envio_id)}
            #         )

            if filter_by:
                if filter_by not in self.FILTER_BY_OPTIONS:
                    raise serializers.ValidationError(
                        {"response": self.filter_by_error.format(
                            used_filter=filter_by,
                            options=self.FILTER_BY_OPTIONS
                        )})

                for id in selected_filter_ids:
                    try:
                        int(id)
                        filters = (
                            ('zone', Zone, "La zona con id {id} no existe."),
                            ('partido', Partido,
                             "El partido con id {id} no existe."),
                            ('town', Town,
                             "La localidad con id {id} no existe."),
                        )
                        for filter, model, error_msg in filters:
                            if filter_by == filter:
                                if not model.objects.filter(pk=id).exists():
                                    raise serializers.ValidationError(
                                        {"response": error_msg.format(id=id)})
                    except ValueError:
                        raise serializers.ValidationError(
                            {"response": "Los ids de los filtros deben ser " +
                             "números enteros."})

        except KeyError:
            raise serializers.ValidationError(
                {"response": "Faltan datos."}
            )
