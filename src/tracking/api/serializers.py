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


class BaseWithdrawSerializer(serializers.ModelSerializer):
    def check_deposit(self, deposit):
        if deposit.envio_set.count() == 0:
            raise serializers.ValidationError(
                {"response": "El depósito no tiene envíos."}
            )


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


class WithdrawAllSerializer(BaseWithdrawSerializer):

    class Meta:
        model = TrackingMovement
        fields = (
            'created_by',
            'carrier',
            'deposit',
        )

    def save(self):

        try:
            author = self.validated_data['created_by']
            deposit = self.validated_data['deposit']
            carrier = self.validated_data['carrier']

            self.check_deposit(deposit)
            # if deposit.envio_set.count() == 0:
            #     raise serializers.ValidationError(
            #         {"response": "El depósito '{}' no tiene envíos.".format(
            #             deposit)})

            movement = TrackingMovement(
                created_by=author,
                carrier=carrier,
                deposit=deposit,
                action=TrackingMovement.ACTION_COLLECTION,
                result=TrackingMovement.RESULT_TRANSFERED,
            )
            movement.save()
            envios = Envio.objects.filter(
                status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
                deposit=deposit
            )
            # Add envios to the movement
            movement.envios.add(*envios)
            envios.update(
                status=Envio.STATUS_MOVING,
                carrier=carrier,
                deposit=None,
            )
            return movement
        except KeyError as e:
            raise serializers.ValidationError(
                {"response": "Faltan datos de {}".format(e)}
            )


class WithdrawByIdsSerializer(BaseWithdrawSerializer):

    envios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = (
            'created_by',
            'carrier',
            'deposit',
            'envios_ids',
        )

    def save(self):

        try:
            author = self.validated_data['created_by']
            deposit = self.validated_data['deposit']
            self.check_deposit(deposit)
            carrier = self.validated_data['carrier']
            envios_ids = self.validated_data['envios_ids']
            if len(envios_ids) == 0:
                raise serializers.ValidationError(
                    {"response": "Faltan datos de 'envios_ids'"})

            if deposit.envio_set.filter(
                    pk__in=envios_ids).count() != len(envios_ids):
                raise serializers.ValidationError(
                    {"response": "Alguno de los envíos con ids " +
                        "{} no existe o no está en el depósito {}.".format(
                            envios_ids, deposit)
                     }
                )
            movement = TrackingMovement(
                created_by=author,
                carrier=carrier,
                deposit=deposit,
                action=TrackingMovement.ACTION_COLLECTION,
                result=TrackingMovement.RESULT_TRANSFERED,
            )
            movement.save()
            envios = Envio.objects.filter(
                status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
                deposit=deposit,
                id__in=envios_ids
            )
            # Add envios to the movement
            movement.envios.add(*envios)
            envios.update(
                status=Envio.STATUS_MOVING,
                carrier=carrier,
                deposit=None,
            )
            return movement
        except KeyError as e:
            raise serializers.ValidationError(
                {"response": "Faltan datos de {}".format(e)}
            )


class WithdrawByFilterSerializer(serializers.Serializer):

    def check_deposit(self, deposit):
        if deposit.envio_set.count() == 0:
            raise serializers.ValidationError(
                {"response": "El depósito no tiene envíos."}
            )

    # class Meta:
    #     extra_kwargs = {'filter_by': {'required': False}}

    created_by = serializers.IntegerField(min_value=0, write_only=True)
    carrier = serializers.IntegerField(min_value=0, write_only=True)
    deposit = serializers.IntegerField(min_value=0, write_only=True)

    selected_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    FILTER_BY_OPTIONS = ['zone', 'partido', 'town']
    filter_by = serializers.CharField(max_length=20, write_only=True)

    def validate_created_by(self, created_by):
        if created_by is None:
            raise serializers.ValidationError(
                {"response": "Falta el usuario que realiza la acción."})
        if not Account.objects.filter(pk=created_by).exists():
            raise serializers.ValidationError(
                {"response": "El usuario con id {} no existe.".format(
                    created_by)})
        return created_by

    def validate(self, data):
        filter_by = data['filter_by']
        if filter_by in [None, '']:
            raise serializers.ValidationError(
                {"response": "Falta el tipo de filtro <filter_by>."})
        if filter_by not in self.FILTER_BY_OPTIONS:
            raise serializers.ValidationError(
                {"response": "Los filtros deben ser 'zone', 'partido' " +
                 "o 'town'."})

        return data
        # try:
        #     data = super().validate(data)
        #     filter_by = data['filter_by']
        #     selected_ids = data['selected_ids']
        #     if filter_by not in self.FILTER_BY_OPTIONS:
        #         raise serializers.ValidationError(
        #             {"response": self.filter_by_error.format(
        #                 used_filter=filter_by,
        #                 options=self.FILTER_BY_OPTIONS
        #             )})
        #     if len(selected_ids) == 0:
        #         raise serializers.ValidationError(
        #             {"response": "Faltan datos de 'selected_ids'"})
        #     return data
        # except KeyError as e:
        #     raise serializers.ValidationError(
        #         {"response": "Faltan datos de {}".format(e)}
        #     )

    def save(self):

        try:
            author = Account.objects.get(pk=self.validated_data['created_by'])
            deposit = Deposit.objects.get(pk=self.validated_data['deposit'])
            self.check_deposit(deposit)
            carrier = Account.objects.get(pk=self.validated_data['carrier'])
            selected_ids = self.validated_data['selected_ids']
            filter_by = self.validated_data['filter_by']
            if len(selected_ids) == 0:
                raise serializers.ValidationError(
                    {"response": "Faltan datos de 'selected_ids'"})

            filters = {}
            if filter_by == 'zone':
                if Zone.objects.filter(pk__in=selected_ids).count() != \
                        len(selected_ids):
                    raise serializers.ValidationError(
                        {"response": "Alguna de las zonas con ids " +
                            "{} no existe.".format(selected_ids)})
                filters = {"town__partido__zone__id__in": selected_ids}
            elif filter_by == 'partido':
                if Partido.objects.filter(pk__in=selected_ids).count() != \
                        len(selected_ids):
                    raise serializers.ValidationError(
                        {"response": "Alguno de los partidos con ids " +
                            "{} no existe.".format(selected_ids)})
                filters = {"town__partido__id__in": selected_ids}
            elif filter_by == 'town':
                if Town.objects.filter(pk__in=selected_ids).count() != \
                        len(selected_ids):
                    raise serializers.ValidationError(
                        {"response": "Alguna de las localidades con ids " +
                            "{} no existe.".format(selected_ids)})
                filters = {"town__id__in": selected_ids}
            else:
                raise serializers.ValidationError(
                    {"response": "Los filtros deben ser 'zone', 'partido' " +
                        "o 'town'"})

            movement = TrackingMovement(
                created_by=author,
                carrier=carrier,
                deposit=deposit,
                action=TrackingMovement.ACTION_COLLECTION,
                result=TrackingMovement.RESULT_TRANSFERED,
            )
            movement.save()
            envios = Envio.objects.filter(
                status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
                deposit=deposit,
                **filters
            )
            # Add envios to the movement
            movement.envios.add(*envios)
            envios.update(
                status=Envio.STATUS_MOVING,
                carrier=carrier,
                deposit=None,
            )
            return movement
        except KeyError as e:
            raise serializers.ValidationError(
                {"response": "Faltan datos de {}".format(e)}
            )
