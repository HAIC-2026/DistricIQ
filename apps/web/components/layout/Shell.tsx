"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  LayoutDashboard,
  Database,
  GitCompareArrows,
  BookOpen,
  ArrowUpRight,
  MapPin,
  ExternalLink,
  MessageCircle,
} from "lucide-react";
const nav = [
  { href: "/", label: "District overview", Icon: LayoutDashboard },
  { href: "/assistant", label: "AI Assistant", Icon: MessageCircle },
  { href: "/data-explorer", label: "Data Explorer", Icon: Database },
  { href: "/comparisons", label: "Compare districts", Icon: GitCompareArrows },
  { href: "/methodology", label: "Sources & methodology", Icon: BookOpen },
];
export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Compass size={28} />
          </span>
          <span>
            District<span className="brand-iq">IQ</span>
            <small>HAWAIʻI</small>
          </span>
        </Link>
        <p className="nav-label">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {nav.map(({ href, label, Icon }) => (
            <Link
              key={href}
              href={href}
              className={path === href ? "nav-link active" : "nav-link"}
              aria-current={path === href ? "page" : undefined}
            >
              <Icon size={18} />
              {label}
              {path === href && <span className="active-dot" />}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="island-mark">
            <MapPin size={18} />
            <span>
              Built for Hawaiʻi.
              <br />
              <b>Grounded in evidence.</b>
            </span>
          </div>
          <a
            className="challenge-link"
            href="https://haic.hawaii.gov/wp-content/uploads/2026/10/HAIC_Use_Case_Know_Your_District_AI_Agent_2026.pdf"
            target="_blank"
            rel="noreferrer"
          >
            2026 Innovation Challenge <ArrowUpRight size={14} />
          </a>
          <span className="version">PHASE 2 · RESEARCH PREVIEW</span>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <span className="topbar-label">
            <span className="live-dot" /> HAWAIʻI LEGISLATIVE INTELLIGENCE
          </span>
          <a
            href="https://geoportal.hawaii.gov/"
            target="_blank"
            rel="noreferrer"
          >
            Hawaiʻi Geoportal <ExternalLink size={13} />
          </a>
        </header>
        <main id="main">{children}</main>
        <footer>
          DistrictIQ Hawaiʻi{" "}
          <span>Public data. Clear sources. Better understanding.</span>
          <span>House + Senate · 76 districts</span>
        </footer>
      </div>
    </div>
  );
}
