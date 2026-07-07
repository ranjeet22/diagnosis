import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { LottiePlayer } from '../components/ui/LottiePlayer';
import { slideUp, staggerContainer, floatingAnimation } from '../animations/animations';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Accordion } from '../components/ui/Accordion';
import { Tabs } from '../components/ui/Tabs';
import { Timeline } from '../components/ui/Timeline';
import { AnimatedCounter } from '../components/ui/AnimatedCounter';
import {
  UploadCloud,
  Activity,
  Network,
  Database,
  Brain,
  ArrowRight,
  Check
} from 'lucide-react';

// 3D Assets (PNGs)
import medicalBrain from '../assets/3d/medical-ai-brain.png';
import floatingDashboard from '../assets/3d/floating-dashboard.png';
import uploadBox from '../assets/3d/upload-box.png';
import analyticsCube from '../assets/3d/analytics-cube.png';
import semanticNetwork from '../assets/3d/semantic-network.png';
import dataCloud from '../assets/3d/data-cloud.png';
import shieldSecurity from '../assets/3d/shield-security.png';
import chatAssistant from '../assets/3d/chat-assistant.png';

// Technical Illustrations (PNGs)
import deterministicArchitectureImg from '../assets/illustrations/deterministic-architecture.png';
import securityShieldImg from '../assets/illustrations/security-shield.png';

// Product Screenshots
import dashboardOverviewImg from '../assets/screenshots/dashboard-overview.png';
import chatInterfaceImg from '../assets/screenshots/chat-interface.png';

// Lottie JSON files
import datasetUploadingAnim from '../assets/lottie/dataset-uploading.json';
import analyticsThinkingAnim from '../assets/lottie/analytics-thinking.json';
import geminiSparkleAnim from '../assets/lottie/gemini-sparkle.json';

// Logos
import WordmarkLogo from '../assets/logos/Wordmark logo.png';
import BrandmarkLogo from '../assets/logos/Brandmark logo.png';

export const LandingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ingest');

  const tabsList = [
    { id: 'ingest', label: '1. Ingest Dataset', icon: <UploadCloud className="w-4 h-4" /> },
    { id: 'profile', label: '2. Profile Schema', icon: <Activity className="w-4 h-4" /> },
    { id: 'semantic', label: '3. Map Ontologies', icon: <Network className="w-4 h-4" /> },
    { id: 'execute', label: '4. Compute DAG', icon: <Database className="w-4 h-4" /> },
    { id: 'explain', label: '5. AI Explains', icon: <Brain className="w-4 h-4" /> }
  ];

  const workflowSteps = [
    {
      step_number: '01',
      title: 'Clinical Dataset Upload',
      description: 'Upload raw medical CSV records securely. The engine automatically discovers delimiters, performs encoding audits, and maps columns.'
    },
    {
      step_number: '02',
      title: 'Topological Schema Profile',
      description: 'Detects data types, categories, numerical boundaries, and evaluates completeness ratios to highlight missing values.'
    },
    {
      step_number: '03',
      title: 'Medical Ontology Mapping',
      description: 'Resolves column headers against standard medical synonyms to classify demographic markers, admissions, stays, and diagnostics.'
    },
    {
      step_number: '04',
      title: 'DAG Analytics Plan',
      description: 'Compiles calculations into a directed acyclic plan, executing topological aggregates locally and cached on Pandas/cuDF engines.'
    },
    {
      step_number: '05',
      title: 'Isolated AI Clinical Insights',
      description: 'Sends compressed aggregation metadata (never raw patient rows) to Gemini to generate narrative clinical summaries.'
    }
  ];



  const faqItems = [
    {
      title: 'How does Diagnōsis isolate Gemini from calculations?',
      content: 'Under our strict AI Isolation philosophy, LLMs never compute sums, averages, or visual recommendations. Raw clinical rows are never sent to Gemini. Instead, our deterministic local engine calculates results first, compiles abstract visual coordinates, and passes only aggregated, privacy-safe metadata contexts to Gemini to formulate clinical narratives.'
    },
    {
      title: 'Is the platform HIPAA compliant?',
      content: 'Yes. By design, Diagnōsis prevents patient-identifying clinical rows from leaving your local container or private network. For Enterprise teams, we sign Business Associate Agreements (BAAs) and offer single-tenant, isolated deployments on AWS, GCP, or Azure.'
    },
    {
      title: 'What dataset schemas are supported?',
      content: 'Diagnōsis can map any clinical dataset containing patient identifiers, demographic records (age, gender), timestamped timelines (admission dates, discharge times), and clinical targets (diagnoses, outcomes, hospital facilities). Our Semantic Mapper maps column names semantically to standardized medical entities.'
    }
  ];

  return (
    <div className="relative min-h-screen bg-slate-50 overflow-hidden select-none">
      
      {/* Background Gradient Mesh & Patterns */}
      <div className="absolute inset-0 bg-gradient-mesh pointer-events-none z-0" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-50/60 via-slate-50 to-slate-50 pointer-events-none z-0" />
      
      {/* Decorative Floating Blobs */}
      <div className="absolute top-[8%] left-[-10%] w-[500px] h-[500px] bg-blue-100/30 rounded-full filter blur-3xl pointer-events-none z-0 animate-pulse duration-10000" />
      <div className="absolute top-[40%] right-[-10%] w-[500px] h-[500px] bg-sky-100/30 rounded-full filter blur-3xl pointer-events-none z-0 animate-pulse duration-10000" />

      {/* ────────────────────────────────────────────────── */}
      {/* HERO SECTION */}
      {/* ────────────────────────────────────────────────── */}
      <section className="relative pt-24 pb-20 px-6 max-w-7xl mx-auto z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Text Column */}
          <motion.div
            className="lg:col-span-7 space-y-6 text-left"
            initial="hidden"
            animate="visible"
            variants={staggerContainer(0.12) as any}
          >
            <motion.h1
              variants={slideUp(0.7) as any}
              className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-textPrimary leading-[1.1]"
            >
              Healthcare Analytics with{' '}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500">
                Zero-Calculation LLMs
              </span>
            </motion.h1>

            <motion.p
              variants={slideUp(0.8) as any}
              className="text-base sm:text-lg text-textSecondary leading-relaxed max-w-xl"
            >
              Profile clinical datasets, map medical ontologies, and compose dashboard layouts.
              All calculations run locally and deterministically. Gemini is only used to explain the numbers.
            </motion.p>

            <motion.div
              variants={slideUp(0.9) as any}
              className="flex flex-col sm:flex-row items-center gap-4 pt-2"
            >
              <Link to="/app" className="w-full sm:w-auto">
                <Button variant="primary" size="lg" className="w-full shadow-md">
                  Launch Platform Console <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Read API Guidelines
              </Button>
            </motion.div>

            {/* Statistics counter grid */}
            <motion.div
              variants={slideUp(0.95) as any}
              className="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-6 border-t border-slate-200/50 max-w-xl text-left"
            >
              <div>
                <p className="text-2xl sm:text-3xl font-extrabold text-textPrimary">
                  <AnimatedCounter value={100} suffix="%" />
                </p>
                <p className="text-[10px] text-textSecondary uppercase tracking-wider font-semibold">
                  Deterministic
                </p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-extrabold text-textPrimary">
                  <AnimatedCounter value={0} prefix="" suffix="" />
                </p>
                <p className="text-[10px] text-textSecondary uppercase tracking-wider font-semibold">
                  Rows Shared
                </p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-extrabold text-textPrimary">
                  <AnimatedCounter value={45} suffix="ms" />
                </p>
                <p className="text-[10px] text-textSecondary uppercase tracking-wider font-semibold">
                  Avg Speed
                </p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-extrabold text-textPrimary">
                  <AnimatedCounter value={21} suffix="" />
                </p>
                <p className="text-[10px] text-textSecondary uppercase tracking-wider font-semibold">
                  Validators
                </p>
              </div>
            </motion.div>

            {/* Ingestion stats */}
            <motion.div
              variants={slideUp(1.0) as any}
              className="pt-6 border-t border-slate-200/60 flex items-center space-x-6 text-xs text-textSecondary"
            >
              <div className="flex items-center space-x-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                <span><strong>FastAPI Engine</strong>: Online</span>
              </div>
              <div>•</div>
              <div><strong>Topological Cache</strong>: Active</div>
            </motion.div>
          </motion.div>

          {/* Right Floating 3D Illustration Column */}
          <motion.div
            className="lg:col-span-5 flex justify-center relative select-none"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            {/* Soft decorative shadow gradient under image */}
            <div className="absolute -bottom-6 w-72 h-8 bg-blue-400/25 rounded-full filter blur-xl animate-pulse" />
            
            <motion.img
              src={medicalBrain}
              alt="Medical AI Brain Illustration"
              className="w-full max-w-[420px] object-contain drop-shadow-2xl z-10"
              variants={floatingAnimation(5.5) as any}
              animate="animate"
            />
          </motion.div>

        </div>

        {/* Brand logo grid watermark */}
        <div className="pt-20 border-b border-slate-200/50 pb-12 flex flex-col md:flex-row items-center justify-between gap-6 text-textSecondary">
          <span className="text-xs font-semibold uppercase tracking-wider">Engine Powering Standards At:</span>
          <div className="flex items-center space-x-12 opacity-60">
            <img src={WordmarkLogo} alt="Diagnōsis Wordmark" className="h-5 object-contain grayscale" />
            <img src={BrandmarkLogo} alt="Diagnōsis Brandmark" className="h-7 object-contain grayscale" />
          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* INTERACTIVE DASHBOARD SCREENSHOT PREVIEW */}
      {/* ────────────────────────────────────────────────── */}
      <section className="relative pb-24 px-6 max-w-7xl mx-auto z-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="relative mx-auto rounded-3xl border border-slate-200/60 bg-white/70 shadow-2xl p-2.5 max-w-5xl backdrop-blur-md group hover:shadow-blue-900/5 transition-all duration-500"
        >
          {/* Browser control bar */}
          <div className="flex items-center justify-between px-4 pb-3 border-b border-slate-100 mb-2.5">
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 rounded-full bg-rose-400/90" />
              <div className="w-3 h-3 rounded-full bg-amber-400/90" />
              <div className="w-3 h-3 rounded-full bg-emerald-400/90" />
            </div>
            <div className="px-10 py-1 rounded-md bg-slate-100/80 text-[10px] text-textSecondary font-mono select-none">
              console.diagnosis.healthcare/overview
            </div>
            <div className="w-12" />
          </div>
          
          <div className="relative overflow-hidden rounded-2xl border border-slate-100">
            {/* Image zoom reveal */}
            <img
              src={dashboardOverviewImg}
              alt="Diagnōsis Dashboard Preview Mockup"
              className="rounded-2xl w-full object-cover shadow-sm group-hover:scale-[1.01] transition-transform duration-700 ease-out"
              loading="lazy"
            />
          </div>
        </motion.div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* FEATURES / PILLARS GRID */}
      {/* ────────────────────────────────────────────────── */}
      <section id="features" className="relative py-28 px-6 max-w-7xl mx-auto z-10">
        <div className="text-center space-y-4 mb-20">
          <Badge variant="info">Platform Features</Badge>
          <h2 className="text-3xl md:text-5xl font-extrabold text-textPrimary tracking-tight">
            Decoupled Multi-Layer Foundation
          </h2>
          <p className="text-sm md:text-base text-textSecondary max-w-xl mx-auto leading-relaxed">
            Diagnōsis isolates dataset ingestion, calculations, and explanations into robust local pipelines.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          {/* Card 1: Ingest */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={uploadBox} alt="Dataset Ingest icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Dataset Ingestion Layer</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Audits raw clinical uploads for injections and anomalies, discover delimiters, encoding sets, and file sizes.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              Learn about audits <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

          {/* Card 2: Profile */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={analyticsCube} alt="Data profiler icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Schema Profiler</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Determines data types, categorical frequencies, boundaries, and missing patient records automatically.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              Explore profiles <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

          {/* Card 3: Semantic */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={semanticNetwork} alt="Semantic map icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Healthcare Semantic Model</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Maps arbitrary dataset columns to medical entities like diagnosis target, hospital stays, outcomes, and facilities.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              Inspect ontologies <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

          {/* Card 4: Execute */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={dataCloud} alt="DAG execution icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Topological DAG Planner</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Builds direct dependency execution routes to compute mathematical calculations locally on Pandas or GPU cuDF.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              See performance details <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

          {/* Card 5: Layout */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={floatingDashboard} alt="Dashboard layout icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Dashboard Composer</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Compiles mathematical outputs into coordinate configurations to render layouts on Apache ECharts.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              View config formats <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

          {/* Card 6: AI Insights */}
          <Card variant="floating" className="p-8 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50/50 border border-blue-100/50 flex items-center justify-center p-3 select-none">
                <img src={shieldSecurity} alt="AI Security icon" className="w-full h-full object-contain" />
              </div>
              <h3 className="text-xl font-bold text-textPrimary">Isolated AI Insight Engine</h3>
              <p className="text-sm text-textSecondary leading-relaxed">
                Formulates clinical insights from aggregated metrics, running with exponential retry and local fallbacks.
              </p>
            </div>
            <div className="pt-2 text-xs font-semibold text-primary flex items-center cursor-pointer hover:translate-x-1 transition-transform">
              Review isolation rules <ArrowRight className="ml-1 w-3.5 h-3.5" />
            </div>
          </Card>

        </div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* INTERACTIVE WORKFLOW PREVIEW WITH LOTTIE */}
      {/* ────────────────────────────────────────────────── */}
      <section id="workflow" className="relative py-28 bg-slate-100/60 border-y border-slate-200/50 px-6 z-10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
            
            {/* Left side text and tabs selection */}
            <div className="lg:col-span-5 space-y-6">
              <Badge variant="primary">Platform Workflow</Badge>
              <h2 className="text-3xl md:text-4xl font-extrabold text-textPrimary tracking-tight leading-tight">
                Secure clinical data flow from ingestion to explanation
              </h2>
              <p className="text-sm md:text-base text-textSecondary leading-relaxed">
                Diagnōsis splits dataset evaluation into five strict stages, ensuring patient confidentiality audits.
              </p>
              
              <Tabs
                tabs={tabsList}
                activeTab={activeTab}
                onChange={setActiveTab}
                className="hidden lg:flex flex-col space-y-2 bg-transparent p-0 w-full"
              />
            </div>

            {/* Right side animated dashboard panel wrapper */}
            <div className="lg:col-span-7">
              <Card variant="glass" className="p-8 border border-slate-200 bg-white/80 shadow-2xl min-h-[460px] flex flex-col justify-between backdrop-blur-md">
                
                <AnimatePresence mode="wait">
                  {activeTab === 'ingest' && (
                    <motion.div
                      key="ingest"
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6 text-left"
                    >
                      <div className="flex items-center space-x-3 text-primary">
                        <UploadCloud className="w-6 h-6 animate-bounce" />
                        <span className="font-bold text-base text-textPrimary">1. Secure Ingestion Pipeline</span>
                      </div>
                      
                      {/* Lottie Animation */}
                      <div className="w-full flex justify-center p-2 bg-blue-50/30 border border-blue-100/50 rounded-2xl h-44 items-center">
                        <LottiePlayer animationData={datasetUploadingAnim} className="h-full object-contain" loop={true} />
                      </div>

                      <p className="text-sm text-textSecondary leading-relaxed">
                        Drag and drop raw CSV clinical logs. The pipeline parses files locally, performs injection audits, and logs structural metadata.
                      </p>
                    </motion.div>
                  )}

                  {activeTab === 'profile' && (
                    <motion.div
                      key="profile"
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6 text-left"
                    >
                      <div className="flex items-center space-x-3 text-primary">
                        <Activity className="w-6 h-6 animate-pulse" />
                        <span className="font-bold text-base text-textPrimary">2. Schema Profiler Engine</span>
                      </div>
                      
                      {/* Lottie Animation */}
                      <div className="w-full flex justify-center p-2 bg-blue-50/30 border border-blue-100/50 rounded-2xl h-44 items-center">
                        <LottiePlayer animationData={analyticsThinkingAnim} className="h-full object-contain" loop={true} />
                      </div>

                      <p className="text-sm text-textSecondary leading-relaxed">
                        Detects target data formats, numerical bounds, categories, and completeness values, building standard schemas.
                      </p>
                    </motion.div>
                  )}

                  {activeTab === 'semantic' && (
                    <motion.div
                      key="semantic"
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6 text-left"
                    >
                      <div className="flex items-center space-x-3 text-primary">
                        <Network className="w-6 h-6" />
                        <span className="font-bold text-base text-textPrimary">3. Medical Synonyms Ontologies</span>
                      </div>
                      
                      {/* 3D Asset Illustration */}
                      <div className="w-full flex justify-center bg-blue-50/30 border border-blue-100/50 rounded-2xl h-44 items-center">
                        <img src={semanticNetwork} alt="Semantic ontology network" className="h-[90%] object-contain animate-pulse" />
                      </div>

                      <p className="text-sm text-textSecondary leading-relaxed">
                        Maps arbitrary columns dynamically to standardized keys (admission dates, zipcodes, facilities, diagnoses).
                      </p>
                    </motion.div>
                  )}

                  {activeTab === 'execute' && (
                    <motion.div
                      key="execute"
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6 text-left"
                    >
                      <div className="flex items-center space-x-3 text-primary">
                        <Database className="w-6 h-6" />
                        <span className="font-bold text-base text-textPrimary">4. Deterministic DAG Executor</span>
                      </div>
                      
                      {/* Lottie Animation */}
                      <div className="w-full flex justify-center p-2 bg-blue-50/30 border border-blue-100/50 rounded-2xl h-44 items-center">
                        <LottiePlayer animationData={analyticsThinkingAnim} className="h-full object-contain" loop={true} />
                      </div>

                      <p className="text-sm text-textSecondary leading-relaxed">
                        Computes math variables locally and caches outcomes inside JSON logs for zero-hallucination queries.
                      </p>
                    </motion.div>
                  )}

                  {activeTab === 'explain' && (
                    <motion.div
                      key="explain"
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6 text-left"
                    >
                      <div className="flex items-center space-x-3 text-primary">
                        <Brain className="w-6 h-6 animate-pulse" />
                        <span className="font-bold text-base text-textPrimary">5. Isolated AI Narratives</span>
                      </div>
                      
                      {/* Lottie Animation */}
                      <div className="w-full flex justify-center p-2 bg-blue-50/30 border border-blue-100/50 rounded-2xl h-44 items-center">
                        <LottiePlayer animationData={geminiSparkleAnim} className="h-full object-contain" loop={true} />
                      </div>

                      <p className="text-sm text-textSecondary leading-relaxed">
                        Synthesizes summaries using external AI models, utilizing only metadata structures to maintain privacy rules.
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>

                <div className="pt-4 flex items-center justify-between text-xs text-textSecondary border-t border-slate-100 mt-4">
                  <span>Diagnōsis Platform Status Console</span>
                  <button
                    onClick={() => {
                      const idx = tabsList.findIndex(t => t.id === activeTab);
                      const nextIdx = (idx + 1) % tabsList.length;
                      setActiveTab(tabsList[nextIdx].id);
                    }}
                    className="text-primary hover:underline font-semibold focus:outline-none flex items-center"
                  >
                    Next Stage <ArrowRight className="ml-1 w-3 h-3" />
                  </button>
                </div>
              </Card>
            </div>

          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* TECHNICAL ARCHITECTURE SECTION WITH ILLUSTRATION */}
      {/* ────────────────────────────────────────────────── */}
      <section id="architecture" className="relative py-28 px-6 max-w-7xl mx-auto z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Explanation Text & Timeline */}
          <div className="lg:col-span-5 space-y-6 text-left">
            <Badge variant="success">Platform Architecture</Badge>
            <h2 className="text-3xl md:text-4xl font-extrabold text-textPrimary tracking-tight leading-tight">
              Platform processing pipeline steps
            </h2>
            <Timeline steps={workflowSteps} />
          </div>

          {/* Technical Illustration Card */}
          <div className="lg:col-span-7">
            <Card variant="glass" className="p-4 border border-slate-200 bg-white/60 shadow-xl overflow-hidden backdrop-blur-md">
              <img
                src={deterministicArchitectureImg}
                alt="Deterministic Architecture pipeline illustration"
                className="w-full rounded-xl object-contain shadow-sm"
                loading="lazy"
              />
            </Card>
          </div>

        </div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* SECURITY / HIPAA COMPLIANCE */}
      {/* ────────────────────────────────────────────────── */}
      <section id="security" className="relative py-28 bg-blue-600 text-white z-10 rounded-t-[40px] md:rounded-t-[60px] overflow-hidden">
        {/* Abstract grids */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
            
            {/* Security Illustration */}
            <div className="lg:col-span-7 flex justify-center">
              <div className="relative w-full max-w-lg p-3.5 rounded-3xl bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl">
                <img
                  src={securityShieldImg}
                  alt="HIPAA Security Shield illustration diagram"
                  className="w-full rounded-2xl object-contain shadow-sm bg-blue-900/10"
                  loading="lazy"
                />
              </div>
            </div>

            {/* Explanation Column */}
            <div className="lg:col-span-5 space-y-6 text-left">
              <Badge variant="primary" className="bg-blue-500/50 text-white border-blue-400/30">
                Security & HIPAA Compliance
              </Badge>
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight">
                Designed for sensitive clinical records
              </h2>
              <p className="text-sm md:text-base text-blue-100 leading-relaxed">
                Raw clinical patient rows never leave your local workspace container. The analytics pipeline filters and sanitizes headers.
              </p>
              
              <ul className="space-y-4 pt-4">
                <li className="flex items-start space-x-3 text-sm">
                  <div className="w-5 h-5 rounded-full bg-blue-500/30 border border-blue-400/40 flex items-center justify-center text-white shrink-0 mt-0.5">
                    <Check className="w-3.5 h-3.5 text-emerald-300" />
                  </div>
                  <span><strong>Audit Sanitation Lock</strong>: Filters prompt injections, SQL keywords, and script exploits prior to execution.</span>
                </li>
                <li className="flex items-start space-x-3 text-sm">
                  <div className="w-5 h-5 rounded-full bg-blue-500/30 border border-blue-400/40 flex items-center justify-center text-white shrink-0 mt-0.5">
                    <Check className="w-3.5 h-3.5 text-emerald-300" />
                  </div>
                  <span><strong>No Database Transmission</strong>: Calculations use transient structures with zero external database logging.</span>
                </li>
                <li className="flex items-start space-x-3 text-sm">
                  <div className="w-5 h-5 rounded-full bg-blue-500/30 border border-blue-400/40 flex items-center justify-center text-white shrink-0 mt-0.5">
                    <Check className="w-3.5 h-3.5 text-emerald-300" />
                  </div>
                  <span><strong>GCP & AWS Sandboxes</strong>: Deploy isolated single-tenant nodes in VPC zones under sign BAAs.</span>
                </li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* CONVERSATIONAL ANALYTICS PREVIEW WITH MOCKUP */}
      {/* ────────────────────────────────────────────────── */}
      <section className="relative py-28 px-6 max-w-7xl mx-auto z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Chat description */}
          <div className="lg:col-span-5 space-y-6 text-left">
            <Badge variant="warning">Intent Router v1.0</Badge>
            <h2 className="text-3xl md:text-4xl font-extrabold text-textPrimary tracking-tight leading-tight">
              Conversational Analytics Intent Router
            </h2>
            <p className="text-sm md:text-base text-textSecondary leading-relaxed">
              Ask questions in natural language. Our intent router maps questions into structured filter and sort commands, keeping math calculations deterministic.
            </p>
            <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-soft space-y-4">
              <div className="flex items-center space-x-2.5">
                <img src={BrandmarkLogo} alt="Compact brand icon" className="w-5 h-5 object-contain" />
                <span className="text-xs font-bold text-textPrimary">LLM State Classifier Logs</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl font-mono text-[11px] text-textSecondary leading-relaxed">
                <p className="text-blue-600">User: "Show disease counts for females over 50"</p>
                <p className="text-emerald-600">Intent: FILTER_AND_GROUP</p>
                <p>&gt; Filters: gender == 'F', age &gt; 50</p>
                <p>&gt; Group_by: Diagnosis • Metric: Count</p>
              </div>
            </div>
          </div>

          {/* Chat Screenshot Mockup */}
          <div className="lg:col-span-7 relative">
            
            {/* Floating 3D Chat assistant icon decoration */}
            <motion.div
              className="absolute -top-10 -left-10 w-20 h-20 rounded-2xl bg-white border border-slate-200/80 shadow-2xl p-3 z-20 flex items-center justify-center select-none"
              variants={floatingAnimation(4.8) as any}
              animate="animate"
            >
              <img src={chatAssistant} alt="Chat assistant 3D icon decoration" className="w-full h-full object-contain" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="relative mx-auto rounded-3xl border border-slate-200 bg-white/70 shadow-2xl p-2 max-w-xl backdrop-blur-md z-10"
            >
              <div className="flex items-center space-x-1.5 px-3 pb-2 border-b border-slate-100 mb-2">
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
              </div>
              <img
                src={chatInterfaceImg}
                alt="Conversational Chat Interface Mockup"
                className="rounded-2xl w-full object-cover shadow-sm"
                loading="lazy"
              />
            </motion.div>
          </div>

        </div>
      </section>



      {/* ────────────────────────────────────────────────── */}
      {/* ACCORDION FAQ SECTION */}
      {/* ────────────────────────────────────────────────── */}
      <section className="relative py-20 px-6 max-w-4xl mx-auto z-10">
        <div className="text-center space-y-3 mb-12">
          <Badge variant="secondary">Common Questions</Badge>
          <h2 className="text-3xl font-extrabold text-textPrimary tracking-tight">
            Frequently Asked Questions
          </h2>
        </div>
        
        <Accordion items={faqItems} />
      </section>

      {/* ────────────────────────────────────────────────── */}
      {/* CALL TO ACTION SECTION */}
      {/* ────────────────────────────────────────────────── */}
      <section className="relative py-28 px-6 max-w-7xl mx-auto z-10">
        <Card variant="glass" className="relative p-10 md:p-20 border border-slate-200 bg-white/70 overflow-hidden shadow-2xl text-center space-y-6 backdrop-blur-md rounded-[32px]">
          <div className="absolute inset-0 bg-gradient-mesh opacity-40 pointer-events-none" />
          
          <h2 className="text-3xl md:text-5xl font-extrabold text-textPrimary tracking-tight">
            Unlock Smarter Healthcare Insights Today
          </h2>
          <p className="text-sm md:text-base text-textSecondary max-w-xl mx-auto leading-relaxed">
            Ingest your clinical datasets, compile schemas, and produce responsive configurations using a completely secure workflow.
          </p>
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10">
            <Link to="/app" className="w-full sm:w-auto">
              <Button variant="primary" size="lg" className="w-full shadow-md">
                Get Started Free <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Contact Sales
            </Button>
          </div>
        </Card>
      </section>

    </div>
  );
};
