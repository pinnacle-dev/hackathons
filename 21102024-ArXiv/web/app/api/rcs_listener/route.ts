import { NextResponse } from "next/server";
import {
  sendText,
  sendUnsubscribeConfirmation,
  sendVerificationMessage,
  setUserSubscribed,
  setUserUnsubscribed,
} from "../../actions";

export async function POST(request: Request) {
  try {
    const inboundMsg = await request.json();

    if (inboundMsg.messageType === "action") {
      console.log("Received postback:", inboundMsg);

      if (inboundMsg.payload === "arxiv") {
        await sendText(inboundMsg.from);
      } else if (inboundMsg.payload === "OPT_IN") {
        console.log("opted in");
        await setUserSubscribed(inboundMsg.from);
        await sendVerificationMessage(inboundMsg.from);
      } else if (inboundMsg.payload === "OPT_OUT") {
        console.log("opted out");
        await setUserUnsubscribed(inboundMsg.from);
        await sendUnsubscribeConfirmation(inboundMsg.from);
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
