import Link from "next/link";
export default function NotFound() {
  return (
    <section className="panel empty-state">
      <h1>Page not found.</h1>
      <Link href="/">Return to the district overview</Link>
    </section>
  );
}
