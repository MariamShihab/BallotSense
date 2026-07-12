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
    id: "scvosa-measure-d",
    label: "Measure D",
    detail: "Santa Clara Valley Open Space Authority special parcel tax",
  },
  {
    id: "scc-bos-district-1",
    label: "Board of Supervisors, District 1",
    detail: "Candidate race to add after the measure flow is proven",
  },
];

const lenses = [
  {
    id: "housing-affordability",
    label: "Housing affordability",
    detail: "Tax mechanics, exemptions, and housing-related evidence only.",
  },
  {
    id: "public-safety",
    label: "Public safety",
    detail: "Reviewed material about safety and wildfire risk.",
  },
  {
    id: "climate-environment",
    label: "Climate/environment",
    detail: "Open space, water, habitats, and environmental evidence.",
  },
  {
    id: "public-education",
    label: "Public education",
    detail: "Education evidence; BallotSense says when none is verified.",
  },
];

const sourceTypeLabels: Record<string, string> = {
  ballot_argument: "Ballot argument",
  campaign_material: "Campaign material",
  candidate_statement: "Candidate statement",
  elections_office_material: "Official elections material",
  official_measure_text: "Official measure text",
};

type Citation = { source_id: string; chunk_id: string; locator: string; public_source_url: string; source_type: string };
type Finding = { status: string; lens_id: string; summary: { text: string; citations: Citation[]; attribution?: string } | null; explanation: string | null };
type Brief = { election_id: string; contest_id: string; findings: Finding[]; disclaimer: string };
type CorrectionDraft = {
  citationKey: string;
  description: string;
  issueType: string;
  status: "idle" | "submitting" | "submitted" | "error";
  message: string | null;
};

export default function Home() {
  const [selectedContest, setSelectedContest] = useState(contests[0].id);
  const [selectedLenses, setSelectedLenses] = useState<string[]>(["climate-environment", "public-education"]);
  const [showResearch, setShowResearch] = useState(false);
  const [note, setNote] = useState("");
  const [brief, setBrief] = useState<Brief | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [correctionDraft, setCorrectionDraft] = useState<CorrectionDraft | null>(null);
  const activeContest = contests.find((contest) => contest.id === (brief?.contest_id ?? selectedContest)) ?? contests[0];

  function toggleLens(lens: string) {
    setSelectedLenses((current) =>
      current.includes(lens)
        ? current.filter((item) => item !== lens)
        : current.length < 3
          ? [...current, lens]
          : current,
    );
  }

  function resetSession() {
    setSelectedContest(contests[0].id);
    setSelectedLenses([]);
    setShowResearch(false);
    setNote("");
    setBrief(null);
    setError(null);
    setCorrectionDraft(null);
  }

  async function loadResearch() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/v1/briefs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ election_id: "ca-scc-2026-primary", contest_id: selectedContest, lens_ids: selectedLenses }),
      });
      if (!response.ok) throw new Error("The cited brief is unavailable right now.");
      setBrief((await response.json()) as Brief);
      setShowResearch(true);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "The cited brief is unavailable right now.");
    } finally { setLoading(false); }
  }

  async function submitCorrection(citation: Citation, lensId: string) {
    if (!brief || !correctionDraft) return;

    setCorrectionDraft({ ...correctionDraft, status: "submitting", message: null });
    try {
      const response = await fetch("/api/v1/corrections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          election_id: brief.election_id,
          contest_id: brief.contest_id,
          lens_id: lensId,
          source_id: citation.source_id,
          chunk_id: citation.chunk_id,
          issue_type: correctionDraft.issueType,
          description: correctionDraft.description,
        }),
      });
      if (!response.ok) throw new Error("Correction report could not be submitted.");
      const result = (await response.json()) as { message: string };
      setCorrectionDraft({
        ...correctionDraft,
        description: "",
        status: "submitted",
        message: result.message,
      });
    } catch (requestError) {
      setCorrectionDraft({
        ...correctionDraft,
        status: "error",
        message: requestError instanceof Error
          ? requestError.message
          : "Correction report could not be submitted.",
      });
    }
  }

  return (
    <main className="min-h-screen bg-[linear-gradient(135deg,#f7f3eb_0%,#f7f3eb_52%,#dbe8df_52%,#dbe8df_100%)]">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-5 py-10 sm:px-8">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#52685c]">
            Archived June 2026 demo · Santa Clara County
          </p>
          <h1 className="mt-4 font-serif text-5xl font-bold leading-[0.98] text-[#191815] sm:text-7xl">
            BallotSense shows its work before it speaks.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#3f3b35]">
            Explore reviewed election material through your selected lenses.
            BallotSense is research assistance, not a voting recommendation.
            There is no account, ballot image, or durable preference storage.
          </p>
          <ol className="mt-7 flex flex-wrap gap-3 text-sm font-semibold text-[#405349]">
            <li className="rounded-full bg-[#e7f3ea] px-3 py-1">1. Choose a contest</li>
            <li className="rounded-full bg-[#e7f3ea] px-3 py-1">2. Pick up to 3 lenses</li>
            <li className="rounded-full bg-[#e7f3ea] px-3 py-1">3. Inspect cited evidence</li>
          </ol>
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
                  key={lens.id}
                  className="flex cursor-pointer items-center gap-3 rounded-md border border-[#d2dfd6] bg-white px-4 py-3 transition has-[:checked]:border-[#386859] has-[:checked]:bg-[#e7f3ea]"
                >
                  <input
                    checked={selectedLenses.includes(lens.id)}
                    className="h-4 w-4 accent-[#386859]"
                    onChange={() => toggleLens(lens.id)}
                    type="checkbox"
                  />
                  <span>
                    <span className="block font-medium text-[#25231f]">{lens.label}</span>
                    <span className="mt-1 block text-sm leading-5 text-[#665f54]">
                      {lens.detail}
                    </span>
                  </span>
                </label>
              ))}
            </div>

            <div className="mt-5 rounded-md border border-[#d2dfd6] bg-[#f0f7f1] p-4 text-sm leading-6 text-[#405349]">
              Select up to three. Selected:{" "}
              <span className="font-semibold">
                {selectedLenses.length > 0
                  ? selectedLenses.map((id) => lenses.find((lens) => lens.id === id)?.label).join(", ")
                  : "No lenses selected"}
              </span>
            </div>
            <button
              type="button"
              disabled={selectedLenses.length === 0}
              onClick={loadResearch}
              className="mt-5 w-full rounded-md bg-[#245c4d] px-4 py-3 font-semibold text-white transition hover:bg-[#19483c] disabled:cursor-not-allowed disabled:bg-[#9aaca3]"
            >
              {loading ? "Loading cited research…" : "View cited research"}
            </button>
          </section>
        </div>

        {error && <p className="mt-6 max-w-3xl rounded-md bg-[#fff0ed] p-4 text-[#7a3324]">{error}</p>}
        {showResearch && brief && (
          <section className="mt-6 max-w-3xl rounded-lg border border-[#c3d1c8] bg-white/95 p-5 shadow-sm" aria-live="polite">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-[#52685c]">{activeContest.label} research brief</p>
            <h2 className="mt-2 text-2xl font-semibold text-[#191815]">What the reviewed material says</h2>
            <p className="mt-2 text-sm leading-6 text-[#665f54]">{brief.disclaimer}</p>
            <div className="mt-5 grid gap-4">
              {brief.findings.map((finding) => {
                const lens = lenses.find((item) => item.id === finding.lens_id);
                return (
                  <article key={finding.lens_id} className="rounded-md border border-[#ddd2c1] p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="font-semibold text-[#191815]">{lens?.label ?? finding.lens_id}</h3>
                      <span className="rounded-full bg-[#edf5ef] px-2 py-1 text-xs font-semibold text-[#405349]">{finding.status}</span>
                    </div>
                    <p className="mt-3 leading-7 text-[#3f3b35]">{finding.summary?.text ?? finding.explanation}</p>
                    {finding.summary?.citations.map((citation) => {
                      const citationKey = `${citation.source_id}:${citation.chunk_id}`;
                      const isReporting = correctionDraft?.citationKey === citationKey;
                      return (
                      <details key={citationKey} className="mt-4 rounded-md bg-[#f7f3eb] p-3">
                        <summary className="cursor-pointer font-semibold text-[#245c4d]">Inspect source proof</summary>
                        <p className="mt-2 text-sm text-[#665f54]">{sourceTypeLabels[citation.source_type] ?? citation.source_type} · {citation.locator}</p>
                        <a className="mt-2 inline-block text-sm font-semibold text-[#245c4d] underline" href={citation.public_source_url} target="_blank" rel="noreferrer">Open original source</a>
                        <div className="mt-3 border-t border-[#e1d7c9] pt-3">
                          <button
                            type="button"
                            onClick={() =>
                              setCorrectionDraft(
                                isReporting
                                  ? null
                                  : {
                                      citationKey,
                                      description: "",
                                      issueType: "misleading_summary",
                                      status: "idle",
                                      message: null,
                                    },
                              )
                            }
                            className="text-sm font-semibold text-[#245c4d] underline"
                          >
                            Report an issue with this source
                          </button>
                          {isReporting && (
                            <div className="mt-3 grid gap-3">
                              <p className="text-sm leading-6 text-[#665f54]">
                                Reports are tied to this citation. Do not include your
                                vote choice, address, email, phone number, or private note.
                              </p>
                              <label className="grid gap-1 text-sm font-semibold text-[#25231f]">
                                Issue type
                                <select
                                  value={correctionDraft.issueType}
                                  onChange={(event) =>
                                    setCorrectionDraft({
                                      ...correctionDraft,
                                      issueType: event.target.value,
                                      status: "idle",
                                      message: null,
                                    })
                                  }
                                  className="rounded-md border border-[#d1c7b7] bg-white p-2 font-normal"
                                >
                                  <option value="misleading_summary">Misleading summary</option>
                                  <option value="incorrect_source">Incorrect source</option>
                                  <option value="broken_source_link">Broken source link</option>
                                  <option value="privacy_concern">Privacy concern</option>
                                  <option value="other">Other</option>
                                </select>
                              </label>
                              <label className="grid gap-1 text-sm font-semibold text-[#25231f]">
                                What should a reviewer check?
                                <textarea
                                  value={correctionDraft.description}
                                  onChange={(event) =>
                                    setCorrectionDraft({
                                      ...correctionDraft,
                                      description: event.target.value,
                                      status: "idle",
                                      message: null,
                                    })
                                  }
                                  className="rounded-md border border-[#d1c7b7] bg-white p-2 font-normal"
                                  rows={3}
                                  maxLength={1000}
                                  placeholder="Describe the source or claim issue for review"
                                />
                              </label>
                              <button
                                type="button"
                                disabled={
                                  correctionDraft.status === "submitting"
                                  || correctionDraft.description.trim().length < 10
                                }
                                onClick={() => submitCorrection(citation, finding.lens_id)}
                                className="rounded-md bg-[#245c4d] px-3 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-[#9aaca3]"
                              >
                                {correctionDraft.status === "submitting"
                                  ? "Submitting report..."
                                  : "Submit correction report"}
                              </button>
                              {correctionDraft.message && (
                                <p className="text-sm font-semibold text-[#405349]">
                                  {correctionDraft.message}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </details>
                    );
                    })}
                  </article>
                );
              })}
            </div>
            <section className="mt-6 rounded-md border border-[#d2dfd6] bg-[#f8fff9] p-4" aria-labelledby="coverage-heading">
              <h3 id="coverage-heading" className="font-semibold text-[#191815]">Evidence coverage</h3>
              <p className="mt-1 text-sm leading-6 text-[#53675b]">Coverage describes what is in this reviewed archive corpus, not a position or endorsement.</p>
              <ul className="mt-3 grid gap-2 text-sm leading-6 text-[#3f3b35]">
                <li><span className="font-semibold">Official election material:</span> available for Measure D.</li>
                <li><span className="font-semibold">Filed ballot arguments and rebuttals:</span> available and clearly attributed.</li>
                <li><span className="font-semibold">Public education:</span> no verified Measure D evidence found.</li>
                <li><span className="font-semibold">District 1 candidate race:</span> not covered yet; no reviewed candidate corpus has been added.</li>
              </ul>
            </section>
            <label className="mt-6 block text-sm font-semibold text-[#25231f]" htmlFor="local-note">Private session note (never sent to BallotSense)</label>
            <textarea id="local-note" value={note} onChange={(event) => setNote(event.target.value)} className="mt-2 w-full rounded-md border border-[#d1c7b7] p-3" rows={3} placeholder="Write a note for this browser session" />
            <button type="button" onClick={() => setNote("")} className="mt-2 text-sm font-semibold text-[#245c4d] underline">Clear local note</button>
          </section>
        )}
      </section>
    </main>
  );
}
