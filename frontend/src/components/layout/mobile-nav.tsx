"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { InstitutionalFooter } from "@/components/layout/institutional-footer";
import { NAV_ITEMS } from "@/components/layout/nav-items";

export function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [pathname]);

  return (
    <>
      <header className="md:hidden fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-sidebar-border bg-sidebar text-sidebar-foreground px-4">
        <div className="flex items-center gap-2">
          <Image src="/branding/mascota-robot.jpeg" alt="Riesgo Académico" width={40} height={40} className="rounded-full" />
          <span className="font-semibold text-sm">Riesgo Académico</span>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setOpen(true)} aria-label="Abrir menú" className="text-sidebar-foreground hover:bg-sidebar-accent">
          <Menu className="h-5 w-5" />
        </Button>
      </header>

      <div
        className={cn(
          "md:hidden fixed inset-0 z-50 bg-black/50 transition-opacity",
          open ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setOpen(false)}
      />

      <aside
        className={cn(
          "md:hidden fixed inset-y-0 left-0 z-50 w-72 flex flex-col bg-sidebar text-sidebar-foreground transition-transform duration-300",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between gap-2 px-4 h-14 border-b border-sidebar-border">
          <div className="flex items-center gap-2">
            <Image src="/branding/mascota-robot.jpeg" alt="Riesgo Académico" width={40} height={40} className="rounded-full" />
            <span className="font-semibold text-sm">Riesgo Académico</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setOpen(false)} aria-label="Cerrar menú" className="text-sidebar-foreground hover:bg-sidebar-accent">
            <X className="h-5 w-5" />
          </Button>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-sidebar-border p-3">
          <ThemeToggle />
        </div>
        <InstitutionalFooter />
      </aside>
    </>
  );
}
