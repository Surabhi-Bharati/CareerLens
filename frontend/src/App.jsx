import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ATS_STOP_WORDS = new Set([
  "the", "and", "for", "with", "you", "your", "are", "our", "from", "that", "this", "will", "have", "has", "who", "what", "when", "where", "how", "all", "any", "can", "may", "must", "should", "their", "they", "them", "into", "about", "using", "use", "used", "work", "working", "role", "job", "team", "strong", "good", "ability", "experience", "knowledge", "skills", "skill", "years", "year", "required", "preferred", "responsibilities", "responsibility", "including", "such", "other", "etc", "will", "new", "build", "develop", "developer"
]);

function getJobKeywords(description) {
  const tokens = (description.toLowerCase().match(/[a-z][a-z0-9+#.]{1,}/g) || [])
    .map((token) => token.replace(/[.]$/, ""))
    .filter((token) => token.length >= 3 && !ATS_STOP_WORDS.has(token));
  return [...new Set(tokens)].slice(0, 60);
}

function calculateAtsReport(resume, jobDescription) {
  const checks = [];
  let contentPoints = 0;
  const addCheck = (label, points, passed, advice) => {
    checks.push({ label, points, passed, advice });
    if (passed) contentPoints += points;
  };
  const fullText = [resume.name, resume.email, resume.phone, resume.linkedin, resume.github, resume.summary, resume.education, resume.skills, resume.projects, resume.experience, resume.certifications].join(" ").trim();
  const wordCount = fullText ? fullText.split(/\s+/).filter(Boolean).length : 0;
  const hasImpact = /\b(\d+%?|increased|reduced|improved|automated|built|created|implemented|designed|led|delivered|optimized|developed|achieved)\b/i.test(`${resume.projects} ${resume.experience}`);

  addCheck("Name and professional contact", 8, Boolean(resume.name.trim() && /.+@.+\..+/.test(resume.email)), "Add your full name and a professional email address.");
  addCheck("Contact links", 4, Boolean(resume.phone.trim() || resume.linkedin.trim() || resume.github.trim()), "Add a phone number and/or a relevant LinkedIn or portfolio link.");
  addCheck("Professional summary", 8, resume.summary.trim().split(/\s+/).filter(Boolean).length >= 25, "Write a focused 2–4 line summary with your role, strongest skills, and career direction.");
  addCheck("Education details", 10, resume.education.trim().length >= 12, "Include degree, institution, expected graduation year, and relevant CGPA/marks if useful.");
  addCheck("Relevant skills", 10, resume.skills.split(",").map((x) => x.trim()).filter(Boolean).length >= 4, "List at least 4 relevant skills using clear, standard names separated by commas.");
  addCheck("Projects with details", 10, resume.projects.trim().split(/\s+/).filter(Boolean).length >= 20, "Describe 1–3 relevant projects, the technologies used, what you built, and your contribution.");
  addCheck("Experience or practical work", 6, resume.experience.trim().split(/\s+/).filter(Boolean).length >= 12, "If you have no job experience, describe internships, volunteering, freelance work, or meaningful practical experience. Do not invent experience.");
  addCheck("Certifications and achievements", 4, resume.certifications.trim().length >= 5, "Add relevant certifications, awards, or achievements if you have them.");
  addCheck("Action verbs or measurable impact", 5, hasImpact, "Use accurate action verbs and measurable results where available, e.g. reduced processing time by 20%. Never invent numbers.");
  addCheck("Enough searchable detail", 5, wordCount >= 100, "Add relevant detail so the resume communicates your work clearly; avoid filler and keep it concise.");

  const keywords = getJobKeywords(jobDescription);
  const searchableResume = [resume.summary, resume.education, resume.skills, resume.projects, resume.experience, resume.certifications].join(" ").toLowerCase();
  const matchedKeywords = keywords.filter((keyword) => searchableResume.includes(keyword));
  const missingKeywords = keywords.filter((keyword) => !searchableResume.includes(keyword));
  const contentPercent = Math.round((contentPoints / 70) * 100);
  const keywordPercent = keywords.length ? Math.round((matchedKeywords.length / keywords.length) * 100) : null;
  const score = keywords.length
    ? Math.round(contentPoints + (matchedKeywords.length / keywords.length) * 30)
    : contentPercent;

  const recommendations = checks.filter((check) => !check.passed).map((check) => check.advice);
  if (keywords.length && missingKeywords.length) {
    recommendations.unshift(`Review the job description for relevant missing terms: ${missingKeywords.slice(0, 8).join(", ")}. Add them only where they accurately describe your skills or experience.`);
  }
  if (!jobDescription.trim()) {
    recommendations.unshift("Paste a target job description to estimate keyword alignment for a specific role.");
  }

  return { score: Math.min(100, score), checks, keywords, matchedKeywords, missingKeywords, contentPercent, keywordPercent, wordCount, recommendations };
}

export default function App() {
  const [page, setPage] = useState("home");
  const [resume, setResume] = useState({
    name: "",
    email: "",
    phone: "",
    linkedin: "",
    github: "",
    summary: "",
    education: "",
    skills: "",
    projects: "",
    experience: "",
    certifications: "",
  });
  const [resumeBuilt, setResumeBuilt] = useState(false);
  const [atsJobDescription, setAtsJobDescription] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [careerInterests, setCareerInterests] = useState("");
  const [careerResult, setCareerResult] = useState(null);
  const [careerLoading, setCareerLoading] = useState(false);
  const [careerError, setCareerError] = useState("");

  function updateResume(event) {
    const { name, value } = event.target;
    setResume((previous) => ({ ...previous, [name]: value }));
  }

  async function analyzeJob(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      console.log("Resume data:", resume);
      console.log("Job description:", jobDescription);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_skills: resume.skills
            .split(",")
            .map((skill) => skill.trim())
            .filter(Boolean),
          resume_text: [
            resume.name,
            resume.email,
            resume.phone,
            resume.linkedin,
            resume.github,
            resume.summary,
            resume.education,
            resume.skills,
            resume.projects,
            resume.experience,
            resume.certifications,
          ]
            .filter(Boolean)
            .join("\n"),
          job_description: jobDescription,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail || data)
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        `${err.message}. Check that the backend is running at ${API_URL}.`
      );
    } finally {
      setLoading(false);
    }
  }

  function buildResume(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    setResumeBuilt(true);
  }

  async function getCareerRecommendations(event) {
    event.preventDefault();
    setCareerLoading(true);
    setCareerError("");
    setCareerResult(null);

    const skills = resume.skills
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean);

    if (!skills.length && !careerInterests.trim()) {
      setCareerError("Add technical skills in Resume Builder or enter career interests before requesting recommendations.");
      setCareerLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/career-recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: {
            full_name: resume.name.trim() || "CareerLens User",
            headline: "",
            email: resume.email,
            phone: resume.phone,
            location: "",
            summary: resume.summary,
            education: resume.education.trim() ? [{ details: resume.education }] : [],
            skills,
            projects: resume.projects.trim() ? [{ details: resume.projects }] : [],
            experience: resume.experience.trim() ? [{ details: resume.experience }] : [],
            certifications: resume.certifications
              .split(/[,\n]/)
              .map((item) => item.trim())
              .filter(Boolean),
            career_interests: careerInterests
              .split(",")
              .map((interest) => interest.trim())
              .filter(Boolean),
          },
          top_n: 3,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail || data)
        );
      }
      setCareerResult(data);
    } catch (err) {
      setCareerError(`${err.message}. Check that the backend is running at ${API_URL}.`);
    } finally {
      setCareerLoading(false);
    }
  }

  const atsReport = calculateAtsReport(resume, atsJobDescription);

  const inputClass =
    "w-full rounded-xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition focus:border-violet-400";

  const labelClass = "mb-2 block text-sm font-medium text-gray-300";

  return (
    <div className="min-h-screen bg-[#080b18] text-white">
      <style>{`
        @media print {
          @page { size: A4; margin: 12mm; }
          body * { visibility: hidden !important; }
          #resume-print-area, #resume-print-area * { visibility: visible !important; }
          #resume-print-area {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            color: #111827 !important;
            background: #ffffff !important;
          }
          #resume-print-area .resume-muted { color: #4b5563 !important; }
          .no-print { display: none !important; }
        }
      `}</style>
      <header className="sticky top-0 z-10 border-b border-white/10 bg-[#080b18]/90 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-5">
          <button
            onClick={() => {
              setPage("home");
              setError("");
              setResult(null);
            }}
            className="text-2xl font-bold tracking-tight"
          >
            Career<span className="text-violet-400">Lens</span>
          </button>

          <div className="flex flex-wrap items-center gap-2 sm:gap-5">
            <button
              onClick={() => {
                setPage("home");
                setError("");
                setResult(null);
              }}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
                page === "home"
                  ? "bg-violet-500 text-white"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              Home
            </button>
            <button
              onClick={() => {
                setPage("resume");
                setError("");
                setResult(null);
              }}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
                page === "resume"
                  ? "bg-violet-500 text-white"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              Resume Builder
            </button>
            <button
              onClick={() => {
                setPage("analyze");
                setError("");
                setResult(null);
              }}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
                page === "analyze"
                  ? "bg-violet-500 text-white"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              Analyze Job
            </button>
            <button
              onClick={() => {
                setPage("careers");
                setCareerError("");
                setCareerResult(null);
              }}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
                page === "careers"
                  ? "bg-violet-500 text-white"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              Career Recommendations
            </button>
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-12 sm:py-20">
        {page === "home" && (
          <section className="grid items-center gap-12 py-8 md:grid-cols-2 md:py-16">
            <div>
              <div className="mb-6 inline-flex rounded-full border border-violet-400/30 bg-violet-400/10 px-4 py-2 text-sm text-violet-300">
                Your career journey, made clearer
              </div>

              <h1 className="text-5xl font-bold leading-tight tracking-tight sm:text-7xl">
                Your skills.
                <br />
                Your future.
                <br />
                <span className="text-violet-400">Your direction.</span>
              </h1>

              <p className="mt-6 max-w-xl text-base leading-8 text-gray-400 sm:text-lg">
                Build your resume, explore job compatibility, discover missing
                skills, and take the next step toward your career goals.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <button
                  onClick={() => setPage("resume")}
                  className="rounded-xl bg-violet-500 px-6 py-3 font-semibold hover:bg-violet-400"
                >
                  Build My Resume →
                </button>
                <button
                  onClick={() => setPage("analyze")}
                  className="rounded-xl border border-white/15 px-6 py-3 font-semibold hover:bg-white/5"
                >
                  Analyze a Job
                </button>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-violet-500/15 to-blue-500/5 p-6 sm:p-9">
              <p className="text-sm text-violet-300">WELCOME TO CAREERLENS</p>
              <h2 className="mt-3 text-3xl font-semibold">
                Turn your potential into a plan.
              </h2>

              <div className="mt-8 space-y-4">
                {[
                  ["01", "Resume Builder", "Organize your academic and project details."],
                  ["02", "Job Compatibility", "Compare your skills with a job description."],
                  ["03", "Skill Gap Analysis", "Identify skills you may need to develop."],
                  ["04", "Career Guidance", "Use your profile to plan your next steps."],
                ].map(([number, title, description]) => (
                  <div
                    key={number}
                    className="flex gap-4 rounded-2xl border border-white/10 bg-black/20 p-4"
                  >
                    <span className="text-lg font-bold text-violet-400">
                      {number}
                    </span>
                    <div>
                      <h3 className="font-semibold">{title}</h3>
                      <p className="mt-1 text-sm text-gray-400">
                        {description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {page === "resume" && (
          <section className="mx-auto max-w-7xl">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-widest text-violet-400">
                Your professional profile
              </p>
              <h1 className="mt-3 text-4xl font-bold sm:text-5xl">Resume Builder</h1>
              <p className="mt-4 max-w-3xl leading-7 text-gray-400">
                Build an ATS-friendly, single-column resume with a live preview, job-keyword alignment, actionable improvement checks, and PDF export. The ATS score is a transparent heuristic estimate—not a score from a specific employer ATS.
              </p>
            </div>

            <div className="grid items-start gap-8 lg:grid-cols-2">
              <form onSubmit={buildResume} className="no-print space-y-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-8">
                <div>
                  <h2 className="text-xl font-bold">Your details</h2>
                  <p className="mt-1 text-sm text-gray-400">Required fields are marked with an asterisk.</p>
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-name">Full name *</label>
                  <input id="resume-name" className={inputClass} name="name" value={resume.name} onChange={updateResume} placeholder="e.g. Surabhi Bharati" required />
                </div>

                <div className="grid gap-5 sm:grid-cols-2">
                  <div>
                    <label className={labelClass} htmlFor="resume-email">Email address *</label>
                    <input id="resume-email" className={inputClass} type="email" name="email" value={resume.email} onChange={updateResume} placeholder="you@example.com" required />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="resume-phone">Phone number</label>
                    <input id="resume-phone" className={inputClass} type="tel" name="phone" value={resume.phone} onChange={updateResume} placeholder="+91 ..." />
                  </div>
                </div>

                <div className="grid gap-5 sm:grid-cols-2">
                  <div>
                    <label className={labelClass} htmlFor="resume-linkedin">LinkedIn URL</label>
                    <input id="resume-linkedin" className={inputClass} type="url" name="linkedin" value={resume.linkedin} onChange={updateResume} placeholder="https://linkedin.com/in/..." />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="resume-github">GitHub / Portfolio URL</label>
                    <input id="resume-github" className={inputClass} type="url" name="github" value={resume.github} onChange={updateResume} placeholder="https://github.com/..." />
                  </div>
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-summary">Professional summary</label>
                  <textarea id="resume-summary" className={inputClass} name="summary" value={resume.summary} onChange={updateResume} placeholder="A short 2–3 sentence introduction about your strengths and goals." rows={3} />
                </div>

                <div>
                  <label className={labelClass} htmlFor="ats-job-description">Target job description (optional, improves keyword analysis)</label>
                  <textarea id="ats-job-description" className={inputClass} value={atsJobDescription} onChange={(event) => setAtsJobDescription(event.target.value)} placeholder="Paste the job description you want to tailor this resume for..." rows={5} />
                  <p className="mt-2 text-xs text-gray-500">We compare terms in this description with your resume text. Include keywords only when they honestly match your experience.</p>
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-education">Education *</label>
                  <textarea id="resume-education" className={inputClass} name="education" value={resume.education} onChange={updateResume} placeholder={"B.Tech in Information Technology — College Name, 2028\nAdd relevant marks/CGPA if you want."} rows={3} required />
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-skills">Technical skills *</label>
                  <textarea id="resume-skills" className={inputClass} name="skills" value={resume.skills} onChange={updateResume} placeholder="Python, Java, SQL, React, Git" rows={3} required />
                  <p className="mt-2 text-xs text-gray-500">Separate individual skills with commas. These skills are also used by Job Compatibility.</p>
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-projects">Projects</label>
                  <textarea id="resume-projects" className={inputClass} name="projects" value={resume.projects} onChange={updateResume} placeholder={"CareerLens — Resume and job compatibility system\nBuilt with React, FastAPI, Python..."} rows={5} />
                  <p className="mt-2 text-xs text-gray-500">Include project name, what you built, technologies, and your contribution.</p>
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-experience">Experience / internships</label>
                  <textarea id="resume-experience" className={inputClass} name="experience" value={resume.experience} onChange={updateResume} placeholder="Role, organisation, dates, and key contributions." rows={4} />
                </div>

                <div>
                  <label className={labelClass} htmlFor="resume-certifications">Certifications and achievements</label>
                  <textarea id="resume-certifications" className={inputClass} name="certifications" value={resume.certifications} onChange={updateResume} placeholder="Certification name — issuing organisation, year" rows={3} />
                </div>

                <button type="submit" className="w-full rounded-xl bg-violet-500 px-5 py-3 font-semibold hover:bg-violet-400">
                  {resumeBuilt ? "Resume Preview Updated ✓" : "Update Resume Preview"}
                </button>
                {resumeBuilt && <p className="text-sm text-emerald-300" role="status">Your resume preview is ready. You can continue editing; the preview updates automatically.</p>}
              </form>

              <div className="min-w-0 space-y-5">
                <section className="no-print rounded-3xl border border-violet-400/20 bg-gradient-to-br from-violet-500/10 to-blue-500/5 p-5 sm:p-6">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-widest text-violet-300">Resume quality check</p>
                      <h2 className="mt-2 text-xl font-bold">ATS Readiness Estimate</h2>
                      <p className="mt-1 max-w-xl text-sm leading-6 text-gray-400">A rule-based estimate of completeness and keyword alignment. Different ATS platforms and recruiters may evaluate resumes differently.</p>
                    </div>
                    <div className="min-w-[112px] rounded-2xl border border-white/10 bg-[#0c1020] p-4 text-center">
                      <p className="text-3xl font-bold text-violet-300">{atsReport.score}</p>
                      <p className="text-xs text-gray-400">out of 100</p>
                    </div>
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-violet-400 transition-all" style={{ width: `${atsReport.score}%` }} /></div>
                  <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
                    <div className="rounded-xl bg-black/20 p-3"><p className="text-xs text-gray-400">Resume words</p><p className="mt-1 text-lg font-semibold">{atsReport.wordCount}</p></div>
                    <div className="rounded-xl bg-black/20 p-3"><p className="text-xs text-gray-400">Checks passed</p><p className="mt-1 text-lg font-semibold">{atsReport.checks.filter((check) => check.passed).length}/{atsReport.checks.length}</p></div>
                    <div className="rounded-xl bg-black/20 p-3"><p className="text-xs text-gray-400">Job keyword match</p><p className="mt-1 text-lg font-semibold">{atsReport.keywordPercent === null ? "Add job description" : `${atsReport.keywordPercent}%`}</p></div>
                  </div>
                  {atsReport.keywords.length > 0 && <div className="mt-5"><h3 className="text-sm font-semibold">Keyword alignment</h3><div className="mt-2 flex flex-wrap gap-2">{atsReport.matchedKeywords.slice(0, 16).map((keyword) => <span key={`matched-${keyword}`} className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-xs text-emerald-200">✓ {keyword}</span>)}{atsReport.missingKeywords.slice(0, 12).map((keyword) => <span key={`missing-${keyword}`} className="rounded-full border border-amber-400/20 bg-amber-400/10 px-2.5 py-1 text-xs text-amber-200">+ {keyword}</span>)}</div><p className="mt-2 text-xs text-gray-500">Green terms were found in your resume; amber terms were not. These are simple text matches, so review them for relevance.</p></div>}
                  <div className="mt-5"><h3 className="text-sm font-semibold">ATS checklist</h3><div className="mt-3 space-y-2">{atsReport.checks.map((check) => <div key={check.label} className="flex items-start gap-3 rounded-xl border border-white/5 bg-black/15 p-3"><span className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs ${check.passed ? "bg-emerald-400/15 text-emerald-300" : "bg-amber-400/15 text-amber-300"}`}>{check.passed ? "✓" : "!"}</span><div className="min-w-0"><p className="text-sm font-medium">{check.label} <span className="text-xs text-gray-500">· {check.points} pts</span></p>{!check.passed && <p className="mt-1 text-xs leading-5 text-gray-400">{check.advice}</p>}</div></div>)}</div></div>
                  {atsReport.recommendations.length > 0 && <div className="mt-5 rounded-2xl border border-violet-400/15 bg-violet-400/5 p-4"><h3 className="text-sm font-semibold text-violet-200">Recommended improvements</h3><ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-gray-300">{atsReport.recommendations.slice(0, 5).map((tip) => <li key={tip}>{tip}</li>)}</ul></div>}
                </section>

                <div className="no-print mb-3 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-bold">Live preview</h2>
                    <p className="mt-1 text-sm text-gray-400">This is how your resume will look when printed.</p>
                  </div>
                  <button type="button" onClick={() => window.print()} className="rounded-xl bg-violet-500 px-4 py-2.5 text-sm font-semibold hover:bg-violet-400">Print / Save as PDF</button>
                </div>

                <article id="resume-print-area" className="min-h-[700px] rounded-xl border border-gray-200 bg-white p-6 text-gray-900 shadow-2xl sm:p-10">
                  <header className="border-b-2 border-gray-800 pb-5">
                    <h2 className="break-words text-3xl font-bold tracking-tight">{resume.name.trim() || "Your Name"}</h2>
                    <div className="resume-muted mt-3 flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-600">
                      {resume.email && <span>{resume.email}</span>}
                      {resume.phone && <span>{resume.phone}</span>}
                      {resume.linkedin && <span className="break-all">{resume.linkedin}</span>}
                      {resume.github && <span className="break-all">{resume.github}</span>}
                      {!resume.email && !resume.phone && !resume.linkedin && !resume.github && <span>Email · Phone · LinkedIn · GitHub</span>}
                    </div>
                  </header>

                  {resume.summary.trim() && <section className="mt-5"><h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Professional Summary</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-6">{resume.summary}</p></section>}

                  <section className="mt-5">
                    <h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Education</h3>
                    <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{resume.education.trim() || "Add your degree, institution, and graduation year."}</p>
                  </section>

                  <section className="mt-5">
                    <h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Technical Skills</h3>
                    <p className="mt-2 text-sm leading-6">{resume.skills.trim() ? resume.skills.split(",").map((skill) => skill.trim()).filter(Boolean).join(" · ") : "Add your technical skills separated by commas."}</p>
                  </section>

                  {resume.projects.trim() && <section className="mt-5"><h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Projects</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-6">{resume.projects}</p></section>}
                  {resume.experience.trim() && <section className="mt-5"><h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Experience</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-6">{resume.experience}</p></section>}
                  {resume.certifications.trim() && <section className="mt-5"><h3 className="border-b border-gray-300 pb-1 text-sm font-bold uppercase tracking-widest">Certifications & Achievements</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-6">{resume.certifications}</p></section>}
                </article>
              </div>
            </div>
          </section>
        )}
        {page === "careers" && (
          <section className="mx-auto max-w-5xl">
            <p className="text-sm font-semibold uppercase tracking-widest text-violet-400">
              Find your direction
            </p>
            <h1 className="mt-3 text-4xl font-bold sm:text-5xl">Career Recommendations</h1>
            <p className="mt-4 max-w-3xl leading-7 text-gray-400">
              Explore career roles that may fit your skills and interests. Your technical skills are taken from the Resume Builder, so you do not need to enter them again.
            </p>

            <form onSubmit={getCareerRecommendations} className="mt-8 space-y-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-8">
              <div>
                <label className={labelClass} htmlFor="career-skills">Skills from your resume</label>
                <div id="career-skills" className="flex flex-wrap gap-2 rounded-xl border border-white/10 bg-black/20 p-4">
                  {resume.skills.split(",").map((skill) => skill.trim()).filter(Boolean).length ? (
                    resume.skills.split(",").map((skill) => skill.trim()).filter(Boolean).map((skill) => (
                      <span key={skill} className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-sm text-violet-200">{skill}</span>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">No skills added yet. Add skills in Resume Builder, or enter interests below.</p>
                  )}
                </div>
              </div>

              <div>
                <label className={labelClass} htmlFor="career-interests">Career interests (optional)</label>
                <input id="career-interests" className={inputClass} value={careerInterests} onChange={(event) => setCareerInterests(event.target.value)} placeholder="e.g. backend, web development, artificial intelligence" />
                <p className="mt-2 text-xs text-gray-500">Separate interests with commas. Examples: backend, frontend, data analysis, machine learning.</p>
              </div>

              <button type="submit" disabled={careerLoading} className="w-full rounded-xl bg-violet-500 px-5 py-3 font-semibold hover:bg-violet-400 disabled:opacity-50">
                {careerLoading ? "Finding careers..." : "Recommend Careers"}
              </button>
            </form>

            {careerError && <div role="alert" className="mt-6 rounded-2xl border border-red-400/30 bg-red-400/10 p-5"><h2 className="font-semibold text-red-300">Could not get recommendations</h2><p className="mt-2 break-words text-sm leading-6 text-red-200">{careerError}</p></div>}

            {careerResult && (
              <section className="mt-8 space-y-5">
                <div className="rounded-3xl border border-violet-400/20 bg-gradient-to-br from-violet-500/10 to-blue-500/5 p-6 sm:p-8">
                  <p className="text-sm font-semibold uppercase tracking-widest text-violet-300">Your career matches</p>
                  <h2 className="mt-2 text-2xl font-bold sm:text-3xl">Roles to explore, {careerResult.candidate_name || resume.name || "candidate"}</h2>
                  <p className="mt-3 text-sm leading-6 text-gray-400">{careerResult.message}</p>
                </div>

                {careerResult.recommendations?.length ? careerResult.recommendations.map((career) => (
                  <article key={career.role} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="max-w-2xl">
                        <h3 className="text-xl font-bold sm:text-2xl">{career.role}</h3>
                        <p className="mt-2 leading-7 text-gray-400">{career.description}</p>
                      </div>
                      <div className="min-w-[110px] rounded-2xl border border-violet-400/20 bg-violet-400/10 p-4 text-center">
                        <p className="text-2xl font-bold text-violet-300">{Number(career.match_score ?? 0).toFixed(1)}%</p>
                        <p className="text-xs text-gray-400">heuristic match</p>
                      </div>
                    </div>

                    {career.reasons?.length > 0 && <div className="mt-5"><h4 className="text-sm font-semibold">Why this role?</h4><ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-gray-300">{career.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></div>}

                    <div className="mt-5 grid gap-5 sm:grid-cols-2">
                      <div>
                        <h4 className="text-sm font-semibold text-emerald-300">Relevant skills you have</h4>
                        <div className="mt-2 flex flex-wrap gap-2">{career.matched_skills?.length ? career.matched_skills.map((skill) => <span key={skill} className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">✓ {skill}</span>) : <p className="text-sm text-gray-500">No matching skills identified yet.</p>}</div>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-amber-300">Skills to explore next</h4>
                        <div className="mt-2 flex flex-wrap gap-2">{career.suggested_skills_to_learn?.length ? career.suggested_skills_to_learn.map((skill) => <span key={skill} className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs text-amber-200">+ {skill}</span>) : <p className="text-sm text-gray-500">No additional skills suggested by this rule set.</p>}</div>
                      </div>
                    </div>
                  </article>
                )) : <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 text-gray-300">{careerResult.message || "No recommendations returned. Add more skills or career interests and try again."}</div>}

                <p className="px-2 text-xs leading-5 text-gray-500">These recommendations use a rule-based comparison of listed skills and interests. Scores are heuristic indicators, not predictions of hiring success.</p>
              </section>
            )}
          </section>
        )}

        {page === "analyze" && (
          <section className="mx-auto max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-widest text-violet-400">
              Find your next opportunity
            </p>
            <h1 className="mt-3 text-4xl font-bold sm:text-5xl">
              Job Compatibility
            </h1>
            <p className="mt-4 leading-7 text-gray-400">
              Add your skills and a job description to check your compatibility
              with the role.
            </p>

            <form
              onSubmit={analyzeJob}
              className="mt-8 space-y-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-8"
            >
              <div>
                <label className={labelClass}>Your skills</label>
                <textarea
                  className={inputClass}
                  name="skills"
                  value={resume.skills}
                  onChange={updateResume}
                  placeholder="Python, SQL, Git, Machine Learning"
                  rows={3}
                  required
                />
              </div>

              <div>
                <label className={labelClass}>Job description</label>
                <textarea
                  className={inputClass}
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                  placeholder="Paste the job responsibilities and required skills here..."
                  rows={7}
                  required
                />
              </div>

              <button
                disabled={loading}
                className="w-full rounded-xl bg-violet-500 px-5 py-3 font-semibold hover:bg-violet-400 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze Compatibility"}
              </button>
            </form>
          </section>
        )}

        {error && (
          <section className="mx-auto mt-8 max-w-3xl rounded-2xl border border-red-400/30 bg-red-400/10 p-5">
            <h2 className="font-semibold text-red-300">Something went wrong</h2>
            <p className="mt-2 break-words text-sm leading-6 text-red-200">
              {error}
            </p>
          </section>
        )}

        
{result && (
  <section className="mx-auto mt-8 max-w-4xl space-y-6">
    <div className="rounded-3xl border border-violet-400/20 bg-gradient-to-br from-violet-500/10 to-blue-500/5 p-6 sm:p-8">
      <p className="text-sm font-semibold uppercase tracking-widest text-violet-300">
        Analysis Complete
      </p>

      <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
        Your Job Compatibility Report
      </h2>

      <p className="mt-3 text-sm leading-6 text-gray-400">
        Here is how your current skills compare with the job description.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-[#0c1020] p-5">
          <p className="text-sm text-gray-400">Final Compatibility Score</p>
          <p className="mt-3 text-4xl font-bold text-violet-300">
            {Number(result.final_score ?? 0).toFixed(2)}%
          </p>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-violet-400 transition-all"
              style={{
                width: `${Math.min(100, Math.max(0, Number(result.final_score) || 0))}%`,
              }}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#0c1020] p-5">
          <p className="text-sm text-gray-400">Resume–Job Text Similarity</p>
          <p className="mt-3 text-4xl font-bold text-blue-300">
            {Number(result.text_similarity ?? 0).toFixed(2)}%
          </p>
          <p className="mt-3 text-xs text-gray-500">
            Measures textual similarity, not a guarantee of job suitability.
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#0c1020] p-5">
          <p className="text-sm text-gray-400">Matched Skills</p>
          <p className="mt-2 text-3xl font-bold text-emerald-300">
            {result.matched_skills?.length ?? 0}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            {result.matched_skills?.length ? (
              result.matched_skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200"
                >
                  ✓ {skill}
                </span>
              ))
            ) : (
              <p className="text-sm text-gray-500">No matched skills returned.</p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#0c1020] p-5">
          <p className="text-sm text-gray-400">Missing Skills</p>
          <p className="mt-2 text-3xl font-bold text-amber-300">
            {result.missing_skills?.length ?? 0}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            {result.missing_skills?.length ? (
              result.missing_skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-sm text-amber-200"
                >
                  + {skill}
                </span>
              ))
            ) : (
              <p className="text-sm text-gray-500">
                No missing skills identified by the current analysis.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>

    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8">
      <h3 className="text-xl font-bold">Skill Analysis Details</h3>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-sm text-gray-400">Total Job Skill Weight</p>
          <p className="mt-1 text-2xl font-semibold">
            {result.total_weight ?? "N/A"}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-400">Matched Skill Weight</p>
          <p className="mt-1 text-2xl font-semibold">
            {result.matched_weight ?? "N/A"}
          </p>
        </div>
      </div>

      {result.weighted_job_skills &&
        Object.keys(result.weighted_job_skills).length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold">Identified Job Skills and Weights</h4>
            <div className="mt-3 flex flex-wrap gap-2">
              {Object.entries(result.weighted_job_skills).map(
                ([skill, weight]) => (
                  <span
                    key={skill}
                    className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-300"
                  >
                    {skill} <span className="text-violet-300">· {weight}</span>
                  </span>
                )
              )}
            </div>
          </div>
        )}

      {result.unrecognized_skills?.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold text-amber-300">
            Skills Not Recognized
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {result.unrecognized_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-amber-400/10 px-3 py-1 text-sm text-amber-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {result.extracted_skills?.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold">Skills Extracted by the System</h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {result.extracted_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-sm text-violet-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>

    <p className="px-2 text-xs leading-5 text-gray-500">
      These results are generated by the current CareerLens analysis module.
      They are estimates based on the submitted information and should not be
      treated as a guarantee of employment or job readiness.
    </p>
  </section>
)}

      </main>

      <footer className="border-t border-white/10 px-5 py-8 text-center text-sm text-gray-500">
        CareerLens · Build skills. Find direction. Grow with confidence.
      </footer>
    </div>
  );
}
