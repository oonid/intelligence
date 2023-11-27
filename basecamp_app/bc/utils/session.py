from datetime import datetime, timezone

# utilities to process sessions


def session_get_token_and_identity(request):
    """

    :param request:
    :return: tuple of dicts: token, identity
    """
    token = None
    identity = None

    if "token" not in request.session:  # no token in session, return None
        return token, identity  # None

    # token exists
    token = request.session["token"]
    # [:-1] to remove 'Z' at the last character in date time str
    token_expires_datetime = datetime.fromisoformat(token["expires_at"][:-1]).astimezone(timezone.utc)

    if token_expires_datetime < datetime.now().astimezone(timezone.utc):  # token expired, strip token, return None
        try:
            del request.session["token"]
        except KeyError:
            pass

        return token, identity  # None

    # token still updated
    if "identity" not in request.session:  # no identity, strip token and return None
        try:
            del request.session["token"]
        except KeyError:
            pass

        return token, identity  # None

    # identity exists
    identity = request.session["identity"]

    # return token and identity
    return token, identity
