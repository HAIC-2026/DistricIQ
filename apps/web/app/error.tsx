"use client";
import { Button } from "@/components/ui/button";
export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="panel empty-state" role="alert">
      <h1>The view could not load.</h1>
      <p>Please try loading the page again.</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
