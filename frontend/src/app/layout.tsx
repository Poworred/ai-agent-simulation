import "./globals.css";

export const metadata = {
  title: "AI 南大",
  description: "多智能体校园社会模拟系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
