import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ACS Master System",
  description: "Read-only ACS Master System operational dashboard foundation."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
