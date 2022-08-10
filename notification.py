import asyncio
import json
import time
from pprint import pprint

from winsdk.windows.foundation.metadata import ApiInformation
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings
from winsdk.windows.ui.notifications.management import (
    UserNotificationListener,
    UserNotificationListenerAccessStatus,
)

if not ApiInformation.is_type_present(
    "Windows.UI.Notifications.Management.UserNotificationListener"
):
    print("UserNotificationListener is not supported on this device.")
    exit()


async def get_notifications_async() -> dict:
    with open("settings.json", "r") as f:
        settings = json.load(f)
    app = []
    if "*" in settings["validApps"]:
        # not recommended, maybe add disable option in settings.json later
        valid = True
    else:
        app.extend(settings["apps"][appName][1] for appName in settings["validApps"])
        valid = False
    # setup settings

    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
        print("Access to UserNotificationListener is not allowed.")
        return {}

    notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
    noti_dict = {}
    for notification in notifications:
        binding = notification.notification.visual.get_binding(
            KnownNotificationBindings.get_toast_generic()
        )

        if (
            valid or notification.app_info.display_info.display_name in app
        ) and binding is not None:
            if len(binding.get_text_elements()) <= 2:
                album = ""
            else:
                album = binding.get_text_elements()[2].text

            # append noti_dict and keep original dict
            noti_dict[str(notification.creation_time)] = {
                "song_name": binding.get_text_elements()[0].text,
                "artist_name": binding.get_text_elements()[1].text,
                "album_name": album,
            }
    return noti_dict


async def standalone(sleep: int = 5):
    while True:
        b = await get_notifications_async()
        pprint(b)
        with open("notification.json", "r") as f:
            c = json.load(f)
        if c != b:
            with open("notification.json", "w") as f:
                json.dump(b, f, indent=2, ensure_ascii=False)
            print("notification.json Updated")
        else:
            print("Skip Update")
        time.sleep(sleep)


def get_notifications(
    title: str | None = None, artist: str | None = None, album_title: str | None = None
):
    if title == "":
        title = None
    if artist == "":
        artist = None
    if album_title == "":
        album_title = None

    noti = asyncio.run(get_notifications_async())
    if noti == {}:
        return {
            "album_title": "",
            "artist": "",
            "title": "",
        }
    if not title and not artist and not album_title:
        # get latest notification from notification.json
        print("Missing title, artist, album_title")
        title = noti[sorted(list(noti.keys()))[-1]]["song_name"]
        artist = noti[sorted(list(noti.keys()))[-1]]["artist_name"]
        album_title = noti[sorted(list(noti.keys()))[-1]]["album_name"]
        return {
            "album_title": album_title,
            "artist": artist,
            "title": title,
        }

    elif not title and artist or album_title:
        # get the latest notification fit artist or album_title from notification.json
        # !!experimental method!!
        print("Missing title")
        for i in sorted(list(noti.keys())):
            if noti[i]["artist_name"] == artist or noti[i]["album_name"] == album_title:
                title = noti[i]["song_name"]
                artist = noti[i]["artist_name"]
                album_title = noti[i]["album_name"]
                return {
                    "album_title": album_title,
                    "artist": artist,
                    "title": title,
                }
        return {
            "album_title": "",
            "artist": "",
            "title": "",
        }

    else:  # only title
        # find notification data with same title
        print("Missing artist, album_title")
        for key in noti:
            if noti[key]["title"] == title:
                artist = noti[key]["artist_name"]
                album_title = noti[key]["album_name"]
                return {
                    "album_title": album_title,
                    "artist": artist,
                    "title": title,
                }
        return {
            "album_title": "",
            "artist": "",
            "title": "",
        }


if __name__ == "__main__":
    asyncio.run(standalone())
