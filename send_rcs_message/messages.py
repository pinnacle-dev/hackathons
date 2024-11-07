from rcs import Action, RcsFunctionalities, Card
from rcs_types import RCSMessage

check_rcs_functionality_action = Action(
    title="Check RCS Features",
    type="trigger",
    payload="check_rcs_functionality",
)

send_rcs_message_action = Action(
    title="Send RCS Message",
    type="trigger",
    payload="send_rcs_message",
)

read_more_action = Action(
    title="Read More",
    type="trigger",
    payload="read_more",
)

rcs_error_msg: RCSMessage = {
    "text": "Sorry, I didn't understand that. Please try again.",
    "quick_replies": [
        check_rcs_functionality_action,
        send_rcs_message_action,
        read_more_action,
    ],
}


intro_msg: RCSMessage = {
    "text": "Check out RCS Business Messaging in action! Click the buttons below to get started!",
    "quick_replies": [
        check_rcs_functionality_action,
        send_rcs_message_action,
        read_more_action,
    ],
}


media_msg: RCSMessage = {
    "media_url": "https://i.ibb.co/YcBFH32/IMG-3410.jpg",
    "quick_replies": [
        check_rcs_functionality_action,
        send_rcs_message_action,
        read_more_action,
    ],
}

pinnacle_carousel_msg: RCSMessage = {
    "cards": [
        Card(
            title="Learn more about Pinnacle",
            subtitle="Sign up for early access to Pinnacle, the future of RCS Business Messaging!",
            media_url="https://i.ibb.co/7C6P5N3/Screenshot-2024-10-21-at-4-47-30-PM.png",
            buttons=[
                Action(
                    type="openUrl",
                    title="Get Access",
                    payload="https://www.trypinnacle.app/access",
                )
            ],
        ),
        Card(
            title="Read the Pinnacle Docs",
            subtitle="Check out the Pinnacle documentation to learn more about our APIs and features!",
            media_url="https://i.ibb.co/YcBFH32/IMG-3410.jpg",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read Docs 📚",
                    payload="https://docs.trypinnacle.app/welcome/introduction",
                )
            ],
        ),
        Card(
            title="On The Potential of AI Personalization in SMS/RCS Messaging for Marketing",
            subtitle="Sean Roades - August 26, 2024\nIn today's fast-paced digital landscape, capturing and retaining customer attention is more challenging than ever. Enter AI-driven personalization and hyper-personalized workflows for SMS and RCS (Rich Communication Services) messaging - a game-changing approach that's set to revolutionize how businesses connect with their customers.",
            media_url="https://media.licdn.com/dms/image/v2/D5612AQEnmrq3TJyGfw/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1724710627702?e=1730332800&v=beta&t=WNMVGgc57ZNvPrW0noBPDhHCbn24YAdRJ0RANKkMu5c",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/potential-ai-personalization-smsrcs-messaging-sean-roades-iz3pc/?trackingId=g82pVkhSvCIcH%2Ff18A27Yw%3D%3D",
                )
            ],
        ),
        Card(
            title="Humans (who aren't using this) are cooked: AI-personalized RCS + SMS marketing",
            subtitle="Sean Roades - August 25, 2024\nAs the lines between artificial intelligence and human interaction blur, Rich Communication Services (RCS) and SMS are undergoing a dramatic transformation. Buckle up as we dive into how this game-changing technology is not just cutting through the noise—it's rewriting the rules of customer engagement.",
            media_url="https://media.licdn.com/dms/image/v2/D5612AQFWCMn50VZu2w/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1724618361124?e=1730332800&v=beta&t=BrZT-5ZlCfne2YBYIKPA2fPIhVZA-xN87A0XSnnhQyo",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/humans-who-arent-using-cooked-ai-personalized-rcs-sms-sean-roades-iqtkc/?trackingId=b1pAGo0lm6Zs7pvoXQoF0g%3D%3D",
                )
            ],
        ),
        Card(
            title="The Future of Mobile Marketing is RCS, not SMS",
            subtitle="Sean Roades - August 20, 2024\nAs we look to the future of mobile marketing, one technology stands out as a game-changer: Rich Communications Services (RCS). RCS is the next generation of SMS, offering a suite of advanced messaging features that provide a more engaging and interactive experience for consumers.",
            media_url="https://media.licdn.com/dms/image/v2/D5612AQE1oS6zlgkdjA/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1724176121089?e=1730332800&v=beta&t=4dS0vWW584XSZoAW32IZ2Ls1p-QmPx6WifV3lw8owLM",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/future-mobile-marketing-rcs-sms-sean-roades-53irc/?trackingId=tTC7HA%2FtspwnUqyxNkWiUQ%3D%3D",
                )
            ],
        ),
    ],
    "quick_replies": [
        check_rcs_functionality_action,
        send_rcs_message_action,
        read_more_action,
    ],
}


def create_rcs_capability_msg(rcs_check_result: RcsFunctionalities) -> RCSMessage:

    return {
        "text": (
            """RCS Capability Check:
Enabled: {is_enabled}
Standalone Rich Card: {standalone_rich_card}
Carousel Rich Card: {carousel_rich_card}
Create Calendar Event Action: {create_calendar_event_action}
Dial Action: {dial_action}
Open URL Action: {open_url_action}
Share Location Action: {share_location_action}
View Location Action: {view_location_action}
""".format(
                **dict(rcs_check_result)
            )
            if dict(rcs_check_result)["is_enabled"]
            else "RCS is not available for this phone number."
        ),
        "quick_replies": [
            check_rcs_functionality_action,
            send_rcs_message_action,
            read_more_action,
        ],
    }


read_more: RCSMessage = {
    "cards": [
        Card(
            title="On The Potential of AI Personalization in SMS/RCS Messaging for Marketing",
            subtitle="Sean Roades - August 26, 2024\nIn today's fast-paced digital landscape, capturing and retaining customer attention is more challenging than ever. Enter AI-driven personalization and hyper-personalized workflows for SMS and RCS (Rich Communication Services) messaging - a game-changing approach that's set to revolutionize how businesses connect with their customers.",
            media_url="https://i.ibb.co/fn31YLW/image.png",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/potential-ai-personalization-smsrcs-messaging-sean-roades-iz3pc/?trackingId=g82pVkhSvCIcH%2Ff18A27Yw%3D%3D",
                )
            ],
        ),
        Card(
            title="Humans (who aren't using this) are cooked: AI-personalized RCS + SMS marketing",
            subtitle="Sean Roades - August 25, 2024\nAs the lines between artificial intelligence and human interaction blur, Rich Communication Services (RCS) and SMS are undergoing a dramatic transformation. Buckle up as we dive into how this game-changing technology is not just cutting through the noise—it's rewriting the rules of customer engagement.",
            media_url="https://i.ibb.co/54GWmXv/image.png",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/humans-who-arent-using-cooked-ai-personalized-rcs-sms-sean-roades-iqtkc/?trackingId=b1pAGo0lm6Zs7pvoXQoF0g%3D%3D",
                )
            ],
        ),
        Card(
            title="RCS Messaging: The Overlooked Powerhouse in DTC Marketing for E-commerce",
            subtitle="Sean Roades - August 23, 2024\nIn the ever-evolving landscape of digital marketing, e-commerce brands are constantly seeking new channels to connect with customers. While email, social media, and traditional SMS have long been staples of direct-to-consumer (DTC) marketing strategies, there's a powerful channel that many marketers are overlooking: Rich Communication Services (RCS) messaging.",
            media_url="https://i.ibb.co/0r781Z6/image.png",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/rcs-messaging-overlooked-powerhouse-dtc-marketing-sean-roades-jvhec/?trackingId=8RY2SEIwupDGEJDVFaLJWw%3D%3D",
                )
            ],
        ),
        Card(
            title="The Future of Mobile Marketing is RCS, not SMS",
            subtitle="Sean Roades - August 20, 2024\nAs we look to the future of mobile marketing, one technology stands out as a game-changer: Rich Communications Services (RCS). RCS is the next generation of SMS, offering a suite of advanced messaging features that provide a more engaging and interactive experience for consumers.",
            media_url="https://i.ibb.co/rMqwSkL/1724176121089-e-1736380800-v-beta-t-o-T4-F9v9ko-TX0-U4-Igt-Ol-Ji57l97-Uu-Jk-Sk-VIFRjt2-JNVE.jpg",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.linkedin.com/pulse/future-mobile-marketing-rcs-sms-sean-roades-53irc/?trackingId=tTC7HA%2FtspwnUqyxNkWiUQ%3D%3D",
                )
            ],
        ),
        Card(
            title="RCS in iOS 18: What You Need to Know About Apple's Android Messaging Upgrade",
            subtitle="Juli Clover - August 2, 2024\nApple is adopting Rich Communication Services (RCS) in 2024, upgrading messaging standards for non-iMessage conversations. Apple's news came as a shock when it was announced in November 2023 because Google had been aggressively pushing Apple to implement RCS for multiple years, but Apple hadn't budged.",
            media_url="https://i.ibb.co/dm91Kfk/apple-rcs-thumb.jpg",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.macrumors.com/guide/rcs/D",
                )
            ],
        ),
        Card(
            title="A Guide to RCS, Why Apple’s Adopting It, and How It Makes Texting Better",
            subtitle="David Nield - June 15, 2024\nThe messaging standard promises better security and cooler features than plain old SMS. Android has had it for years, but now iPhones are getting it too.",
            media_url="https://i.ibb.co/YXYx8s1/01-ios.jpg",
            buttons=[
                Action(
                    type="openUrl",
                    title="Read More",
                    payload="https://www.wired.com/story/guide-to-rcs-why-it-makes-texting-better/",
                )
            ],
        ),
    ],
    "quick_replies": [
        check_rcs_functionality_action,
        send_rcs_message_action,
        read_more_action,
    ],
}


def create_send_rcs_message_intro(
    from_: str,
) -> RCSMessage:
    return {
        "text": "You received an RCS message from " + from_ + ". Check it out 🚀🦝",
    }


def create_send_rcs_message_confirmation() -> RCSMessage:
    return {
        "text": "Successfully sent an RCS message! Check out our other features below.",
        "quick_replies": [
            check_rcs_functionality_action,
            send_rcs_message_action,
            read_more_action,
        ],
    }


def create_send_rcs_message_with_payload(
    to: str,
) -> RCSMessage:
    return {
        "text": "What type of message would you like to send to " + to + "?",
        "quick_replies": [
            Action(
                title="Text",
                type="trigger",
                payload=f'{{"type": "send_text_message", "to": "{to}"}}',
            ),
            Action(
                title="Image",
                type="trigger",
                payload=f'{{"type": "send_media_message", "to": "{to}"}}',
            ),
            Action(
                title="Carousel",
                type="trigger",
                payload=f'{{"type": "send_carousel", "to": "{to}"}}',
            ),
        ],
    }


def create_send_rcs_message_not_enabled(
    to: str,
) -> RCSMessage:
    return {
        "text": "RCS is not enabled on the target device. Do you want to send an invite via SMS to"
        + to
        + "?",
        "quick_replies": [
            Action(
                title="Yes",
                type="trigger",
                payload=f'{{"type": "send_sms_invite", "to": "{to}"}}',
            ),
            Action(
                title="No",
                type="trigger",
                payload=f'{{"type": "cancel_send_rcs_message", "to": "{to}"}}',
            ),
        ],
    }
