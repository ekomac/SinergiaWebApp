from decimal import Decimal
from clients.models import Discount
from envios.models import Envio, DETAIL_CODES


class PriceCalculator(object):

    def __init__(self, envio: Envio):
        self.envio = envio
        return

    def calculate(self) -> Decimal:
        """Performs de calculation for the price of the 'envio'

        Returns:
            Decimal: The total price
        """
        # Get the 'envio'
        envio = self.envio

        # Get the town of recipient's address
        town = envio.town

        #  Get the code. If 'envio' is from flex, return flex's code for
        # given town, else the normal code.
        code = town.flex_code if envio.is_flex else town.delivery_code

        # Set code's price to default price. Later used when
        # parsing the detail to a price
        self.default_price = code.price

        # Get the total price
        total_price = self.get_price()

        # If the 'envio' has got a discount
        discount = Discount.objects.filter(
            client__id=envio.client.id,
            is_for_flex=envio.is_flex,
            partidos__in=[envio.town.partido]
        ).first()
        if discount:
            return total_price - Decimal(total_price * Decimal(discount.amount / 100))

        # return the total price
        return total_price

    def detail_to_price(self, detail) -> Decimal:
        """Parse a package detail pair in "3-4" format,
        where 3 is the id-code for the type of package,
        and 4 is the amount of packages.

        Args:
            detail (str): package detail pair in "3-4" format.

        Returns:
            Decimal: the total price.
        """
        parts = detail.split('-')
        code = parts[0]
        amount = parts[1]
        detail_code = DETAIL_CODES[code]
        print(f'{detail_code=}')
        total_price = Decimal(
            self.default_price * detail_code["multiplier"] * int(amount))
        return total_price

    def get_price(self):
        if not self.envio.is_flex:
            detail_codes = self.envio.detail.split(',')
            prices = map(self.detail_to_price, detail_codes)
            return Decimal(sum(prices))
        return Decimal(self.default_price)
