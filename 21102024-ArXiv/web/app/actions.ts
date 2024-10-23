"use server";

import { createServerClient } from "@supabase/ssr";
import { z } from "zod";
import { PinnacleClient } from "rcs-js";
import { NextResponse } from "next/server";

const Subscriber = z.object({
  name: z.string().min(1, "Name is required"),
  number: z
    .string()
    .regex(/^\+1\d{10}$/, "Phone number must be in the format +12345678901"),
});

// Initialize Supabase client
if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
  console.error(
    "SUPABASE_URL and SUPABASE_KEY environment variables must be set"
  );
  console.log("SUPABASE_URL:", process.env.SUPABASE_URL);
  console.log("SUPABASE_KEY:", process.env.SUPABASE_KEY);
}

const supabase = createServerClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!,
  {
    cookies: {
      get: () => undefined,
      set: () => {},
      remove: () => {},
    },
  }
);

export type SubscriberState = {
  message: string | null;
  isRegistered: boolean;
  error: string[] | null;
};

export const createSubscriber = async (
  prevState: SubscriberState,
  formData: FormData
): Promise<SubscriberState> => {
  console.log("User registered");
  const number = formData.get("number") as string;
  const name = formData.get("name") as string;

  console.log("Name:", name);
  console.log("Number:", number);

  try {
    // Register the user (replace with your actual registration logic)
    await registerUser(name, number);

    console.log("User registered successfully");
    return {
      ...prevState,
      isRegistered: true,
      error: null,
      message: `${number}`,
    };
  } catch (error: unknown) {
    console.error("Registration failed:", error);
    return {
      ...prevState,
      message: null,
      isRegistered: false,
      error:
        error instanceof Error
          ? [error.message]
          : ["An unknown error occurred"],
    };
  }
};

// Assume this function exists elsewhere in your code
async function registerUser(name: string, number: string): Promise<void> {
  try {
    const validatedData = Subscriber.parse({ name, number });

    console.log("Passed validation");

    // Check if the user is already registered
    const { data, error } = await supabase
      .from("ArxivSubscribers")
      .select("*")
      .eq("phone_number", validatedData.number)
      .single();

    if (error && error.code !== "PGRST116") {
      throw new Error("Database error: " + error.message);
    }

    if (data) {
      throw new Error(
        `User with phone number ${validatedData.number} is already registered`
      );
    }

    // Insert new subscriber
    const { error: insertError } = await supabase
      .from("ArxivSubscribers")
      .insert({
        name: validatedData.name,
        phone_number: validatedData.number,
        is_subscribed: false,
      });

    if (insertError) {
      throw new Error("Failed to register user: " + insertError.message);
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(
        "Validation error: " + error.errors.map((e) => e.message).join(", ")
      );
    }
    throw error;
  }
}

if (!process.env.PINNACLE_API_KEY) {
  throw new Error(
    "PINNACLE_API_KEY is not defined in the environment variables"
  );
}

const client = new PinnacleClient({ apiKey: process.env.PINNACLE_API_KEY });

const ROSIE_THE_RACCOON = "https://i.ibb.co/YcBFH32/IMG-3410.jpg";
const SAD_ROSIE_THE_RACCOON = "https://i.ibb.co/nQxWmS1/raccoon.jpg";

export async function sendText(number: string): Promise<boolean> {
  if (!number) {
    console.error("Phone number is required to send a text message");
    return false;
  }

  try {
    const result = await client.send.rcs({
      from: "test",
      to: number,
      cards: [
        {
          title: `Hey it's Rosie from Pinnacle here! Would you like to opt into receiving daily updates on new AI papers from ArXiv?`,
          subtitle: "It'll be great--I promise ❤️",
          mediaUrl: ROSIE_THE_RACCOON,
        },
      ],
      quickReplies: [
        {
          title: "Yes, sign me up!",
          type: "trigger",
          payload: "OPT_IN",
        },
        {
          title: "No, thanks",
          type: "trigger",
          payload: "OPT_OUT",
        },
      ],
    });
    console.log("RCS message send result:", result);
    return true;
  } catch (error) {
    console.error("Failed to send RCS message:", error);
    return false;
  }
}

// Add this new type for the webhook payload
type WebhookPayload = {
  messageType: string;
  buttonPayload: {
    title: string;
    payload: string;
    execute: string;
    sent: string;
    fromNum: string;
  };
};

export async function setUserSubscribed(phoneNumber: string): Promise<void> {
  try {
    const { error } = await supabase
      .from("ArxivSubscribers")
      .update({ is_subscribed: true })
      .eq("phone_number", phoneNumber);

    if (error) {
      throw new Error("Failed to update subscription status: " + error.message);
    }

    console.log(`User ${phoneNumber} successfully subscribed`);
  } catch (error) {
    console.error("Error updating subscription status:", error);
    throw error;
  }
}

export async function setUserUnsubscribed(phoneNumber: string): Promise<void> {
  try {
    const { error } = await supabase
      .from("ArxivSubscribers")
      .update({ is_subscribed: false })
      .eq("phone_number", phoneNumber);

    if (error) {
      throw new Error(
        "Failed to update unsubscription status: " + error.message
      );
    }

    console.log(`User ${phoneNumber} successfully unsubscribed`);
  } catch (error) {
    console.error("Error updating unsubscription status:", error);
    throw error;
  }
}

export async function sendUnsubscribeConfirmation(
  number: string
): Promise<boolean> {
  if (!number) {
    console.error("Phone number is required to send a text message");
    return false;
  }

  try {
    const result = await client.send.rcs({
      from: "test",
      to: number,
      cards: [
        {
          title: "You've been unsubscribed from ArXiv AI paper updates",
          subtitle:
            "We're sorry to see you go! You can always resubscribe later.",
          mediaUrl: SAD_ROSIE_THE_RACCOON,
        },
      ],
      quickReplies: [
        {
          title: "Resubscribe",
          type: "trigger",
          payload: "OPT_IN",
        },
      ],
    });
    console.log("RCS unsubscribe confirmation sent:", result);
    return true;
  } catch (error) {
    console.error("Failed to send RCS unsubscribe confirmation:", error);
    return false;
  }
}

export async function sendVerificationMessage(
  number: string
): Promise<boolean> {
  if (!number) {
    console.error("Phone number is required to send a verification message");
    return false;
  }

  try {
    const result = await client.send.rcs({
      from: "test",
      to: number,
      cards: [
        {
          title: "You're all set!",
          subtitle: "You'll recieve daily updates",
        },
      ],
      quickReplies: [
        {
          title: "Opt out",
          type: "trigger",
          payload: "OPT_OUT",
        },
      ],
    });
    console.log("RCS verification message sent:", result);
    return true;
  } catch (error) {
    console.error("Failed to send RCS verification message:", error);
    return false;
  }
}
