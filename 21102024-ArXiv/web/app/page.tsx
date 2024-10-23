"use client";
import { useFormStatus } from "react-dom";
import { useFormState } from "react-dom";
import { createSubscriber, SubscriberState, sendText } from "./actions";
import { useState, useEffect } from "react";
import { PhoneInput } from "@/components/phone-input";
import { AnimatedBackground } from "animated-backgrounds";

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
      className="py-2 px-4 bg-[#83ff85] text-black rounded-none focus:outline-none focus:ring-2 focus:ring-[#303030] font-mono hover:bg-[#5ff562] transition-colors duration-100"
      disabled={pending}
    >
      {pending ? "Submitting..." : "Opt In"}
    </button>
  );
}

export default function Home() {
  const [state, formAction] = useFormState(createSubscriber, initialState);
  const [existingNumber, setExistingNumber] = useState<string | null>(null);
  const [registeredNumber, setRegisteredNumber] = useState<string | null>(null);
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
      console.log;
      const match = state.message?.match(/\+\d+/);
      if (match) {
        console.log("Registered number found:", match[0]);
        setRegisteredNumber(match[0]);
      } else {
        console.log("No phone number found in the message");
      }
    } else {
      setRegisteredNumber(null);
    }
  }, [state]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    formData.set("number", `+1${phoneNumber.replace(/\D/g, "")}`);
    formAction(formData);
  };

  return (
    <div className="">
      <AnimatedBackground
        animationName="matrixRain"
        style={{ opacity: 0.2 }} // Add any additional CSS styles
      />
      <div className="flex flex-col items-center justify-center min-h-screen gap-y-8 p-2 text-center">
        <div className="flex flex-col gap-y-4 items-center justify-center">
          <p className="font-mono font-bold text-3xl text-center">
            <span className="text-[#83ff85]">ArXiv</span> Updates
          </p>
          <p className="text-gray-500 max-w-xs text-center">
            Stay up to late with the latest AI papers via our RCS newsletter
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
                    className="underline text-[#83ff85]"
                  >
                    resend here
                  </button>{" "}
                  or{" "}
                  <button
                    onClick={() => {
                      setExistingNumber(null);
                    }}
                    className="underline text-[#83ff85]"
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
