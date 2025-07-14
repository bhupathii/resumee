import React from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Zap, 
  Shield, 
  Download, 
  RefreshCw, 
  Sparkles,
  Check,
  Star
} from 'lucide-react';

const Features: React.FC = () => {
  const features = [
    {
      icon: FileText,
      title: 'ATS-Optimized Templates',
      description: 'Professional LaTeX templates that pass through Applicant Tracking Systems',
      highlight: false
    },
    {
      icon: Zap,
      title: 'AI-Powered Optimization',
      description: 'Advanced AI tailors your resume to match specific job requirements',
      highlight: true
    },
    {
      icon: Shield,
      title: 'Privacy Protected',
      description: 'Your data is secure and never shared with third parties',
      highlight: false
    },
    {
      icon: Download,
      title: 'Instant PDF Generation',
      description: 'Download your professionally formatted resume in seconds',
      highlight: false
    },
    {
      icon: RefreshCw,
      title: 'Unlimited Revisions',
      description: 'Generate multiple versions for different job applications',
      highlight: true
    },
    {
      icon: Sparkles,
      title: 'Smart Content Enhancement',
      description: 'AI improves your content with industry-specific keywords',
      highlight: false
    }
  ];

  const premiumFeatures = [
    'Remove TailorCV watermark',
    'Access to premium templates',
    'Priority processing',
    'Advanced customization options',
    'Email delivery of resumes',
    'Unlimited generations'
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
            Powerful Features
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to create the perfect resume for any job application
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              viewport={{ once: true }}
              className={`relative p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg ${
                feature.highlight 
                  ? 'border-primary-200 bg-primary-50' 
                  : 'border-gray-200 bg-white hover:border-primary-200'
              }`}
            >
              {feature.highlight && (
                <div className="absolute -top-3 -right-3 bg-primary-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                  Popular
                </div>
              )}
              <div className="mb-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  feature.highlight ? 'bg-primary-600' : 'bg-gray-100'
                }`}>
                  <feature.icon className={`w-6 h-6 ${
                    feature.highlight ? 'text-white' : 'text-gray-600'
                  }`} />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 text-white"
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <div className="flex items-center mb-4">
                <Star className="w-6 h-6 text-yellow-400 mr-2" />
                <h3 className="text-2xl font-semibold">Upgrade to Premium</h3>
              </div>
              <p className="text-primary-100 mb-6">
                Get access to advanced features and create unlimited professional resumes
              </p>
              <a
                href="/payment"
                className="inline-flex items-center bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200"
              >
                Upgrade Now - ₹299
              </a>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Premium Features:</h4>
              <ul className="space-y-3">
                {premiumFeatures.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                    <span className="text-primary-100">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Features;