"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from "recharts";
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
  const [activeTab, setActiveTab] = useState("Landing");
  const [selectedView, setSelectedView] = useState("Main");
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [drawerOpen, setDrawerOpen] = useState<"none" | "trust" | "roadmap" | "evidence">("none");
  const [authMode, setAuthMode] = useState("login");
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  
  const [userName, setUserName] = useState("Piyush Shukla");
  const [userInitials, setUserInitials] = useState("PS");
  
  const [selectedSkills, setSelectedSkills] = useState<string[]>(['Python', 'Java', 'Machine Learning']);
  const [prefFormat, setPrefFormat] = useState<string[]>(['Remote']);
  const [prefType, setPrefType] = useState<string[]>(['Hackathons']);
  const [prefAvailability, setPrefAvailability] = useState<string>('Weekends');
  const [prefFree, setPrefFree] = useState<boolean>(true);
  const [prefSustainable, setPrefSustainable] = useState<boolean>(true);

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

  const renderMyOpportunities = () => (
    <motion.div
      key="my-opps"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8"
    >
      <div className="flex gap-4 mb-6 border-b border-panel pb-4">
        <button className="text-primary font-medium border-b-2 border-primary pb-4 -mb-4">Saved (4)</button>
        <button className="text-textSub hover:text-textMain pb-4 -mb-4 transition-colors">Applied (2)</button>
        <button className="text-textSub hover:text-textMain pb-4 -mb-4 transition-colors">Completed (1)</button>
      </div>
      <div className="grid grid-cols-2 gap-6">
        {exploreData.map(opp => (
          <div key={opp.id + "-saved"} className="bg-panel border border-panel rounded-lg p-6 relative">
             <div className="flex justify-between items-start mb-2">
               <h3 className="text-lg font-medium text-textMain">{opp.title}</h3>
               <button className="text-textSub hover:text-risk transition-colors"><Trash2 size={16}/></button>
             </div>
             <p className="text-sm text-textSub mb-4">{opp.organizer}</p>
             <div className="flex items-center gap-4 text-sm text-textSub">
               <span className="flex items-center gap-1"><Clock size={14}/> Deadline: {opp.deadline}</span>
               <span className="flex items-center gap-1 text-primary"><Zap size={14}/> 1 pending task</span>
             </div>
             <div className="mt-4 flex gap-2">
               <button className="flex-1 bg-primary text-white text-sm py-2 rounded">Apply Now</button>
             </div>
          </div>
        ))}
      </div>
    </motion.div>
  );

  const renderLearningJourney = () => (
    <motion.div
      key="learning"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8 max-w-4xl"
    >
      <div className="bg-panel border border-panel rounded-lg p-6 flex justify-between items-center">
        <div>
           <h3 className="text-xl text-textMain">AI/ML Engineer Path</h3>
           <p className="text-sm text-textSub">Level: Intermediate • 3 Active Goals</p>
        </div>
        <div className="text-right">
           <div className="text-2xl font-light text-success">65%</div>
           <div className="text-xs text-textSub">Career Readiness</div>
        </div>
      </div>
      
      <div className="space-y-4">
        <h4 className="text-sm uppercase tracking-widest text-textSub">Current Focus Areas</h4>
        
        <div className="bg-panel border border-primary/30 rounded-lg p-5">
           <div className="flex justify-between items-center mb-2">
             <span className="text-primary font-medium flex items-center gap-2"><Target size={16}/> Model Deployment</span>
             <span className="text-sm text-textSub">2/3 Completed</span>
           </div>
           <div className="h-1.5 bg-base rounded-full overflow-hidden mb-4">
             <div className="h-full bg-primary w-2/3"></div>
           </div>
           <div className="space-y-2 pl-6 border-l-2 border-base">
             <div className="text-sm text-textSub flex items-center gap-2"><CheckCircle2 size={14} className="text-success"/> Learn Docker Basics</div>
             <div className="text-sm text-textSub flex items-center gap-2"><CheckCircle2 size={14} className="text-success"/> Build FastAPI Wrapper</div>
             <div className="text-sm text-textMain flex items-center gap-2"><Clock size={14} className="text-primary"/> Deploy on Render <button className="ml-auto text-xs bg-base px-2 py-1 rounded">Continue</button></div>
           </div>
        </div>
      </div>
    </motion.div>
  );

  const renderTrustEvidence = () => (
    <motion.div
      key="trust-main"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8 max-w-4xl"
    >
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-panel border border-panel rounded-lg p-6">
          <div className="text-3xl font-light text-secondary mb-1">94%</div>
          <div className="text-sm text-textSub">Average Platform Trust</div>
        </div>
        <div className="bg-panel border border-panel rounded-lg p-6">
          <div className="text-3xl font-light text-textMain mb-1">142</div>
          <div className="text-sm text-textSub">Sources Verified Today</div>
        </div>
        <div className="bg-panel border border-panel rounded-lg p-6">
          <div className="text-3xl font-light text-risk mb-1">12</div>
          <div className="text-sm text-textSub">Contradictions Flagged</div>
        </div>
      </div>
      
      <div className="bg-panel border border-panel rounded-lg p-6">
        <h3 className="text-lg font-medium text-textMain mb-4 flex items-center gap-2"><ShieldCheck className="text-secondary"/> Global Verification Log</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center py-3 border-b border-base">
            <div>
              <div className="text-sm text-textMain font-medium">Contradiction Detected: HackNY 2026</div>
              <div className="text-xs text-textSub mt-1">Source A (Oct 10) differs from Source B (Oct 12). Trust score penalized by 15.</div>
            </div>
            <span className="text-xs px-2 py-1 bg-risk/10 text-risk rounded">Flagged</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b border-base">
            <div>
              <div className="text-sm text-textMain font-medium">Canonical Merge: Web3 Summit</div>
              <div className="text-xs text-textSub mt-1">Deduplication engine merged 3 identical listings into one canonical source.</div>
            </div>
            <span className="text-xs px-2 py-1 bg-secondary/10 text-secondary rounded">Merged</span>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderProfile = () => {
    if (isEditingProfile) {
      return (
        <motion.div key="profile-edit" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-8 max-w-4xl">
          <div className="flex justify-between items-center mb-6 border-b border-panel pb-6">
             <div>
                <h2 className="text-2xl font-light text-textMain">Edit Profile & Priorities</h2>
                <p className="text-textSub mt-1">Update your AI matching preferences.</p>
             </div>
             <div className="flex gap-3">
               <button onClick={() => setIsEditingProfile(false)} className="px-4 py-2 border border-panel text-textSub hover:text-textMain rounded transition-colors text-sm">Cancel</button>
               <button onClick={() => setIsEditingProfile(false)} className="px-4 py-2 bg-primary text-white rounded transition-colors text-sm shadow-[0_0_15px_rgba(193,59,42,0.3)]">Save Changes</button>
             </div>
          </div>
          
          <div className="space-y-6">
             <div className="bg-panel border border-panel rounded-lg p-6">
                <h3 className="text-sm uppercase tracking-widest text-textSub mb-4">Interests & Skills</h3>
                <div className="flex flex-wrap gap-2 mb-4">
                  {['Python', 'Java', 'React', 'Machine Learning'].map(skill => (
                    <span key={skill} className="px-3 py-1.5 bg-success/10 border border-success/20 text-success rounded flex items-center gap-2 text-sm">{skill} <X size={14} className="cursor-pointer"/></span>
                  ))}
                  <button className="px-3 py-1.5 bg-base border border-panel text-textSub hover:text-textMain rounded text-sm flex items-center gap-1"><Plus size={14}/> Add Skill</button>
                </div>
             </div>

             <div className="bg-panel border border-panel rounded-lg p-6">
                <h3 className="text-sm uppercase tracking-widest text-textSub mb-4">Matching Priorities</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-textSub block mb-2">Preferred Format</label>
                    <select className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors">
                      <option>Remote / Online</option>
                      <option>In-Person</option>
                      <option>Hybrid</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-textSub block mb-2">Availability</label>
                    <select className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors">
                      <option>Weekends</option>
                      <option>Evenings</option>
                      <option>Flexible</option>
                    </select>
                  </div>
                </div>
             </div>
          </div>
        </motion.div>
      );
    }

    return (
    <motion.div
      key="profile-main"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-8 max-w-4xl"
    >
      <div className="flex items-end justify-between">
        <div className="flex items-center gap-6">
          <div className="w-24 h-24 rounded-xl bg-panel border-2 border-primary/30 flex items-center justify-center text-4xl text-secondary font-light">
            {userInitials}
          </div>
          <div>
            <h2 className="text-2xl font-medium text-textMain">{userName}</h2>
            <p className="text-textSub">2nd Year Computer Science Engineering</p>
            <div className="flex gap-2 mt-2">
              <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub flex items-center gap-1"><MapPin size={12}/> Bangalore, India</span>
              <span className="px-2 py-1 bg-base border border-panel rounded text-xs text-textSub flex items-center gap-1"><Zap size={12}/> AI/ML Focus</span>
            </div>
          </div>
        </div>
        <button onClick={() => setIsEditingProfile(true)} className="px-4 py-2 border border-primary/30 text-primary hover:bg-primary/10 rounded transition-colors text-sm">Edit Profile</button>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="bg-panel border border-panel rounded-lg p-6">
          <h3 className="text-sm uppercase tracking-widest text-textSub mb-4">Verified Skills</h3>
          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1.5 bg-success/10 border border-success/20 text-success rounded text-sm">Python (Advanced)</span>
            <span className="px-3 py-1.5 bg-success/10 border border-success/20 text-success rounded text-sm">Java (Intermediate)</span>
            <span className="px-3 py-1.5 bg-success/10 border border-success/20 text-success rounded text-sm">Basic ML</span>
            <span className="px-3 py-1.5 bg-base border border-panel text-textSub rounded text-sm">Web Dev</span>
          </div>
        </div>

        <div className="bg-panel border border-panel rounded-lg p-6">
          <h3 className="text-sm uppercase tracking-widest text-textSub mb-4">Discovery Preferences</h3>
          <ul className="space-y-3">
            <li className="flex justify-between text-sm"><span className="text-textSub">Budget</span><span className="text-textMain">Free / Low-cost</span></li>
            <li className="flex justify-between text-sm"><span className="text-textSub">Format</span><span className="text-textMain">Remote / Online</span></li>
            <li className="flex justify-between text-sm"><span className="text-textSub">Availability</span><span className="text-textMain">Weekends</span></li>
            <li className="flex justify-between text-sm"><span className="text-textSub">Sustainability</span><span className="text-textMain flex items-center gap-1 text-success"><CheckCircle2 size={14}/> Interested</span></li>
          </ul>
        </div>
      </div>
    </motion.div>
    );
  };

  const renderAuth = () => (
    <div className="h-screen w-full bg-base text-textMain relative overflow-hidden font-sans flex flex-col items-center justify-center">
      <div className="noise-overlay opacity-40"></div>
      
      <div className="absolute top-8 left-8 flex items-center gap-3 z-20 cursor-pointer" onClick={() => setActiveTab("Landing")}>
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center font-bold text-white tracking-widest border border-secondary/30">D</div>
        <span className="text-xl font-semibold tracking-wide">DISHA</span>
      </div>

      <div className="w-full max-w-md bg-panel border border-panel rounded-2xl shadow-2xl p-10 z-10 relative">
        <h2 className="text-3xl font-light text-textMain mb-2">{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
        <p className="text-textSub mb-8">{authMode === 'login' ? 'Enter your details to access your portal.' : 'Begin your intelligent discovery journey.'}</p>
        
        <div className="space-y-4 mb-6">
          {authMode === 'register' && (
             <input type="text" placeholder="Full Name" value={userName} onChange={(e) => {
               setUserName(e.target.value);
               const initials = e.target.value.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
               setUserInitials(initials || "U");
             }} className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" />
          )}
          <input type="email" placeholder="Email Address" className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" />
          <input type="password" placeholder="Password" className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" />
        </div>

        <button 
          onClick={() => setActiveTab(authMode === 'register' ? "Onboarding" : "Dashboard")}
          className="w-full py-3 bg-primary hover:bg-primary/90 text-white rounded font-medium flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(193,59,42,0.3)] mb-4"
        >
          {authMode === 'login' ? 'Sign In' : 'Sign Up'} <ArrowRight size={18} />
        </button>

        <p className="text-sm text-textSub text-center mt-6">
          {authMode === 'login' ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')} className="text-primary hover:underline font-medium">
            {authMode === 'login' ? 'Register' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );

  const renderLanding = () => (
    <div className="h-screen w-full bg-base text-textMain relative overflow-hidden font-sans">
      <div className="noise-overlay opacity-40"></div>
      
      <nav className="absolute top-0 w-full p-8 flex justify-between items-center z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center font-bold text-white tracking-widest border border-secondary/30">
            D
          </div>
          <span className="text-xl font-semibold tracking-wide">DISHA</span>
        </div>
        <div className="flex gap-6">
          <button className="text-sm font-medium text-textSub hover:text-textMain transition-colors">Platform</button>
          <button className="text-sm font-medium text-textSub hover:text-textMain transition-colors">Trust</button>
          <button className="text-sm font-medium text-textSub hover:text-textMain transition-colors">Equity</button>
        </div>
        <button onClick={() => { setActiveTab("Auth"); setAuthMode("register"); }} className="px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded text-sm font-medium shadow-[0_0_20px_rgba(193,59,42,0.3)] transition-all">
          Build Opportunity Profile
        </button>
      </nav>

      <div className="h-full flex items-center justify-center relative z-10 px-10">
        <div className="max-w-6xl w-full grid grid-cols-2 gap-20 items-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-secondary/10 border border-secondary/30 rounded-full text-secondary text-xs font-semibold mb-6">
              <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
              Agentic Intelligence Online
            </div>
            <h1 className="text-6xl font-light leading-tight tracking-tight mb-6 text-textMain">
              Discover opportunities <br/><span className="text-primary font-medium italic">built for your future.</span>
            </h1>
            <p className="text-lg text-textSub mb-10 max-w-lg leading-relaxed">
              Don't make students search for opportunities. Make opportunities intelligently discoverable. Disha verifies, maps, and guides your practical learning journey.
            </p>
            <div className="flex gap-4">
              <button onClick={() => { setActiveTab("Auth"); setAuthMode("register"); }} className="px-8 py-4 bg-primary hover:bg-primary/90 text-white rounded font-medium text-lg flex items-center gap-2 shadow-[0_0_25px_rgba(193,59,42,0.4)] transition-all group">
                Start Profiling <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button onClick={() => { setActiveTab("Auth"); setAuthMode("login"); }} className="px-8 py-4 bg-panel border border-panel hover:border-textSub text-textMain rounded font-medium text-lg transition-colors">
                Explore Demo
              </button>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="relative h-[600px] perspective-1000"
          >
            <motion.div 
              animate={{ rotateY: [0, 5, 0, -5, 0], rotateX: [0, 5, 0, -5, 0] }}
              transition={{ repeat: Infinity, duration: 10, ease: "easeInOut" }}
              className="absolute inset-0 bg-panel border border-secondary/30 rounded-2xl shadow-2xl p-6 transform-style-3d"
            >
              <div className="h-full flex flex-col">
                <div className="flex justify-between items-center mb-6 border-b border-base pb-4">
                  <div className="text-sm text-textSub uppercase tracking-widest flex items-center gap-2">
                    <ShieldCheck size={16} className="text-secondary" /> Neural Match Engine
                  </div>
                  <div className="text-xs bg-success/10 text-success border border-success/30 px-2 py-1 rounded">Syncing</div>
                </div>
                
                <div className="flex-1 relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                      { subject: 'ML Skills', A: 120, fullMark: 150 },
                      { subject: 'Eligibility', A: 98, fullMark: 150 },
                      { subject: 'Format Match', A: 86, fullMark: 150 },
                      { subject: 'Trust Score', A: 99, fullMark: 150 },
                      { subject: 'SDG Impact', A: 85, fullMark: 150 },
                      { subject: 'Cost', A: 65, fullMark: 150 },
                    ]}>
                      <PolarGrid stroke="#3a3229" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#9C9184', fontSize: 10 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                      <Radar name="Student Match" dataKey="A" stroke="#C13B2A" fill="#C13B2A" fillOpacity={0.4} />
                    </RadarChart>
                  </ResponsiveContainer>
                  
                  <motion.div 
                    animate={{ y: [0, -10, 0] }}
                    transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                    className="absolute top-10 -left-10 bg-panel border border-secondary/40 px-4 py-3 rounded-lg shadow-xl backdrop-blur-md flex items-center gap-3"
                  >
                    <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center text-secondary"><CheckCircle2 size={16} /></div>
                    <div>
                      <div className="text-xs text-textSub">Trust Verification</div>
                      <div className="text-sm font-medium text-textMain">Score: 92/100</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    animate={{ y: [0, 10, 0] }}
                    transition={{ repeat: Infinity, duration: 5, delay: 1, ease: "easeInOut" }}
                    className="absolute bottom-20 -right-8 bg-panel border border-primary/40 px-4 py-3 rounded-lg shadow-xl backdrop-blur-md flex items-center gap-3"
                  >
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary"><Target size={16} /></div>
                    <div>
                      <div className="text-xs text-textSub">Skill Gap Found</div>
                      <div className="text-sm font-medium text-textMain">Docker Deployment</div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );

  const renderOnboarding = () => (
    <div className="h-screen w-full bg-base text-textMain relative overflow-hidden font-sans flex flex-col items-center justify-center">
      <div className="noise-overlay opacity-40"></div>
      
      <div className="absolute top-8 left-8 flex items-center gap-3 z-20 cursor-pointer" onClick={() => setActiveTab("Landing")}>
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center font-bold text-white tracking-widest border border-secondary/30">D</div>
        <span className="text-xl font-semibold tracking-wide">DISHA</span>
      </div>

      <div className="w-full max-w-2xl bg-panel border border-panel rounded-2xl shadow-2xl p-10 z-10 relative">
        <div className="flex justify-between items-center mb-8">
          <div className="text-sm text-textSub uppercase tracking-widest">Step {onboardingStep} of 6</div>
          <div className="flex gap-1">
            {[1,2,3,4,5,6].map(step => (
              <div key={step} className={`h-1.5 w-8 rounded-full transition-colors ${step <= onboardingStep ? 'bg-primary' : 'bg-base border border-panel'}`}></div>
            ))}
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={onboardingStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="min-h-[250px]"
          >
            {onboardingStep === 1 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">01. Identity</h2>
                <p className="text-textSub mb-8">Let's start with the basics. Who are you?</p>
                <div className="space-y-4">
                  <input type="text" placeholder="Full Name" value={userName} onChange={(e) => {
                    setUserName(e.target.value);
                    const initials = e.target.value.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
                    setUserInitials(initials || "U");
                  }} className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" />
                  <input type="text" placeholder="Current Year / Education" className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" defaultValue="2nd Year B.Tech CSE" />
                </div>
              </div>
            )}
            {onboardingStep === 2 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">02. Skills Matrix</h2>
                <p className="text-textSub mb-8">What technologies have you worked with?</p>
                <div className="flex flex-wrap gap-3">
                  {['Python', 'Java', 'React', 'TypeScript', 'Machine Learning', 'Docker', 'AWS', 'Figma', 'C++'].map(skill => {
                    const isSelected = selectedSkills.includes(skill);
                    return (
                      <div 
                        key={skill} 
                        onClick={() => setSelectedSkills(prev => isSelected ? prev.filter(s => s !== skill) : [...prev, skill])}
                        className={`px-4 py-2 border rounded-lg cursor-pointer transition-colors ${isSelected ? 'bg-secondary/10 border-secondary text-secondary' : 'bg-base border-panel text-textSub hover:border-textMain'}`}>
                        {skill}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {onboardingStep === 3 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">03. Career Goals</h2>
                <p className="text-textSub mb-8">What role are you ultimately aiming for?</p>
                <input type="text" placeholder="e.g. AI/ML Engineer, Full Stack Developer..." className="w-full bg-base border border-panel rounded-lg px-4 py-3 text-textMain outline-none focus:border-primary transition-colors" defaultValue="AI/ML Engineer" />
              </div>
            )}
            {onboardingStep === 4 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">04. Preferences</h2>
                <p className="text-textSub mb-8">How do you prefer to learn and participate?</p>
                <div className="grid grid-cols-2 gap-4">
                  {['Remote', 'In-Person', 'Hybrid'].map(fmt => (
                    <div 
                      key={fmt}
                      onClick={() => setPrefFormat(prev => prev.includes(fmt) ? prev.filter(f => f !== fmt) : [...prev, fmt])}
                      className={`rounded-lg p-4 cursor-pointer flex items-center justify-between border transition-colors ${prefFormat.includes(fmt) ? 'bg-secondary/10 border-secondary text-secondary' : 'bg-base border-panel text-textSub hover:border-textMain'}`}>
                      {fmt} {prefFormat.includes(fmt) && <CheckCircle2 size={16}/>}
                    </div>
                  ))}
                  {['Hackathons', 'Bootcamps'].map(typ => (
                    <div 
                      key={typ}
                      onClick={() => setPrefType(prev => prev.includes(typ) ? prev.filter(t => t !== typ) : [...prev, typ])}
                      className={`rounded-lg p-4 cursor-pointer flex items-center justify-between border transition-colors ${prefType.includes(typ) ? 'bg-secondary/10 border-secondary text-secondary' : 'bg-base border-panel text-textSub hover:border-textMain'}`}>
                      {typ} {prefType.includes(typ) && <CheckCircle2 size={16}/>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {onboardingStep === 5 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">05. Availability</h2>
                <p className="text-textSub mb-8">When do you have time for external opportunities?</p>
                <div className="flex gap-3">
                  {['Weekends', 'Evenings', 'Summer'].map(time => (
                    <div 
                      key={time}
                      onClick={() => setPrefAvailability(time)}
                      className={`flex-1 rounded-lg p-4 text-center cursor-pointer border transition-colors ${prefAvailability === time ? 'bg-secondary/10 border-secondary text-secondary' : 'bg-base border-panel text-textSub hover:border-textMain'}`}>
                      {time}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {onboardingStep === 6 && (
              <div>
                <h2 className="text-3xl font-light text-textMain mb-2">06. Impact & Accessibility</h2>
                <p className="text-textSub mb-8">Help us apply an equity lens to your recommendations.</p>
                <div className="space-y-4">
                  <div onClick={() => setPrefFree(!prefFree)} className="flex justify-between items-center bg-base border border-panel rounded-lg p-4 cursor-pointer hover:border-textMain transition-colors">
                    <div>
                      <div className="text-textMain font-medium">Free / Stipend only</div>
                      <div className="text-xs text-textSub">Prioritize zero-cost opportunities</div>
                    </div>
                    <ToggleRight className={`transition-colors ${prefFree ? "text-success" : "text-textSub rotate-180"}`} size={28} />
                  </div>
                  <div onClick={() => setPrefSustainable(!prefSustainable)} className="flex justify-between items-center bg-base border border-panel rounded-lg p-4 cursor-pointer hover:border-textMain transition-colors">
                    <div>
                      <div className="text-textMain font-medium">Sustainability Focus</div>
                      <div className="text-xs text-textSub">Prioritize SDG-aligned impact projects</div>
                    </div>
                    <ToggleRight className={`transition-colors ${prefSustainable ? "text-success" : "text-textSub rotate-180"}`} size={28} />
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        <div className="flex justify-between mt-10 pt-6 border-t border-base">
          <button 
            onClick={() => setOnboardingStep(Math.max(1, onboardingStep - 1))}
            className={`px-6 py-2 text-textSub hover:text-textMain font-medium transition-colors ${onboardingStep === 1 ? 'invisible' : ''}`}
          >
            Back
          </button>
          <button 
            onClick={() => {
              if (onboardingStep < 6) setOnboardingStep(onboardingStep + 1);
              else setActiveTab("Dashboard");
            }}
            className="px-8 py-2 bg-primary hover:bg-primary/90 text-white rounded font-medium flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(193,59,42,0.3)]"
          >
            {onboardingStep === 6 ? "Generate Profile" : "Continue"} <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    if (selectedView === "Detail") return renderDetail();
    
    switch (activeTab) {
      case "Dashboard": return renderDashboard();
      case "Explore": return renderExplore();
      case "Planner": return renderPlanner();
      case "Team Finder": return renderTeamFinder();
      case "Privacy Center": return renderPrivacyCenter();
      case "My Opportunities": return renderMyOpportunities();
      case "Learning Journey": return renderLearningJourney();
      case "Trust & Evidence": return renderTrustEvidence();
      case "Profile": return renderProfile();
      default: return renderDashboard();
    }
  };

  if (activeTab === "Landing") return renderLanding();
  if (activeTab === "Auth") return renderAuth();
  if (activeTab === "Onboarding") return renderOnboarding();

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
              {userInitials}
            </div>
            <div>
              <p className="text-sm font-medium">{userName}</p>
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
               activeTab === "Dashboard" ? `Good evening, ${userName.split(' ')[0]}` : 
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