import { Suspense } from "react";
import { Assistant } from "@/components/assistant/Assistant";

export const metadata = { title: "AI Assistant | DistrictIQ Hawaiʻi" };

export default function Page() {
  return <Suspense fallback={<p role="status">Preparing your assistant…</p>}><Assistant /></Suspense>;
}
