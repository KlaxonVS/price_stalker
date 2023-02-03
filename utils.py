async def get_id(link: str):
    index = link.split('/').index('catalog')
    return int(link.split('/')[index + 1])
