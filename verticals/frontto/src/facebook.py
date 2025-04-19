from collections import defaultdict

from utils import fix_phone


def try_to_process_verification(request, token_to_match) -> tuple[bool, str, int]:
    # Try to process the verification step
    # request: the request object
    # token: the valid token
    # return:
    #       process flag: True if process the verification step, False if not
    #       challenge text,
    #       response code

    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == token_to_match:
            return True, challenge, 200
        else:
            return True, "Verification failed", 403

    return False, "", 200


def all_phone_and_messages_gen(request):
    if request.method == "POST":
        data = request.get_json()

        if data:
            if "entry" in data:
                for entry in data["entry"]:
                    for change in entry.get("changes", []):
                        if "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                sender_id = message["from"]
                                phone = fix_phone(sender_id)
                                text = message.get("text", {}).get("body", "")
                                yield (phone, text)


def all_phone_and_messages(request):
    phone_and_messages = [x for x in all_phone_and_messages_gen(request)]
    phone_and_messages_dict = defaultdict(list)
    for phone, message in phone_and_messages:
        phone_and_messages_dict[phone].append(message)

    phone_and_messages_dict = {
        phone: "\n\n".join(list_of_messages)
        for phone, list_of_messages in phone_and_messages_dict.items()
    }

    return phone_and_messages_dict


if __name__ == "__main__":
    pass
