def entity_data_cleanse(entity: str, type: str, term: str, ):
    """
    Ignores twitter handles, quantity, date, original search term, links
    """
    return "@" not in entity and \
           type != "QUANTITY" and \
           type != "DATE" and \
           entity != term.lower() and \
           "http:" not in entity and \
           "https:" not in entity
