
def static_get_comment_parent_types():
    return ['Message', 'Question::Answer', 'Schedule::Entry', 'Todolist', 'Todo']


def static_get_recording_parent_types():
    return ['Todo', 'Todolist']


def static_get_vault_parent_types():
    return ['Vault']


def static_get_recording_types():
    return ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist', 'Upload',
            'Vault']


def static_get_webhook_types():
    return ['Comment', 'Document', 'Message', 'Question::Answer', 'Schedule::Entry', 'Todo', 'Todolist', 'Upload',
            'Vault', 'Client::Approval::Response', 'Client::Forward', 'Client::Reply', 'CloudFile', 'GoogleDocument',
            'Inbox::Forward', 'Question']
