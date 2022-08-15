def build_full_address(
    address: str,
    zip_code: str,
    town: str,
    title_cased: bool = True
) -> str:
    """
    Build a full address from an address, zip code and town.

    Args:
        address (str): Street and number of the address.
        zip_code (str): Zip code of the address.
        town (str): Town of the address.
        title_cased (bool): If True, the address will be in title case;
                            optional. Default: True.

    Returns:
        str: Full address.
    """
    result = '{title},{zip_code} {town}'.format(
        title=address,
        zip_code=f" {zip_code}" if zip_code else "",
        town=town
    )
    if title_cased:
        return result.title()
    return result
