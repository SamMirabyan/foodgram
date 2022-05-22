def create_tags(admin_client):
    result = []
    data = {'name': 'Ланч', 'slug': 'lunch', 'color': '#443FFA'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Быстрый перекус', 'slug': 'fast', 'color': '#00FF55'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Сладкое', 'slug': 'sweet', 'color': '#C35'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)
    return result
