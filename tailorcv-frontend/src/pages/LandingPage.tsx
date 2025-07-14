import React from 'react';
import Hero from '../components/Hero';
import HowItWorks from '../components/HowItWorks';
import Features from '../components/Features';
import Testimonials from '../components/Testimonials';
import Footer from '../components/Footer';

interface LandingPageProps {
  user?: any;
}

const LandingPage: React.FC<LandingPageProps> = ({ user }) => {
  return (
    <div className="min-h-screen">
      <Hero user={user} />
      <HowItWorks />
      <Features />
      <Testimonials />
      <Footer />
    </div>
  );
};

export default LandingPage;