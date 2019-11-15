def stats(request):
    session = request.session
    stats = session.get('stats', {})
    times = stats.get('times', {}).copy()
    visits = stats.get('visits', {}).copy()
    if 'total' in times:
        times_total = times.pop('total')
    else:
        times_total = 0
    if 'total' in visits:
        visits_total = visits.pop('total')
    else:
        visits_total = 0
    return {
        'times': times,
        'visits': visits,
        'times_total': times_total,
        'visits_total': visits_total
    }