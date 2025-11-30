import Link from "next/link";

export default function VisActor() {
  return (
    <Link
      href="#"
      target="_blank"
      className="relative my-2 flex flex-col items-center justify-center gap-y-2 px-4 py-4"
    >
      <div className="dot-matrix absolute left-0 top-0 -z-10 h-full w-full" />
    </Link>
  );
}
