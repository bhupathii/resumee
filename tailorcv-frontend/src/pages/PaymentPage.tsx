import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Upload, 
  CheckCircle, 
  AlertCircle,
  Star,
  Check,
  Loader2,
  Camera,
  CreditCard
} from 'lucide-react';

const PaymentPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const premiumFeatures = [
    'Remove TailorCV watermark',
    'Access to premium LaTeX templates',
    'Priority processing (faster generation)',
    'Advanced customization options',
    'Email delivery of resumes',
    'Unlimited resume generations',
    'Priority customer support',
    'Early access to new features'
  ];

  const handleScreenshotUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
        setScreenshot(file);
        setError(null);
      } else {
        setError('Please upload an image file under 5MB');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!screenshot) {
      setError('Please upload a payment screenshot');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('screenshot', screenshot);
      formData.append('timestamp', new Date().toISOString());

      const response = await fetch('/api/payment/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        setUploadSuccess(true);
      } else {
        setError(data.error || 'Failed to upload payment screenshot');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  if (uploadSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center"
        >
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Payment Submitted!</h2>
          <p className="text-gray-600 mb-6">
            Your payment screenshot has been submitted for verification. 
            You'll receive an email confirmation within 24 hours.
          </p>
          <div className="space-y-3">
            <Link
              to="/generate"
              className="block w-full bg-primary-600 hover:bg-primary-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
            >
              Generate Resume
            </Link>
            <Link
              to="/"
              className="block w-full text-primary-600 hover:text-primary-700 py-3 px-4 rounded-lg font-medium transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="mb-8">
            <Link 
              to="/" 
              className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </Link>
            <h1 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mb-2">
              Upgrade to Premium
            </h1>
            <p className="text-lg text-gray-600">
              Unlock advanced features and create unlimited professional resumes
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex items-center mb-6">
                <Star className="w-6 h-6 text-yellow-400 mr-2" />
                <h2 className="text-2xl font-bold text-gray-900">Premium Features</h2>
              </div>
              
              <div className="space-y-4 mb-8">
                {premiumFeatures.map((feature, index) => (
                  <div key={index} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>

              <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-6 rounded-lg">
                <div className="text-center">
                  <div className="text-3xl font-bold mb-2">₹299</div>
                  <div className="text-primary-100">One-time payment</div>
                  <div className="text-sm text-primary-200 mt-2">
                    Lifetime access to all premium features
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex items-center mb-6">
                <CreditCard className="w-6 h-6 text-primary-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-900">Complete Payment</h2>
              </div>

              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Step 1: Make UPI Payment
                </h3>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <div className="text-center">
                    <div className="w-32 h-32 bg-gray-200 rounded-lg mx-auto mb-4 flex items-center justify-center">
                      <span className="text-gray-500 text-sm">UPI QR Code</span>
                    </div>
                    <div className="space-y-2">
                      <p className="font-medium text-gray-900">Pay ₹299 using UPI</p>
                      <p className="text-sm text-gray-600">UPI ID: tailorcv@paytm</p>
                      <p className="text-sm text-gray-600">
                        Or scan the QR code with any UPI app
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Step 2: Upload Payment Screenshot
                  </h3>
                  
                  <div className="mb-4">
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                      required
                    />
                  </div>

                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                    <input
                      type="file"
                      id="screenshot-upload"
                      accept="image/*"
                      onChange={handleScreenshotUpload}
                      className="hidden"
                    />
                    <label
                      htmlFor="screenshot-upload"
                      className="cursor-pointer flex flex-col items-center"
                    >
                      {screenshot ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-8 h-8 mr-2" />
                          <span className="font-medium">{screenshot.name}</span>
                        </div>
                      ) : (
                        <>
                          <Camera className="w-12 h-12 text-gray-400 mb-2" />
                          <span className="text-gray-600 font-medium">
                            Upload Payment Screenshot
                          </span>
                          <span className="text-sm text-gray-500 mt-1">
                            PNG, JPG up to 5MB
                          </span>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                {error && (
                  <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-red-700">{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!screenshot || !email || isUploading}
                  className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white py-4 px-6 rounded-lg font-semibold text-lg transition-colors duration-200 flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    'Submit for Verification'
                  )}
                </button>
              </form>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Your payment will be verified manually within 24 hours. 
                  You'll receive an email confirmation once approved.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PaymentPage;