import { NextResponse } from "next/server";
import {
  sendUnsubscribeConfirmation,
  sendVerificationMessage,
  setUserSubscribed,
  setUserUnsubscribed,
} from "../../actions";

export async function POST(request: Request) {
  console.log("Received post");

  try {
    const body = await request.json();
    console.log(body);

    if (body.messageType === "postback") {
      const { buttonPayload } = body;

      const { title, payload, execute, sent, fromNum } = buttonPayload;

      console.log("Received postback:", {
        title,
        payload,
        execute,
        sent,
        fromNum,
      });

      if (payload === "OPT_IN") {
        console.log("opted in");
        await setUserSubscribed(fromNum);
        await sendVerificationMessage(fromNum);
      }

      if (payload === "OPT_OUT") {
        console.log("opted out");
        await setUserUnsubscribed(fromNum);
        await sendUnsubscribeConfirmation(fromNum);
      }

      return NextResponse.json({
        success: true,
        message: "Postback received and processed",
      });
    }

    return NextResponse.json(
      { success: false, message: "Unsupported message type" },
      { status: 400 }
    );
  } catch (error) {
    console.error("Error processing request:", error);
    return NextResponse.json(
      { success: false, message: "Internal server error" },
      { status: 500 }
    );
  }
}
