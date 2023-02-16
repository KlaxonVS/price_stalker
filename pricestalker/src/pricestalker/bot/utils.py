async def get_id(link: str):
    if link is None:
        return None
    if link.isdigit():
        return int(link)
    index = link.split('/').index('catalog')
    pk = link.split('/')[index + 1]
    return int(pk) if pk.isdigit() else None
