import Image from "next/image";

export function InstitutionalFooter() {
  return (
    <div className="flex items-center justify-center gap-4 border-t border-sidebar-border px-4 py-3">
      <Image src="/branding/logo-uagrm.png" alt="Facultad de Ingeniería UAGRM" width={44} height={44} className="rounded-full opacity-90" />
      <Image src="/branding/logo-iicct.png" alt="IICCT Investigación FICCT" width={76} height={28} className="object-contain opacity-90" />
    </div>
  );
}
