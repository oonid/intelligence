from django.urls import path

from . import views

urlpatterns = [
    path('', views.basecamp_main, name='bc-main'),
    path('auth', views.basecamp_auth, name='bc-auth'),
    path('redirect', views.basecamp_redirect, name='bc-redirect'),
    # people
    path('people/', views.app_people_main, name='app-people-main'),
    path('people/person/', views.app_people_person, name='app-people-person'),
    path('people/load/all/to/db', views.app_people_load_all_to_db, name='app-people-load-all-to-db'),
    # project
    path('project/', views.app_project_main, name='app-project-main'),
    path('project/<int:project_id>', views.app_project_detail, name='app-project-detail'),
    path('project/<int:project_id>/update-db', views.app_project_detail, kwargs={'update_db': True},
         name='app-project-detail-update-db'),
    # todoset
    path('project/<int:bucket_id>/todoset/<int:todoset_id>', views.app_todoset_detail, name='app-todoset-detail'),
    # project-recording
    path('project/<int:project_id>/recording/type/<recording_type>', views.app_project_recording_by_type,
         name='app-project-recording-by-type'),
    # recording
    path('recording/', views.app_recording_main, name='app-recording-main'),
    path('recording/type/<recording_type>', views.app_recording_by_type, name='app-recording-by-type'),
]
