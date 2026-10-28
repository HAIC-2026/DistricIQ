import type { Metadata } from "next";
import "./globals.css";
import "@arcgis/core/assets/esri/themes/light/main.css";
import { Providers } from "@/components/providers";
import { Shell } from "@/components/layout/Shell";
export const metadata: Metadata = {
  title: "DistrictIQ Hawaiʻi | Know your district",
  description:
    "Source-transparent geographic discovery and legislative district intelligence for Hawaiʻi.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <Shell>{children}</Shell>
        </Providers>
      </body>
    </html>
  );
}
