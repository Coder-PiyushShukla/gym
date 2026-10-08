"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Compass,
  Briefcase,
  CalendarDays,
  Users,
  Map,
  ShieldCheck,
  User,
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ChevronRight,
  ExternalLink,
  Target,
  ArrowRight,
  X,
  FileText,
  Filter,
  Trash2,
  ToggleRight,
  Plus,
  Clock,
  MapPin,
  Zap
} from "lucide-react";

const opportunityData = {
  id: "opp-01",
  title: "AI for Sustainable Cities Hackathon",
  organizer: "Global Climate Tech Initiative",
  matchScore: 94,
  trustScore: 92,
  eligibility: "Eligible",
  cost: "Free",
  format: "Online / Remote",
  deadline: "12 Nov 2026",
  sustainability: "SDG 11",
  teamSize: "3-5 Members",
  lastVerified: "18 mins ago",
  sources: 3,
  whyThis: [
    "Matches Python & ML skills",
    "Aligns with AI/ML Engineer goal",
    "Free registration",
    "Weekend event fits availability",
    "Remote participation",
    "High sustainability impact"
  ],
  whyNot: [
    "Team of 3-5 required (You are solo)",
    "Basic deployment knowledge recommended"
  ],
  skillGaps: ["Deployment", "Docker"],
};

const exploreData = [
  opportunityData,
  {
    id: "opp-02",
    title: "Open Source Contributor Summit",
    organizer: "OSF Foundation",
    matchScore: 88,
    trustScore: 98,
    eligibility: "Eligible",
    cost: "Free",
    format: "Hybrid",
    deadline: "20 Nov 2026",
    sustainability: "Education",
    teamSize: "Individual",
    lastVerified: "2 hours ago",
    sources: 4,
    whyThis: ["Excellent for web dev skills", "High networking value"],
    whyNot: ["Requires travel if attending in person"],
    skillGaps: [],
  },
  {
    id: "opp-03",
    title: "FinTech App Challenge",
    organizer: "National Bank",
    matchScore: 72,
    trustScore: 65,
    eligibility: "Unknown",
    cost: "₹500",
    format: "In-Person",
    deadline: "5 Dec 2026",
    sustainability: "None",
    teamSize: "2-4 Members",
    lastVerified: "5 days ago",
    sources: 1,
    whyThis: ["Good prize pool"],
    whyNot: ["Eligibility not stated clearly", "Low trust score", "Not remote"],
    skillGaps: ["Financial APIs"],
  }
];

export default function DishaPrototype() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [selectedView, setSelectedView] = useState("Main");
  const [drawerOpen, setDrawerOpen] = useState<"none" | "trust" | "roadmap" | "evidence">("none");

  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Explore", icon: Compass },
    { name: "My Opportunities", icon: Briefcase },
    { name: "Planner", icon: CalendarDays },
    { name: "Team Finder", icon: Users },
    { name: "Learning Journey", icon: Map },
    { name: "Trust & Evidence", icon: ShieldCheck },
    { name: "Profile", icon: User },
    { name: "Privacy Center", icon: ShieldAlert },
  ];

  const renderDashboard = () => (
    <motion.div
      key="dashboard"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-10"
    >
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: "Profile Match", value: "94%", color: "text-success", border: "border-success/30" },
          { label: "Open Opportunities", value: "18", color: "text-textMain", border: "border-panel" },
          { label: "Strong Matches", value: "7", color: "text-secondary", border: "border-secondary/30" },
          { label: "Beginner Friendly", value: "4", color: "text-textMain", border: "border-panel" },
          { label: "Sustainability", value: "6", color: "text-success", border: "border-panel" },
        ].map((stat, i) => (
          <div key={i} className={`bg-panel border ${stat.border} rounded-lg p-5 flex flex-col justify-center`}>
            <span className={`text-3xl font-light ${stat.color}`}>{stat.value}</span>
            <span className="text-xs text-textSub uppercase tracking-wider mt-2">{stat.label}</span>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-sm uppercase tracking-widest text-textSub mb-6 flex items-center gap-2">
          <Target size={16} className="text-primary" /> Top Opportunities For You
        </h2>
        <div className="grid grid-cols-2 gap-6">
          <div 
            onClick={() => setSelectedView("Detail")}
            className="bg-panel border border-secondary/20 rounded-lg p-6 hover:border-secondary/60 transition-colors cursor-pointer group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 bg-secondary/10 border-b border-l border-secondary/20 px-3 py-1 rounded-bl-lg text-secondary text-xs font-semibold flex items-center gap-1">
              <CheckCircle2 size={12} /> {opportunityData.matchScore}% MATCH
            </div>
            <h3 className="text-xl font-medium text-textMain mt-2">{opportunityData.title}</h3>
            <p className="text-sm text-textSub mt-1">{opportunityData.organizer}</p>
            
            <div className="flex flex-wrap gap-2 mt-6">
              <span className="px-2 py-1 bg-success/10 text-success border border-success/20 rounded text-xs">Eligible</span>
              <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub">Free</span>
              <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub">Remote</span>
              <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub">SDG 11</span>
            </div>

            <div className="mt-8 pt-6 border-t border-base flex justify-between items-center">
              <div className="flex items-center gap-2 text-sm text-secondary">
                <ShieldCheck size={16} /> Trust Score: {opportunityData.trustScore}/100
              </div>
              <span className="text-primary text-sm font-medium flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                Analyze <ArrowRight size={16} />
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderExplore = () => (
    <motion.div
      key="explore"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8"
    >
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-primary" size={20} />
          <input
            type="text"
            placeholder="Find free beginner-friendly AI hackathons I can attend remotely..."
            className="w-full bg-panel border border-primary/30 focus:border-primary outline-none rounded-lg py-4 pl-12 pr-4 text-textMain placeholder:text-textSub transition-colors"
          />
        </div>
        <button className="px-6 py-4 bg-panel border border-panel hover:border-textSub rounded-lg flex items-center gap-2 text-textMain transition-colors">
          <Filter size={18} /> Filters
        </button>
      </div>

      <div className="flex gap-2 flex-wrap mb-6">
        {["AI/ML", "Remote", "Free", "Beginner Friendly", "SDG: Climate"].map(tag => (
          <span key={tag} className="px-3 py-1.5 bg-panel border border-secondary/30 text-secondary rounded-full text-xs font-medium flex items-center gap-1">
            {tag} <X size={12} className="cursor-pointer" />
          </span>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {exploreData.map(opp => (
          <div 
            key={opp.id}
            onClick={() => setSelectedView("Detail")}
            className="bg-panel border border-panel hover:border-secondary/40 rounded-lg p-6 cursor-pointer group relative overflow-hidden flex flex-col justify-between"
          >
            <div>
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-medium text-textMain max-w-[80%]">{opp.title}</h3>
                <div className={`px-2 py-1 rounded text-xs font-semibold flex items-center gap-1 ${opp.matchScore > 80 ? 'bg-secondary/10 text-secondary border border-secondary/20' : 'bg-base text-textSub border border-panel'}`}>
                  {opp.matchScore}% MATCH
                </div>
              </div>
              <p className="text-sm text-textSub">{opp.organizer}</p>
              
              <div className="flex flex-wrap gap-2 mt-4">
                <span className={`px-2 py-1 border rounded text-xs ${opp.eligibility === 'Eligible' ? 'bg-success/10 text-success border-success/20' : 'bg-pending/10 text-pending border-pending/20'}`}>
                  {opp.eligibility}
                </span>
                <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub">{opp.cost}</span>
                <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub">{opp.format}</span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-base flex justify-between items-center">
              <div className={`flex items-center gap-2 text-sm ${opp.trustScore > 80 ? 'text-secondary' : 'text-pending'}`}>
                {opp.trustScore > 80 ? <ShieldCheck size={16} /> : <AlertTriangle size={16} />}
                Trust: {opp.trustScore}/100
              </div>
              <span className="text-textSub group-hover:text-primary text-sm font-medium flex items-center gap-1 transition-colors">
                View Details <ArrowRight size={16} />
              </span>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );

  const renderPlanner = () => (
    <motion.div
      key="planner"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8 max-w-4xl"
    >
      <div className="bg-risk/10 border border-risk/30 rounded-lg p-5 flex items-start gap-4">
        <AlertTriangle className="text-risk shrink-0" size={24} mt-1 />
        <div>
          <h3 className="text-risk font-medium mb-1">Schedule Conflict Detected</h3>
          <p className="text-sm text-textMain mb-3">Your saved "AI for Sustainable Cities Hackathon" (12-14 Nov) clashes with your "Mid-Semester Exam" (13 Nov).</p>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-risk text-white text-xs font-medium rounded hover:bg-risk/90">Prioritize Exam & Drop Hackathon</button>
            <button className="px-4 py-2 bg-base border border-panel text-textMain text-xs font-medium rounded hover:border-textSub">Find Alternative Hackathons</button>
          </div>
        </div>
      </div>

      <div className="relative border-l border-panel ml-4 space-y-8 pb-8">
        {[
          { date: "10 Nov", title: "Docker Workshop", type: "Learning", time: "10:00 AM" },
          { date: "12 Nov", title: "AI Hackathon Starts", type: "Opportunity", time: "09:00 AM", conflict: true },
          { date: "13 Nov", title: "Mid-Semester Exam", type: "Academic", time: "10:00 AM", conflict: true },
        ].map((event, i) => (
          <div key={i} className="relative pl-8">
            <div className={`absolute -left-3 top-1 w-6 h-6 rounded-full border-4 border-base flex items-center justify-center ${event.conflict ? 'bg-risk' : 'bg-secondary'}`}></div>
            <div className="text-sm text-textSub mb-1">{event.date} • {event.time}</div>
            <div className={`bg-panel border rounded-lg p-4 ${event.conflict ? 'border-risk/30 shadow-[0_0_15px_rgba(230,57,70,0.1)]' : 'border-panel'}`}>
              <div className="text-xs uppercase tracking-widest text-textSub mb-2">{event.type}</div>
              <div className="text-lg text-textMain">{event.title}</div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );

  const renderTeamFinder = () => (
    <motion.div
      key="team"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8"
    >
      <div className="bg-panel border border-panel rounded-lg p-6 flex justify-between items-center">
        <div>
          <h3 className="text-lg text-textMain mb-1">Your Target Role: Backend/ML Developer</h3>
          <p className="text-sm text-textSub">AI is finding teammates with complementary skills for the AI Hackathon.</p>
        </div>
        <button className="px-4 py-2 bg-base border border-panel rounded text-sm text-textMain hover:border-textSub">Update Profile</button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {[
          { name: "Sarah J.", role: "Frontend UI/UX", match: 96, skills: ["React", "Figma", "Tailwind"], missing: "Backend, ML", why: "Strong match because your ML skills perfectly complement her UI/UX expertise." },
          { name: "Rahul M.", role: "Data Analyst", match: 82, skills: ["Python", "Pandas", "Research"], missing: "Deployment", why: "Good alignment on Python, but both of you lack deployment experience." }
        ].map((user, i) => (
          <div key={i} className="bg-panel border border-panel rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded bg-base border border-panel flex items-center justify-center text-textSub text-lg font-bold">
                  {user.name.charAt(0)}
                </div>
                <div>
                  <h4 className="text-lg text-textMain">{user.name}</h4>
                  <div className="text-sm text-textSub">{user.role}</div>
                </div>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-bold ${user.match > 90 ? 'bg-success/10 text-success border border-success/20' : 'bg-base text-textSub border border-panel'}`}>
                {user.match}% COMPLEMENTARY
              </div>
            </div>
            
            <div className="bg-base rounded p-3 mb-4 border border-panel">
              <div className="text-xs text-textSub mb-1 flex items-center gap-1"><Zap size={12}/> AI Reasoning</div>
              <div className="text-sm text-textMain">{user.why}</div>
            </div>

            <div className="flex flex-wrap gap-2 mb-6">
              {user.skills.map(s => <span key={s} className="px-2 py-1 bg-panel border border-secondary/20 text-secondary rounded text-xs">{s}</span>)}
            </div>

            <div className="flex gap-3">
              <button className="flex-1 py-2 bg-primary hover:bg-primary/90 text-white text-sm rounded transition-colors">Invite to Team</button>
              <button className="px-4 py-2 bg-base border border-panel hover:border-textSub text-textMain text-sm rounded transition-colors">View Profile</button>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );

  const renderPrivacyCenter = () => (
    <motion.div
      key="privacy"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="max-w-3xl space-y-8"
    >
      <div className="bg-panel border border-panel rounded-lg p-8">
        <h3 className="text-xl text-textMain mb-2 flex items-center gap-2"><ShieldCheck className="text-success" /> Privacy-First Intelligence</h3>
        <p className="text-sm text-textSub mb-8">Disha processes your data locally where possible and maintains a human-in-the-loop philosophy. No automatic applications are ever submitted on your behalf.</p>
        
        <div className="space-y-6">
          <div className="flex items-center justify-between py-4 border-b border-base">
            <div>
              <div className="text-textMain font-medium">Automatic Eligibility Checking</div>
              <div className="text-xs text-textSub mt-1">Allow AI to verify your profile against opportunity requirements.</div>
            </div>
            <ToggleRight className="text-success" size={32} />
          </div>
          <div className="flex items-center justify-between py-4 border-b border-base">
            <div>
              <div className="text-textMain font-medium">Team Formation Visibility</div>
              <div className="text-xs text-textSub mt-1">Allow others to see your complementary skill match score.</div>
            </div>
            <ToggleRight className="text-success" size={32} />
          </div>
          <div className="flex items-center justify-between py-4 border-b border-base">
            <div>
              <div className="text-textMain font-medium">External Web Scraping</div>
              <div className="text-xs text-textSub mt-1">Allow Disha to cross-reference your public GitHub profile.</div>
            </div>
            <ToggleRight className="text-textSub rotate-180" size={32} />
          </div>
        </div>
      </div>

      <div className="bg-risk/5 border border-risk/20 rounded-lg p-8">
        <h3 className="text-xl text-risk mb-2 flex items-center gap-2"><Trash2 /> Danger Zone</h3>
        <p className="text-sm text-textSub mb-6">Permanently delete your intelligence profile, saved opportunities, and skill map.</p>
        <button className="px-6 py-3 bg-risk hover:bg-risk/90 text-white font-medium rounded text-sm transition-colors shadow-[0_0_15px_rgba(230,57,70,0.2)]">
          Delete My Data
        </button>
      </div>
    </motion.div>
  );

  const renderDetail = () => (
    <motion.div
      key="detail"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-5xl mx-auto space-y-8"
    >
      <button 
        onClick={() => setSelectedView("Main")}
        className="text-textSub hover:text-textMain text-sm flex items-center gap-2 mb-6"
      >
        <ChevronRight className="rotate-180" size={16} /> Back
      </button>

      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-4xl font-light tracking-tight text-textMain">{opportunityData.title}</h2>
          <p className="text-lg text-textSub mt-2 flex items-center gap-2">
            {opportunityData.organizer} 
            <span className="w-1 h-1 rounded-full bg-panel"></span>
            <span className="text-sm text-secondary flex items-center gap-1 border border-secondary/20 bg-secondary/5 px-2 py-0.5 rounded">
              <CheckCircle2 size={12} /> Verified
            </span>
          </p>
        </div>
        <div className="flex gap-4">
          <button className="px-6 py-2 border border-panel hover:border-textSub rounded bg-panel text-sm font-medium transition-colors">
            Save
          </button>
          <button className="px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded text-sm font-medium flex items-center gap-2 shadow-[0_0_20px_rgba(193,59,42,0.3)] transition-all">
            Add to Planner
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mt-8">
        <div 
          onClick={() => setDrawerOpen("trust")}
          className="col-span-1 bg-panel border border-secondary/30 rounded-lg p-5 cursor-pointer hover:bg-panel/80 transition-colors"
        >
          <span className="text-xs text-textSub uppercase tracking-wider block mb-2">Trust Score</span>
          <div className="text-3xl font-light text-secondary flex items-baseline gap-1">
            92<span className="text-sm text-textSub">/100</span>
          </div>
          <p className="text-xs text-textSub mt-2 flex items-center gap-1">
            <ExternalLink size={12} /> Click to view evidence
          </p>
        </div>
        <div className="col-span-1 bg-panel border border-success/30 rounded-lg p-5">
          <span className="text-xs text-textSub uppercase tracking-wider block mb-2">Eligibility</span>
          <div className="text-xl font-medium text-success flex items-center gap-2 mt-3">
            <CheckCircle2 size={20} /> Eligible
          </div>
        </div>
        <div className="col-span-2 bg-panel border border-panel rounded-lg p-5 flex flex-wrap gap-x-8 gap-y-4 items-center">
          <div>
            <span className="text-xs text-textSub uppercase block mb-1">Deadline</span>
            <span className="text-sm text-textMain">{opportunityData.deadline}</span>
          </div>
          <div>
            <span className="text-xs text-textSub uppercase block mb-1">Cost</span>
            <span className="text-sm text-textMain">{opportunityData.cost}</span>
          </div>
          <div>
            <span className="text-xs text-textSub uppercase block mb-1">Format</span>
            <span className="text-sm text-textMain">{opportunityData.format}</span>
          </div>
          <div>
            <span className="text-xs text-textSub uppercase block mb-1">Team Size</span>
            <span className="text-sm text-pending">{opportunityData.teamSize}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-8 mt-8">
        <div className="col-span-2 space-y-6">
          <div className="bg-panel border border-panel rounded-lg p-8">
            <h3 className="text-xs uppercase tracking-widest text-textSub mb-4 border-b border-base pb-4">Explainable AI Analysis</h3>
            
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h4 className="text-success text-sm font-medium mb-3 flex items-center gap-2">
                  <CheckCircle2 size={16} /> WHY THIS?
                </h4>
                <ul className="space-y-3">
                  {opportunityData.whyThis.map((reason, i) => (
                    <li key={i} className="text-sm text-textMain flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-success/50 mt-1.5 shrink-0"></div>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-pending text-sm font-medium mb-3 flex items-center gap-2">
                  <AlertTriangle size={16} /> WHY NOT?
                </h4>
                <ul className="space-y-3">
                  {opportunityData.whyNot.map((reason, i) => (
                    <li key={i} className="text-sm text-textMain flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-pending/50 mt-1.5 shrink-0"></div>
                      {reason}
                    </li>
                  ))}
                </ul>
                
                <div className="mt-8">
                  <h4 className="text-risk text-sm font-medium mb-3 flex items-center gap-2">
                    <XCircle size={16} /> SKILL GAP IDENTIFIED
                  </h4>
                  <div className="flex gap-2">
                    {opportunityData.skillGaps.map(gap => (
                      <span key={gap} className="px-2 py-1 bg-risk/10 border border-risk/20 text-risk text-xs rounded">{gap}</span>
                    ))}
                  </div>
                  <button 
                    onClick={() => setDrawerOpen("roadmap")}
                    className="mt-4 text-xs text-primary border border-primary/30 px-3 py-1.5 rounded hover:bg-primary/10 transition-colors"
                  >
                    Generate Readiness Roadmap
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 space-y-6">
          <div className="bg-panel border border-panel rounded-lg p-6">
            <h3 className="text-xs uppercase tracking-widest text-textSub mb-4">Opportunity Value</h3>
            <div className="space-y-4">
              {[
                { label: "Skill Growth", score: 92 },
                { label: "Career Relevance", score: 95 },
                { label: "Accessibility", score: 88 },
              ].map(metric => (
                <div key={metric.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-textSub">{metric.label}</span>
                    <span className="text-textMain">{metric.score}</span>
                  </div>
                  <div className="h-1 w-full bg-base rounded-full overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${metric.score}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-panel border border-panel rounded-lg p-6">
            <h3 className="text-xs uppercase tracking-widest text-textSub mb-4">Next Steps</h3>
            <button 
              onClick={() => { setActiveTab("Team Finder"); setSelectedView("Main"); }}
              className="w-full py-3 bg-base border border-textSub/20 hover:border-textSub/50 text-sm text-textMain rounded mb-3 flex items-center justify-center gap-2 transition-colors"
            >
              <Users size={16} /> Find Compatible Teammates
            </button>
            <button className="w-full py-3 bg-base border border-textSub/20 hover:border-textSub/50 text-sm text-textMain rounded flex items-center justify-center gap-2 transition-colors">
              <FileText size={16} /> Open Official Source
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderContent = () => {
    if (selectedView === "Detail") return renderDetail();
    
    switch (activeTab) {
      case "Dashboard": return renderDashboard();
      case "Explore": return renderExplore();
      case "Planner": return renderPlanner();
      case "Team Finder": return renderTeamFinder();
      case "Privacy Center": return renderPrivacyCenter();
      case "My Opportunities": 
      case "Learning Journey":
      case "Trust & Evidence":
      case "Profile":
        return (
          <div className="flex flex-col items-center justify-center h-[60vh] text-textSub">
            <ShieldCheck size={48} className="mb-4 text-panel" />
            <h2 className="text-xl text-textMain mb-2">{activeTab}</h2>
            <p>Module integrated into core flow. Navigate via Dashboard or Explore.</p>
          </div>
        );
      default: return renderDashboard();
    }
  };

  return (
    <div className="flex h-screen bg-base text-textMain font-sans overflow-hidden">
      <div className="noise-overlay"></div>

      <nav className="w-64 border-r border-panel bg-base flex flex-col z-10">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center font-bold text-white tracking-widest border border-secondary/30">
            D
          </div>
          <span className="text-xl font-semibold tracking-wide">DISHA</span>
        </div>

        <div className="flex-1 py-4 flex flex-col gap-1 px-4 overflow-y-auto">
          {navItems.map((item) => (
            <button
              key={item.name}
              onClick={() => {
                setActiveTab(item.name);
                setSelectedView("Main"); 
              }}
              className={`flex items-center gap-3 px-4 py-3 rounded-md transition-all duration-200 ${
                activeTab === item.name && selectedView !== "Detail"
                  ? "bg-panel text-primary border border-primary/20 shadow-[0_0_15px_rgba(193,59,42,0.1)]"
                  : "text-textSub hover:bg-panel/50 hover:text-textMain"
              }`}
            >
              <item.icon size={18} />
              <span className="text-sm font-medium">{item.name}</span>
            </button>
          ))}
        </div>

        <div className="p-6 border-t border-panel">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
            <span className="text-xs text-textSub uppercase tracking-wider">AI Intelligence Online</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded bg-panel border border-textSub/30 flex items-center justify-center text-secondary font-bold">
              AK
            </div>
            <div>
              <p className="text-sm font-medium">Alex Kumar</p>
              <p className="text-xs text-textSub">2nd Year Eng.</p>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 relative overflow-y-auto scroll-smooth z-10">
        <header className="sticky top-0 z-20 bg-base/80 backdrop-blur-md border-b border-panel px-10 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-light tracking-wide">
              {selectedView === "Detail" ? "Opportunity Intelligence" : 
               activeTab === "Dashboard" ? "Good evening, Alex" : 
               activeTab}
            </h1>
            <p className="text-sm text-textSub mt-1">
              {selectedView === "Detail" ? "Detailed analysis and verification" : 
               activeTab === "Dashboard" ? "Your personalized opportunity landscape" :
               `Managing your ${activeTab.toLowerCase()}`}
            </p>
          </div>
        </header>

        <div className="p-10">
          <AnimatePresence mode="wait">
            {renderContent()}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {drawerOpen === "trust" && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setDrawerOpen("none")}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
              />
              <motion.div
                initial={{ x: "100%" }}
                animate={{ x: 0 }}
                exit={{ x: "100%" }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className="fixed top-0 right-0 h-full w-[500px] bg-panel border-l border-secondary/30 z-50 p-8 shadow-2xl overflow-y-auto"
              >
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <h2 className="text-2xl font-light text-textMain flex items-center gap-3">
                      <ShieldCheck className="text-secondary" size={28} /> Verification Protocol
                    </h2>
                    <p className="text-sm text-textSub mt-2">Data grounded by 3 independent sources.</p>
                  </div>
                  <button onClick={() => setDrawerOpen("none")} className="text-textSub hover:text-textMain">
                    <X size={24} />
                  </button>
                </div>

                <div className="border border-secondary/20 bg-secondary/5 p-6 rounded-lg mb-8 relative">
                  <div className="absolute top-4 right-4 text-xs text-secondary border border-secondary/30 px-2 py-1 rounded font-mono">
                    LAST CHECK: 18M AGO
                  </div>
                  <div className="text-5xl font-light text-secondary mb-2">92</div>
                  <div className="text-xs uppercase tracking-widest text-textSub">Overall Trust Score</div>
                  
                  <div className="space-y-4 mt-6">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-textSub">Source Credibility</span>
                      <span className="text-textMain font-mono">95%</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-textSub">Field Completeness</span>
                      <span className="text-textMain font-mono">90%</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-textSub">Cross-source Agreement</span>
                      <span className="text-textMain font-mono">94%</span>
                    </div>
                  </div>
                </div>

                <h3 className="text-xs uppercase tracking-widest text-textSub mb-4 border-b border-base pb-2">Extracted Evidence</h3>
                
                <div className="space-y-4">
                  {[
                    { field: "Deadline", value: "12 Nov 2026", source: "Official Organizer Website", status: "Verified" },
                    { field: "Cost", value: "Free", source: "Devfolio API", status: "Verified" },
                    { field: "Format", value: "Online", source: "College Notice Board", status: "Verified" },
                  ].map((ev, i) => (
                    <div key={i} className="bg-base border border-panel rounded p-4">
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-textMain">{ev.field}</span>
                        <span className="text-xs text-success flex items-center gap-1"><CheckCircle2 size={12}/> {ev.status}</span>
                      </div>
                      <div className="text-lg text-textMain mb-3">{ev.value}</div>
                      <div className="text-xs text-textSub bg-panel inline-block px-2 py-1 rounded">
                        Source: {ev.source}
                      </div>
                    </div>
                  ))}
                  
                  <div className="bg-base border border-risk/30 rounded p-4 relative overflow-hidden">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-risk"></div>
                    <div className="flex justify-between mb-2 pl-2">
                      <span className="text-sm font-medium text-textMain">Stipend / Prize</span>
                      <span className="text-xs text-risk flex items-center gap-1"><AlertTriangle size={12}/> Not Stated</span>
                    </div>
                    <div className="text-sm text-textSub pl-2">No evidence found across 3 sources. AI has deliberately left this field blank to prevent hallucination.</div>
                  </div>
                </div>
              </motion.div>
            </>
          )}

          {drawerOpen === "roadmap" && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setDrawerOpen("none")}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
              />
              <motion.div
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                exit={{ y: "100%" }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className="fixed bottom-0 left-[10%] right-[10%] h-[80vh] bg-panel border-t border-x border-primary/30 z-50 p-10 rounded-t-2xl shadow-2xl overflow-y-auto"
              >
                <div className="flex justify-between items-start mb-10">
                  <div>
                    <h2 className="text-3xl font-light text-textMain flex items-center gap-3">

<Map className="text-primary" size={32} />
Readiness Roadmap
                    </h2>
                    <p className="text-sm text-textSub mt-2">Bridging the gap for: {opportunityData.title}</p>
                  </div>
                  <button onClick={() => setDrawerOpen("none")} className="text-textSub hover:text-textMain">
                    <X size={24} />
                  </button>
                </div>

                <div className="relative">
                  <div className="absolute left-6 top-10 bottom-10 w-0.5 bg-base border-l border-dashed border-textSub/30"></div>
                  
                  <div className="space-y-12">
                    <div className="relative flex gap-8 items-start">
                      <div className="w-12 h-12 rounded-full bg-success/20 border border-success flex items-center justify-center shrink-0 z-10">
                        <CheckCircle2 className="text-success" size={20} />
                      </div>
                      <div className="pt-2">
                        <h3 className="text-lg font-medium text-textMain">Current Profile</h3>
                        <p className="text-sm text-textSub mt-1">Python, Machine Learning basics confirmed.</p>
                      </div>
                    </div>

                    <div className="relative flex gap-8 items-start">
                      <div className="w-12 h-12 rounded-full bg-base border border-primary flex items-center justify-center shrink-0 z-10 shadow-[0_0_15px_rgba(193,59,42,0.4)]">
                        <span className="text-primary font-bold">1</span>
                      </div>
                      <div className="bg-base border border-panel rounded-lg p-6 flex-1">
                        <h3 className="text-lg font-medium text-textMain text-primary">Learn Basic Deployment (Gap)</h3>
                        <p className="text-sm text-textSub mt-2 mb-4">Estimated effort: 12 hours. Required for hackathon project submission.</p>
                        <div className="flex gap-3">
                          <button className="px-4 py-2 bg-panel border border-textSub/20 text-xs rounded hover:text-white transition-colors">Course: Intro to Docker</button>
                          <button className="px-4 py-2 bg-panel border border-textSub/20 text-xs rounded hover:text-white transition-colors">Tutorial: Vercel/Heroku</button>
                        </div>
                      </div>
                    </div>

                    <div className="relative flex gap-8 items-start">
                      <div className="w-12 h-12 rounded-full bg-base border border-textSub flex items-center justify-center shrink-0 z-10 text-textSub">
                        <span className="font-bold">2</span>
                      </div>
                      <div className="bg-base border border-panel/50 opacity-60 rounded-lg p-6 flex-1">
                        <h3 className="text-lg font-medium text-textMain">Complete Beginner ML Project</h3>
                        <p className="text-sm text-textSub mt-1">Apply deployment skills in a low-stakes environment.</p>
                      </div>
                    </div>

                    <div className="relative flex gap-8 items-start">
                      <div className="w-12 h-12 rounded-full bg-base border border-textSub flex items-center justify-center shrink-0 z-10 text-textSub">
                        <Target size={20} />
                      </div>
                      <div className="pt-2">
                        <h3 className="text-lg font-medium text-textMain">Target Opportunity</h3>
                        <p className="text-sm text-textSub mt-1">{opportunityData.title}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}