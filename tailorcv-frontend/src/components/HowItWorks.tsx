import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Brain, Download, CheckCircle } from 'lucide-react';

const HowItWorks: React.FC = () => {
  const steps = [
    {
      icon: Upload,
      title: 'Upload Your Data',
      description: 'Share your LinkedIn profile URL or upload your existing resume PDF',
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: Brain,
      title: 'AI Processing',
      description: 'Our AI analyzes the job description and optimizes your resume content',
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: Download,
      title: 'Download PDF',
      description: 'Get your professionally formatted, ATS-friendly resume in PDF format',
      color: 'from-green-500 to-green-600'
    },
    {
      icon: CheckCircle,
      title: 'Apply with Confidence',
      description: 'Use your tailored resume to land more interviews and job offers',
      color: 'from-orange-500 to-orange-600'
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform your career prospects in just four simple steps
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="text-center">
                <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center mx-auto mb-6 shadow-lg`}>
                  <step.icon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-10 left-full w-full">
                  <div className="flex items-center justify-center">
                    <div className="w-16 h-0.5 bg-gradient-to-r from-gray-300 to-gray-400"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full ml-2"></div>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl p-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">
              Ready to transform your career?
            </h3>
            <p className="text-gray-600 mb-6">
              Join thousands of professionals who have already upgraded their resumes with TailorCV
            </p>
            <a
              href="/generate"
              className="inline-flex items-center bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              Get Started Now
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;