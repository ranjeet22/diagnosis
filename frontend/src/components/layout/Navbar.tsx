import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Menu, X } from 'lucide-react';
import combinationLogo from '../../assets/logos/combination logo.png';

export const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'Workflow', href: '#workflow' },
    { name: 'Architecture', href: '#architecture' },
    { name: 'Security', href: '#security' },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'py-3.5 bg-white/70 backdrop-blur-md border-b border-slate-200/50 shadow-sm'
          : 'py-5 bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center space-x-2 focus:outline-none">
          <img src={combinationLogo} alt="Diagnōsis" className="h-8 object-contain" />
        </a>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center space-x-8">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="text-sm font-medium text-textSecondary hover:text-primary transition-colors focus:outline-none"
            >
              {link.name}
            </a>
          ))}
        </div>

        {/* Actions */}
        <div className="hidden md:flex items-center space-x-4">
          <Link to="/app">
            <Button variant="primary" size="sm">
              Launch Console
            </Button>
          </Link>
        </div>

        {/* Mobile menu trigger */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-1 text-textPrimary focus:outline-none"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-white border-b border-slate-200 shadow-md p-6 flex flex-col space-y-4">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-semibold text-textPrimary hover:text-primary transition-colors focus:outline-none"
            >
              {link.name}
            </a>
          ))}
          <hr className="border-slate-100" />
          <div className="flex flex-col space-y-3 pt-2">
            <Link to="/app" className="w-full" onClick={() => setMobileMenuOpen(false)}>
              <Button variant="primary" size="md" className="w-full">
                Launch Console
              </Button>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
