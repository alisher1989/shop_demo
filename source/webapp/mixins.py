from datetime import datetime

from django.views.generic import View
#
# stats = {
#     'visits': {
#         'page1': 5,
#         'page2': 6,
#         'page3': 4,
#         'total': 15
#     },
#     'times': {
#         'page1': 100,
#         'page2': 200,
#         'page3': 300,
#         'total': 600
#     }
#     'last_page_visit': '...',
# }
# last_page - хранит url предыдущей страницы.
# last_time - хранит время посещения предыдущей страницы, чтобы считать разницу от текущего.

class StatisticsMixin(View):
    def get(self, request, *args, **kwargs):
        stats = request.session.get('stats', {})

        visits = stats.get('visits', {})

        current_page_visits = visits.get(request.path, 0)
        current_page_visits += 1
        visits[request.path] = current_page_visits

        total_visits = visits.get('total', 0)
        total_visits += 1
        visits['total'] = total_visits

        stats['visits'] = visits

        times = stats.get('times', {})
        now = datetime.now()
        last_time = request.session.get('last_time')
        last_page = request.session.get('last_page')
        if last_page:
            last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
            time_diff = (now - last_time).total_seconds()

            last_page_time = times.get(last_page, 0)
            last_page_time += time_diff
            times[last_page] = last_page_time

            total_time = times.get('total', 0)
            total_time += time_diff
            times['total'] = total_time

        stats['times'] = times

        request.session['stats'] = stats
        request.session['last_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
        request.session['last_page'] = request.path

        return super().get(request, *args, **kwargs)
