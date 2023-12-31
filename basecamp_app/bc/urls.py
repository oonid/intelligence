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
    # project-recording
    path('project/<int:bucket_id>/recording/type/<recording_type>', views.app_project_recording_by_type,
         name='app-project-recording-by-type'),
    path('project/<int:bucket_id>/recording/parent/<int:parent_id>/comment', views.app_project_recording_parent_comment,
         name='app-project-recording-parent-comment'),
    # recording
    path('recording/', views.app_recording_main, name='app-recording-main'),
    path('recording/type/<recording_type>', views.app_recording_by_type, name='app-recording-by-type'),
    # comment
    path('project/<int:bucket_id>/comment/<int:comment_id>', views.app_comment_detail, name='app-comment-detail'),
    # message_type
    path('project/<int:bucket_id>/message/type', views.app_message_type, name='app-message-type'),
    path('project/<int:bucket_id>/message_board/<int:message_board_id>', views.app_message_board_detail,
         name='app-message-board-detail'),
    path('project/<int:bucket_id>/message_board/<int:message_board_id>/message', views.app_message_board_message,
         name='app-message-board-message'),
    path('project/<int:bucket_id>/message/<int:message_id>', views.app_message_detail, name='app-message-detail'),
    # questionnaire
    path('project/<int:bucket_id>/questionnaire/<int:questionnaire_id>', views.app_questionnaire_detail,
         name='app-questionnaire-detail'),
    path('project/<int:bucket_id>/questionnaire/<int:questionnaire_id>/question', views.app_questionnaire_question,
         name='app-questionnaire-question'),
    path('project/<int:bucket_id>/question/<int:question_id>', views.app_question_detail, name='app-question-detail'),
    path('project/<int:bucket_id>/question/<int:question_id>/answer', views.app_question_answer,
         name='app-question-answer'),
    path('project/<int:bucket_id>/question_answer/<int:question_answer_id>', views.app_question_answer_detail,
         name='app-question-answer-detail'),
    # schedule
    path('project/<int:bucket_id>/schedule/<int:schedule_id>', views.app_schedule_detail, name='app-schedule-detail'),
    path('project/<int:bucket_id>/schedule/<int:schedule_id>/entry', views.app_schedule_entry,
         name='app-schedule-entry'),
    path('project/<int:bucket_id>/schedule_entry/<int:schedule_entry_id>', views.app_schedule_entry_detail,
         name='app-schedule-entry-detail'),
    # todoset
    path('project/<int:bucket_id>/todoset/<int:todoset_id>', views.app_todoset_detail, name='app-todoset-detail'),
    # todolist
    path('project/<int:bucket_id>/todoset/<int:todoset_id>/todolist', views.app_todolist_main,
         name='app-todolist-main'),
    path('project/<int:bucket_id>/todolist/<int:todolist_id>', views.app_todolist_detail, name='app-todolist-detail'),
    # todolist_group
    path('project/<int:bucket_id>/todolist/<int:todolist_id>/group', views.app_todolist_group_main,
         name='app-todolist_group-main'),
    # todo
    path('project/<int:bucket_id>/todolist/<int:todolist_id>/todo', views.app_todo_main, name='app-todo-main'),
    path('project/<int:bucket_id>/todo/<int:todo_id>', views.app_todo_detail, name='app-todo-detail'),
    # vault, document, upload (different from CloudFile and GoogleDocument)
    path('project/<int:bucket_id>/vault/<int:vault_id>', views.app_vault_detail, name='app-vault-detail'),
    path('project/<int:bucket_id>/vault/<int:vault_id>/vaults', views.app_vault_vaults, name='app-vault-vaults'),
    path('project/<int:bucket_id>/vault/<int:vault_id>/documents', views.app_vault_documents,
         name='app-vault-documents'),
    path('project/<int:bucket_id>/vault/<int:vault_id>/uploads', views.app_vault_uploads, name='app-vault-uploads'),
    path('project/<int:bucket_id>/document/<int:document_id>', views.app_document_detail, name='app-document-detail'),
    path('project/<int:bucket_id>/upload/<int:upload_id>', views.app_upload_detail, name='app-upload-detail'),
]
