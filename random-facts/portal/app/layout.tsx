import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Fun Facts Text Updates",
  description: "Get fun facts every day!",
  openGraph: {
    images: [
      {
        url: "https://i.ibb.co/wyhW9pn/Pitch-Deck-Pinnacle-9.png", // raccoon image
        width: 1200,
        height: 630,
        alt: "Fun Facts Text Updates Preview",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: ["https://i.ibb.co/wyhW9pn/Pitch-Deck-Pinnacle-9.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
