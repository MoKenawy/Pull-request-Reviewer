"use client";

import dynamic from "next/dynamic";
import { Thread } from "@/components/thread.aui";

// Threads exist only in the browser, and the list's first client render differs from the server's loading
// skeleton, which React reports as a hydration mismatch. So the list is not server-rendered.
const ThreadList = dynamic(
  () => import("@/components/thread-list.aui").then((m) => m.ThreadList),
  { ssr: false },
);

export default function Home() {
  return (
    <div className="flex h-dvh">
      <div className="max-w-md">
        <ThreadList />
      </div>
      <div className="flex-grow">
        <Thread />
      </div>
    </div>
  );
}
