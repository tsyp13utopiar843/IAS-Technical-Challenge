import type { Metadata } from "next";
import Container from "@/components/container";
import { TopNav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Machines Status - IAS Dashboard",
  description: "Real-time monitoring of industrial machines status, performance metrics, and maintenance alerts",
};

export default function MachinesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <TopNav title="Machines Status" />
      <main>
        <Container>{children}</Container>
      </main>
    </>
  );
}
