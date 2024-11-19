"use client";
import { useFormStatus } from "react-dom";
import { createSubscriber, SubscriberState, sendText } from "./actions";
import { useState, useEffect, useActionState, startTransition } from "react";
import { PhoneInput } from "@/components/phone-input";
import AnimatedMessages from "@/app/AnimatedMessages";

// Define the initial state and action
const initialState: SubscriberState = {
  message: null,
  error: null,
  isRegistered: false,
};

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      className="py-2 px-4 bg-[#1F8AFF] text-black rounded-none focus:outline-none focus:ring-2 focus:ring-[#303030] font-mono hover:bg-[#2546ff] transition-colors duration-100"
      disabled={pending}
    >
      {pending ? "Submitting..." : "Opt In"}
    </button>
  );
}

export default function Home() {
  const [state, dispatch] = useActionState(createSubscriber, initialState);
  const [existingNumber, setExistingNumber] = useState<string | null>(null);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<string | null>(null);

  const handleSendText = async (number: string) => {
    setSending(true);
    setSendResult(null);
    const result = await sendText(number);
    setSending(false);
    if (result === true) {
      setSendResult("Text sent successfully!");
    } else {
      setSendResult("Failed to send text. Please try again.");
    }
  };

  useEffect(() => {
    console.log("State changed:", state);

    if (
      Array.isArray(state.error) &&
      state.error[0].startsWith("User with phone number")
    ) {
      const match = state.error[0].match(/\+\d+/);
      if (match) {
        setExistingNumber(match[0]);
      }
    } else {
      setExistingNumber(null);
    }

    if (state.isRegistered) {
      console.log("User registered successfully");
      const match = state.message?.match(/\+\d+/);
      console.log("Match:", match);
      if (match) {
        console.log("Registered number found:", match[0]);
      } else {
        console.log("No phone number found in the message");
      }
    }
  }, [state]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    formData.set("number", `+1${phoneNumber.replace(/\D/g, "")}`);
    startTransition(() => {
      dispatch(formData);
    });
  };

  return (
    <div className="w-full min-h-screen relative flex flex-col items-center justify-center">
      <AnimatedMessages />
      <div className="flex flex-col items-center justify-center gap-y-8 p-2 text-center z-50">
        <div className="flex flex-col gap-y-4 items-center justify-center">
          <p className="font-mono font-bold text-3xl text-center">
            <span className="text-[#1F8AFF]">Fun Facts</span>
          </p>
          <p className="text-gray-500 max-w-xs text-center">
            Get fun facts every day!
          </p>
        </div>
        <div className="flex flex-col items-center gap-8">
          {!existingNumber && (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <input
                name="name"
                placeholder="Your name"
                className="py-2 px-4 bg-[#161616] text-white rounded-none focus:outline-none focus:ring-2 focus:ring-[#303030] border-2 border-[#242424]"
                required
              />
              <PhoneInput
                value={phoneNumber}
                placeholder="(555) 123-4567"
                onChange={setPhoneNumber}
              />
              <SubmitButton />
            </form>
          )}
          <div className="flex flex-col justify-center items-center gap-y-4">
            {state.error && (
              <p className="text-red-500 font-bold">{state.error}</p>
            )}
            {state.message && <p className="text-green-500">{state.message}</p>}
            {existingNumber && (
              <div className="flex flex-col items-center gap-4 max-w-xl text-center">
                <p>
                  If this is your number, and you no longer have access to the
                  opt in / opt out menu, you can{" "}
                  <button
                    onClick={() => handleSendText(existingNumber ?? "")}
                    className="underline text-[#1F8AFF]"
                  >
                    resend here
                  </button>{" "}
                  or{" "}
                  <button
                    onClick={() => {
                      setExistingNumber(null);
                    }}
                    className="underline text-[#1F8AFF]"
                  >
                    register another number here
                  </button>
                </p>
                {sending && <p>Sending text...</p>}
                {sendResult && (
                  <p
                    className={
                      sendResult.includes("successfully")
                        ? "text-green-500"
                        : "text-red-500"
                    }
                  >
                    {sendResult}
                  </p>
                )}
              </div>
            )}
            {/* {registeredNumber && (
              <div className="flex flex-col items-center gap-4">
                <p>
                  Registration almost complete! Would you like to send a
                  verification text to complete your registration?
                </p>
                <SendTextButton number={registeredNumber} />
              </div>
            )} */}
          </div>
        </div>
      </div>
    </div>
  );
}
