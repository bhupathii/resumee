import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Zap, Shield, Users, CheckCircle } from 'lucide-react';
import GoogleAuth from '../components/GoogleAuth';

interface SignInPageProps {
  user: any;
  onLogin: (user: any) => void;
  onLogout: () => void;
}

const SignInPage: React.FC<SignInPageProps> = ({ user, onLogin, onLogout }) => {
  const features = [
    {
      icon: <FileText className="w-6 h-6" />,
      title: "AI-Powered Resume Generation",
      description: "Transform your LinkedIn profile or existing resume into a tailored masterpiece"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Job-Specific Optimization",
      description: "Match your resume perfectly to any job description with intelligent keyword optimization"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Premium Templates",
      description: "Access professional, ATS-friendly resume templates designed by experts"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Personal Dashboard",
      description: "Track your applications, manage multiple resumes, and monitor your job search progress"
    }
  ];

  const benefits = [
    "Generate unlimited tailored resumes",
    "Access to premium templates",
    "Personal dashboard and analytics",
    "Priority customer support",
    "Export in multiple formats"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
            Welcome to <span className="text-primary-600">TailorCV</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Create ATS-optimized resumes tailored to any job description. 
            Sign in with Google to access all features and start your journey to landing your dream job.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Sign In */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-xl p-8 lg:p-12"
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Sign In to Continue</h2>
              <p className="text-gray-600 mb-8">
                Access your personal dashboard and start creating professional resumes
              </p>
              
              <div className="flex justify-center">
                <GoogleAuth user={user} onLogin={onLogin} onLogout={onLogout} />
              </div>
            </div>

            <div className="border-t pt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">What you'll get:</h3>
              <ul className="space-y-3">
                {benefits.map((benefit, index) => (
                  <motion.li 
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className="flex items-center text-gray-700"
                  >
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                    {benefit}
                  </motion.li>
                ))}
              </ul>
            </div>
          </motion.div>

          {/* Right Column - Features */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Why Choose TailorCV?</h2>
            
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className="flex items-start space-x-4">
                  <div className="bg-primary-100 p-3 rounded-lg text-primary-600">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Bottom CTA */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-16"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Land Your Dream Job?
            </h3>
            <p className="text-gray-600 mb-6">
              Join thousands of professionals who have successfully optimized their resumes with TailorCV
            </p>
            <div className="flex justify-center">
              <GoogleAuth user={user} onLogin={onLogin} onLogout={onLogout} />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SignInPage;