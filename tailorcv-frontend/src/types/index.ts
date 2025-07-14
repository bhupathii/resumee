export interface ResumeData {
  personalInfo: {
    name: string;
    email: string;
    phone: string;
    location: string;
    linkedin: string;
    github?: string;
    website?: string;
  };
  summary: string;
  skills: string[];
  experience: {
    title: string;
    company: string;
    location: string;
    startDate: string;
    endDate: string;
    current: boolean;
    description: string[];
  }[];
  education: {
    degree: string;
    institution: string;
    location: string;
    startDate: string;
    endDate: string;
    gpa?: string;
    relevantCourses?: string[];
  }[];
  projects: {
    name: string;
    description: string;
    technologies: string[];
    link?: string;
    github?: string;
  }[];
  certifications?: {
    name: string;
    issuer: string;
    date: string;
    link?: string;
  }[];
}

export interface JobDescription {
  title: string;
  company: string;
  requirements: string[];
  responsibilities: string[];
  skills: string[];
  experience: string;
}

export interface PaymentStatus {
  id: string;
  email?: string;
  screenshotUrl: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected';
}

export interface User {
  id: string;
  email?: string;
  ip: string;
  isPremium: boolean;
  lastGenerated?: string;
  generationCount: number;
}