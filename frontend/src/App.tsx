import { useEffect } from 'react';
import Lenis from 'lenis';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { LandingPage } from './pages/LandingPage';
import { Footer } from './components/layout/Footer';
import { WorkspacePage } from './pages/WorkspacePage';

function LandingLayout() {
  useEffect(() => {
    // Initialize Lenis smooth scroll only on landing page
    const lenis = new Lenis({
      duration: 1.1,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow">
        <LandingPage />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingLayout />} />
        <Route path="/app" element={<WorkspacePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
