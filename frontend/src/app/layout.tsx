import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { MobileNav } from "@/components/layout/mobile-nav";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/theme-provider";
import { PageTransition } from "@/components/layout/page-transition";
import { DatasetProvider } from "@/contexts/dataset-context";
import { DatasetBar } from "@/components/layout/dataset-bar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Riesgo Académico - Analytics",
  description: "Sistema Predictivo de Riesgo Académico Estudiantil",
  icons: { icon: "/branding/mascota-robot.jpeg" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full bg-background">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <DatasetProvider>
            <Sidebar />
            <MobileNav />
            <main className="md:pl-64">
              <div className="max-w-6xl mx-auto px-4 pt-20 pb-8 md:px-6 md:pt-8">
                <DatasetBar />
                <PageTransition>{children}</PageTransition>
              </div>
            </main>
          </DatasetProvider>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
