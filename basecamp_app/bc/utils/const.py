
def static_get_comment_parent_types():
    return ['Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todolist', 'Todo', 'Upload']


def static_get_message_parent_types():
    return ['Message::Board']


def static_get_vault_parent_types():
    return ['Vault']


def static_get_recording_types():
    return ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist', 'Upload',
            'Vault']


def static_get_webhook_types():
    return ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist', 'Upload',
            'Vault', 'Client::Approval::Response', 'Client::Forward', 'Client::Reply', 'CloudFile', 'GoogleDocument',
            'Inbox::Forward', 'Question']
