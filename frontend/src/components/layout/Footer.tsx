import React from 'react';
import { ShieldCheck } from 'lucide-react';
import combinationLogo from '../../assets/logos/combination logo.png';

export const Footer: React.FC = () => {
  const footerLinks = [
    {
      title: 'Platform',
      links: [
        { name: 'Core Engine', href: '#' },
        { name: 'Semantic Layers', href: '#' },
        { name: 'API Reference', href: '#' },
        { name: 'Security Policy', href: '#' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { name: 'Documentation', href: '#' },
        { name: 'Asset Catalog', href: '#' },
        { name: 'Interactive Walkthrough', href: '#' },
        { name: 'Platform Status', href: '#' },
      ],
    },
    {
      title: 'Security & Compliance',
      links: [
        { name: 'HIPAA Overview', href: '#' },
        { name: 'SOC2 Standards', href: '#' },
        { name: 'Data Processing (DPA)', href: '#' },
        { name: 'Terms & Privacy', href: '#' },
      ],
    },
  ];

  return (
    <footer className="bg-slate-50 border-t border-slate-200/80 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 mb-12">
          {/* Logo & Brand Column */}
          <div className="lg:col-span-2 space-y-4">
            <a href="#" className="flex items-center space-x-2 focus:outline-none">
              <img src={combinationLogo} alt="Diagnōsis" className="h-8 object-contain" />
            </a>
            <p className="text-sm text-textSecondary leading-relaxed max-w-sm">
              Enterprise clinical dataset profiler, semantic planning model,
              and secure AI insight engine running 100% deterministically.
            </p>
            <div className="flex space-x-4 pt-2">
              <a href="https://github.com/ranjeet22" target="_blank" rel="noopener noreferrer" className="text-textSecondary hover:text-primary transition-colors" aria-label="GitHub">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="https://www.linkedin.com/in/ranjeet-singh-a08961305/" target="_blank" rel="noopener noreferrer" className="text-textSecondary hover:text-primary transition-colors" aria-label="LinkedIn">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </div>

          {/* Links Columns */}
          {footerLinks.map((col, idx) => (
            <div key={idx} className="space-y-4">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-textPrimary">
                {col.title}
              </h4>
              <ul className="space-y-2.5">
                {col.links.map((link, lIdx) => (
                  <li key={lIdx}>
                    <a
                      href={link.href}
                      className="text-sm text-textSecondary hover:text-primary transition-colors focus:outline-none"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <hr className="border-slate-200/60 mb-8" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-textSecondary leading-relaxed">
            &copy; {new Date().getFullYear()} Diagnōsis. All rights reserved. Designed for healthcare platforms.
          </div>
          {/* HIPAA & SOC2 Compliant Badges */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 px-3 py-1 bg-white border border-slate-200 rounded-full text-[10px] font-semibold text-textSecondary">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>HIPAA COMPLIANT</span>
            </div>
            <div className="flex items-center space-x-1.5 px-3 py-1 bg-white border border-slate-200 rounded-full text-[10px] font-semibold text-textSecondary">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>SOC2 TYPE II</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
