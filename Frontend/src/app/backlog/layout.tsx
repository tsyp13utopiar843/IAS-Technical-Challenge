import type { Metadata } from "next";
import Container from "@/components/container";
import { TopNav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Incident Backlog - IAS Dashboard",
  description: "Real-time incident tracking and backlog management for machine and worker safety events",
};

export default function BacklogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <TopNav title="Backlog" />
      <main>
        <Container>{children}</Container>
      </main>
    </>
  );
}
