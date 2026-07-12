import type { Route } from "./+types/home";
import { useState } from "react";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "BallotSense MVP" },
    {
      name: "description",
      content: "Citation-first voter research for the BallotSense archive demo.",
    },
  ];
}

const contests = [
  {
    id: "measure-d",
    label: "Measure D",
    detail: "Santa Clara Valley Open Space Authority special parcel tax",
  },
  {
    id: "bos-d1",
    label: "Board of Supervisors, District 1",
    detail: "Candidate race to add after the measure flow is proven",
  },
];

const lenses = [
  "Housing affordability",
  "Public safety",
  "Climate/environment",
  "Public education",
];

export default function Home() {
  const [selectedContest, setSelectedContest] = useState(contests[0].id);
  const [selectedLenses, setSelectedLenses] = useState<string[]>([
    "Climate/environment",
    "Public education",
  ]);

  function toggleLens(lens: string) {
    setSelectedLenses((current) =>
      current.includes(lens)
        ? current.filter((item) => item !== lens)
        : [...current, lens],
    );
  }

  function resetSession() {
    setSelectedContest(contests[0].id);
    setSelectedLenses([]);
  }

  return (
    <main className="min-h-screen bg-[linear-gradient(135deg,#f7f3eb_0%,#f7f3eb_52%,#dbe8df_52%,#dbe8df_100%)]">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-5 py-10 sm:px-8">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#52685c]">
            Archive demo contract
          </p>
          <h1 className="mt-4 font-serif text-5xl font-bold leading-[0.98] text-[#191815] sm:text-7xl">
            BallotSense shows its work before it speaks.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#3f3b35]">
            This Phase 1 shell keeps the demo choices in browser memory only.
            There is no account, voter profile, analytics identifier, ballot
            image, or durable preference storage.
          </p>
        </div>

        <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_0.85fr]">
          <section className="rounded-lg border border-[#d1c7b7] bg-[#fffbf2]/90 p-5 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-[#191815]">
                  Demo contest
                </h2>
                <p className="mt-1 text-sm text-[#665f54]">
                  Stored only in React state for this browser session.
                </p>
              </div>
              <button
                type="button"
                onClick={resetSession}
                className="rounded-md border border-[#9c8f7c] px-3 py-2 text-sm font-semibold text-[#453f36] transition hover:bg-[#efe6d7]"
              >
                Reset
              </button>
            </div>

            <div className="mt-5 grid gap-3">
              {contests.map((contest) => (
                <label
                  key={contest.id}
                  className="flex cursor-pointer items-start gap-3 rounded-md border border-[#ddd2c1] bg-white p-4 transition has-[:checked]:border-[#386859] has-[:checked]:bg-[#edf5ef]"
                >
                  <input
                    checked={selectedContest === contest.id}
                    className="mt-1 h-4 w-4 accent-[#386859]"
                    name="contest"
                    onChange={() => setSelectedContest(contest.id)}
                    type="radio"
                  />
                  <span>
                    <span className="block font-semibold text-[#191815]">
                      {contest.label}
                    </span>
                    <span className="mt-1 block text-sm leading-6 text-[#665f54]">
                      {contest.detail}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-[#c3d1c8] bg-[#f8fff9]/90 p-5 shadow-sm">
            <h2 className="text-xl font-semibold text-[#191815]">
              Issue lenses
            </h2>
            <p className="mt-1 text-sm text-[#53675b]">
              The MVP starts with fixed lenses, not free-text political values.
            </p>

            <div className="mt-5 grid gap-3">
              {lenses.map((lens) => (
                <label
                  key={lens}
                  className="flex cursor-pointer items-center gap-3 rounded-md border border-[#d2dfd6] bg-white px-4 py-3 transition has-[:checked]:border-[#386859] has-[:checked]:bg-[#e7f3ea]"
                >
                  <input
                    checked={selectedLenses.includes(lens)}
                    className="h-4 w-4 accent-[#386859]"
                    onChange={() => toggleLens(lens)}
                    type="checkbox"
                  />
                  <span className="font-medium text-[#25231f]">{lens}</span>
                </label>
              ))}
            </div>

            <div className="mt-5 rounded-md border border-[#d2dfd6] bg-[#f0f7f1] p-4 text-sm leading-6 text-[#405349]">
              Selected:{" "}
              <span className="font-semibold">
                {selectedLenses.length > 0
                  ? selectedLenses.join(", ")
                  : "No lenses selected"}
              </span>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
