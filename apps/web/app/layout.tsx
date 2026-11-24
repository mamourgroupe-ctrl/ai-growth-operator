import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Growth Operator",
  description: "مساعد تسويق ذكي للشركات الصغيرة في الجزائر",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
