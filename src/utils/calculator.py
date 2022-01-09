from decimal import Decimal
from clients.models import Discount
from envios.models import Envio, DETAIL_CODES


class Invoice:

    def __init__(self, *envios: Envio) -> None:
        self.envios = []
        for envio in envios:
            if isinstance(envio, Envio):
                self.envios.append(envio)
        if not envios:
            raise ValueError('No envios were provided')

    def get_total_cost(self) -> Decimal:
        total = Decimal(0)
        for envio in self.envios:
            total += envio.price
        return round(total)


# def calculate_envio_price(envio: Envio) -> Decimal:
#     """
#     Performs de calculation for the price of the 'envio'.
#     It applies the discount if it is available.
#     The operations are made with Decimal to avoid the rounding errors.

#     Returns:
#         Decimal: The price of the 'envio'.
#     """
#     # Get the town of recipient's address
#     town = envio.town

#     #  Get the code. If 'envio' is from flex, return flex's code for
#     # given town, else the normal code.
#     code = town.flex_code if envio.is_flex else town.delivery_code

#     # Get the price for the given code
#     price = Decimal(str(code.price))

#     # Get the detail for the given envio
#     detail_codes = envio.detail.split(',')

#     # Initialize total price to 0
#     total_price = Decimal(0)

#     # Get the price for each package detail
#     for detail_code in detail_codes:
#         # Unpack code and amount spliting by '-'
#         code, amount = detail_code.split('-')
#         # Get the package detail for the given code
#         detail_code = DETAIL_CODES[code]
#         # Get multiplier for the given package detail
#         multiplier = detail_code["multiplier"]
#         # Multiply the price by the multiplier for given package
#         # detail, times the amount of packages
#         result = Decimal(str(multiplier)) * price * Decimal(amount)
#         # Add the result to the total price
#         total_price += result

#     # Get single discount for envio's client and partido, if and
#     # only if the envio and discount match the is_for_flex and is_flex flags
#     discount = Discount.objects.filter(
#         client__id=envio.client.id,
#         is_for_flex=envio.is_flex,
#         partidos__in=[envio.town.partido]
#     ).first()

#     # If discount exists, apply it to the total price
#     if discount:
#         discount = Decimal(discount.amount) / Decimal(100)
#         total_discount = total_price * discount
#         result = total_price - total_discount
#         return result

#     print("discount NO")
#     print("total_price", total_price)
#     # return the total price
#     return total_price
