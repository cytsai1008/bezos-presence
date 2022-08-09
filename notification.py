import asyncio
import json
import time
from pprint import pprint

from winsdk.windows.foundation.metadata import ApiInformation
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus

if not ApiInformation.is_type_present("Windows.UI.Notifications.Management.UserNotificationListener"):
    print("UserNotificationListener is not supported on this device.")
    exit()


async def get_notifications() -> dict:
    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
        print("Access to UserNotificationListener is not allowed.")
        exit()

    notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
    noti_dict = {}
    for notification in notifications:
        binding = notification.notification.visual.get_binding(KnownNotificationBindings.get_toast_generic())
        if notification.app_info.display_info.display_name == "Amazon Music" and binding is not None:
            if len(binding.get_text_elements()) <= 2:
                album = ""
            else:
                album = binding.get_text_elements()[2].text

            """
            {"song_name": binding.get_text_elements()[0].text,
            "artist_name": binding.get_text_elements()[1].text, "album_name": album,
            "create_time": str(notification.creation_time), }
            """
            # append noti_dict and keep original dict
            noti_dict[str(notification.creation_time)] = {
                "song_name": binding.get_text_elements()[0].text,
                "artist_name": binding.get_text_elements()[1].text,
                "album_name": album,
            }
    return noti_dict


async def main(sleep: int = 1):
    while True:
        b = await get_notifications()
        pprint(b)
        with open("notification.json", "w") as f:
            json.dump(b, f, indent=2, ensure_ascii=False)
        time.sleep(sleep)


if __name__ == "__main__":
    asyncio.run(main())
